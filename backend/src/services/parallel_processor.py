"""
Parallel processing utilities for RAG chatbot performance optimization.
Provides concurrent execution, task coordination, and resource management.
"""

import asyncio
import time
import logging
from typing import Any, Dict, List, Optional, Callable, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import functools

from ..utils.config import get_config
from ..utils.errors import CacheError, DatabaseError


logger = logging.getLogger(__name__)


@dataclass
class TaskResult:
    """Result of a parallel task execution."""

    task_id: str
    success: bool
    result: Any = None
    error: Optional[Exception] = None
    start_time: float = 0.0
    end_time: float = 0.0
    execution_time: float = 0.0

    def __post_init__(self):
        if self.end_time > 0 and self.start_time > 0:
            self.execution_time = self.end_time - self.start_time


@dataclass
class ParallelConfig:
    """Configuration for parallel processing."""

    max_workers: int = 10
    timeout: float = 30.0
    use_processes: bool = False  # False for I/O bound, True for CPU bound
    chunk_size: int = 5
    retry_attempts: int = 3
    retry_delay: float = 1.0
    progress_callback: Optional[Callable] = None


class ParallelProcessor:
    """Manages parallel execution of tasks with coordination and monitoring."""

    def __init__(self, config: Optional[ParallelConfig] = None):
        self.config = config or ParallelConfig()
        self.executor = None
        self.semaphore = None
        self.running_tasks = {}
        self.completed_tasks = []
        self.stats = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "total_execution_time": 0.0,
            "avg_execution_time": 0.0,
            "concurrent_tasks": 0,
            "max_concurrent": 0,
        }

    async def initialize(self):
        """Initialize parallel processing resources."""
        if self.config.use_processes:
            # Use process pool for CPU-bound tasks
            self.executor = ProcessPoolExecutor(max_workers=self.config.max_workers)
            logger.info(
                f"Initialized process pool with {self.config.max_workers} workers"
            )
        else:
            # Use thread pool for I/O-bound tasks
            self.executor = ThreadPoolExecutor(max_workers=self.config.max_workers)
            logger.info(
                f"Initialized thread pool with {self.config.max_workers} workers"
            )

        # Semaphore for concurrent task limiting
        self.semaphore = asyncio.Semaphore(self.config.max_workers)

    async def execute_task(
        self, task_id: str, func: Callable, *args, **kwargs
    ) -> TaskResult:
        """Execute a single task with error handling and timing."""
        start_time = time.time()

        async with self.semaphore:
            try:
                # Update running tasks
                self.running_tasks[task_id] = {
                    "start_time": start_time,
                    "func": func.__name__,
                }

                # Update concurrent count
                current_concurrent = len(self.running_tasks)
                if current_concurrent > self.stats["max_concurrent"]:
                    self.stats["max_concurrent"] = current_concurrent
                self.stats["concurrent_tasks"] = current_concurrent

                # Execute task with timeout
                if asyncio.iscoroutinefunction(func):
                    result = await asyncio.wait_for(
                        func(*args, **kwargs), timeout=self.config.timeout
                    )
                else:
                    # Run sync function in executor
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        self.executor, functools.partial(func, *args, **kwargs)
                    )

                end_time = time.time()

                # Create successful result
                task_result = TaskResult(
                    task_id=task_id,
                    success=True,
                    result=result,
                    start_time=start_time,
                    end_time=end_time,
                )

                # Update statistics
                self._update_stats(task_result)

                # Call progress callback if provided
                if self.config.progress_callback:
                    await self.config.progress_callback(task_result)

                return task_result

            except asyncio.TimeoutError:
                end_time = time.time()
                error_msg = f"Task {task_id} timed out after {self.config.timeout}s"
                logger.warning(error_msg)

                task_result = TaskResult(
                    task_id=task_id,
                    success=False,
                    error=TimeoutError(error_msg),
                    start_time=start_time,
                    end_time=end_time,
                )

                self._update_stats(task_result)
                return task_result

            except Exception as e:
                end_time = time.time()
                logger.error(f"Task {task_id} failed: {e}")

                task_result = TaskResult(
                    task_id=task_id,
                    success=False,
                    error=e,
                    start_time=start_time,
                    end_time=end_time,
                )

                self._update_stats(task_result)
                return task_result

            finally:
                # Remove from running tasks
                if task_id in self.running_tasks:
                    del self.running_tasks[task_id]

    async def execute_tasks(
        self, tasks: List[Tuple[str, Callable, tuple, dict]]
    ) -> List[TaskResult]:
        """Execute multiple tasks in parallel."""
        if not self.executor:
            await self.initialize()

        self.stats["total_tasks"] += len(tasks)
        logger.info(f"Executing {len(tasks)} tasks in parallel")

        # Create task coroutines
        coroutines = []
        for task_id, func, args, kwargs in tasks:
            coro = self.execute_task(task_id, func, *args, **kwargs)
            coroutines.append(coro)

        # Execute all tasks concurrently
        results = await asyncio.gather(*coroutines, return_exceptions=True)

        # Process results
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                # Handle exception from gather
                task_result = TaskResult(task_id="unknown", success=False, error=result)
                processed_results.append(task_result)
            else:
                processed_results.append(result)

        self.completed_tasks.extend(processed_results)
        logger.info(f"Completed {len(processed_results)} tasks")

        return processed_results

    async def execute_batched_tasks(
        self, tasks: List[Tuple[str, Callable, tuple, dict]]
    ) -> List[TaskResult]:
        """Execute tasks in batches to manage resource usage."""
        if not self.executor:
            await self.initialize()

        all_results = []
        total_tasks = len(tasks)
        processed_count = 0

        # Process in batches
        for i in range(0, total_tasks, self.config.chunk_size):
            batch = tasks[i : i + self.config.chunk_size]
            batch_num = i // self.config.chunk_size + 1
            total_batches = (
                total_tasks + self.config.chunk_size - 1
            ) // self.config.chunk_size

            logger.info(
                f"Processing batch {batch_num}/{total_batches} ({len(batch)} tasks)"
            )

            # Execute batch
            batch_results = await self.execute_tasks(batch)
            all_results.extend(batch_results)
            processed_count += len(batch)

            # Small delay between batches
            if i + self.config.chunk_size < total_tasks:
                await asyncio.sleep(0.1)

        logger.info(f"Completed all {total_tasks} tasks in {total_batches} batches")
        return all_results

    async def execute_with_retry(
        self, task_id: str, func: Callable, *args, **kwargs
    ) -> TaskResult:
        """Execute task with retry logic."""
        last_error = None

        for attempt in range(self.config.retry_attempts):
            try:
                # Add delay for retries (except first attempt)
                if attempt > 0:
                    await asyncio.sleep(self.config.retry_delay * attempt)

                result = await self.execute_task(
                    f"{task_id}_retry_{attempt}", func, *args, **kwargs
                )

                if result.success:
                    if attempt > 0:
                        logger.info(
                            f"Task {task_id} succeeded on attempt {attempt + 1}"
                        )
                    return result
                else:
                    last_error = result.error

            except Exception as e:
                last_error = e
                logger.warning(f"Task {task_id} attempt {attempt + 1} failed: {e}")

        # All retries failed
        error_msg = f"Task {task_id} failed after {self.config.retry_attempts} attempts"
        logger.error(error_msg)

        return TaskResult(
            task_id=task_id,
            success=False,
            error=last_error or Exception("Unknown error"),
            start_time=time.time(),
            end_time=time.time(),
        )

    def _update_stats(self, result: TaskResult):
        """Update processing statistics."""
        self.stats["completed_tasks"] += 1

        if result.success:
            self.stats["total_execution_time"] += result.execution_time
        else:
            self.stats["failed_tasks"] += 1

        # Calculate average execution time
        if self.stats["completed_tasks"] > 0:
            self.stats["avg_execution_time"] = (
                self.stats["total_execution_time"] / self.stats["completed_tasks"]
            )

    def get_stats(self) -> Dict[str, Any]:
        """Get current processing statistics."""
        return {
            **self.stats,
            "success_rate": (
                (self.stats["completed_tasks"] - self.stats["failed_tasks"])
                / self.stats["completed_tasks"]
                * 100
                if self.stats["completed_tasks"] > 0
                else 0
            ),
            "running_tasks": len(self.running_tasks),
            "config": {
                "max_workers": self.config.max_workers,
                "timeout": self.config.timeout,
                "chunk_size": self.config.chunk_size,
                "retry_attempts": self.config.retry_attempts,
            },
        }

    def reset_stats(self):
        """Reset processing statistics."""
        self.stats = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "total_execution_time": 0.0,
            "avg_execution_time": 0.0,
            "concurrent_tasks": 0,
            "max_concurrent": 0,
        }

    async def close(self):
        """Close parallel processing resources."""
        if self.executor:
            self.executor.shutdown(wait=True)
            logger.info("Parallel processor executor shutdown")

        # Cancel any running tasks
        for task_id in list(self.running_tasks.keys()):
            logger.warning(f"Cancelling running task: {task_id}")
            # Note: In a real implementation, you'd want to track and cancel actual task futures


class BatchProcessor:
    """Specialized processor for batch operations like embedding generation."""

    def __init__(self, parallel_config: Optional[ParallelConfig] = None):
        self.processor = ParallelProcessor(parallel_config)

    async def process_embeddings_batch(
        self, texts: List[str], embed_func: Callable
    ) -> List[TaskResult]:
        """Process multiple texts for embedding generation."""
        tasks = []

        for i, text in enumerate(texts):
            task_id = f"embed_{i}"
            tasks.append((task_id, embed_func, (text,), {}))

        return await self.processor.execute_batched_tasks(tasks)

    async def process_retrieval_batch(
        self, queries: List[str], retrieve_func: Callable
    ) -> List[TaskResult]:
        """Process multiple queries for vector retrieval."""
        tasks = []

        for i, query in enumerate(queries):
            task_id = f"retrieve_{i}"
            tasks.append((task_id, retrieve_func, (query,), {}))

        return await self.processor.execute_batched_tasks(tasks)

    async def process_database_batch(
        self, operations: List[Tuple[str, Callable, tuple, dict]]
    ) -> List[TaskResult]:
        """Process multiple database operations."""
        tasks = []

        for i, (op_type, func, args, kwargs) in enumerate(operations):
            task_id = f"db_{op_type}_{i}"
            tasks.append((task_id, func, args, kwargs))

        return await self.processor.execute_batched_tasks(tasks)


# Decorator for parallel execution
def parallel_execute(max_workers: int = 10, timeout: float = 30.0):
    """Decorator to make functions execute in parallel when called with multiple inputs."""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            # If called with single arguments, execute normally
            if len(args) <= 1 and not kwargs:
                return await func(*args, **kwargs)

            # If called with multiple arguments, execute in parallel
            processor = ParallelProcessor(
                ParallelConfig(max_workers=max_workers, timeout=timeout)
            )

            await processor.initialize()

            # Create tasks for each argument
            tasks = []
            for i, arg in enumerate(args):
                if isinstance(arg, (list, tuple)):
                    # Handle nested arguments
                    task_id = f"parallel_{i}"
                    tasks.append((task_id, func, arg, kwargs))
                else:
                    # Handle single arguments
                    task_id = f"parallel_{i}"
                    tasks.append((task_id, func, (arg,), kwargs))

            # Execute in parallel
            results = await processor.execute_tasks(tasks)
            await processor.close()

            # Extract results in order
            successful_results = []
            for result in results:
                if result.success:
                    successful_results.append(result.result)
                else:
                    logger.error(f"Parallel task failed: {result.error}")

            return successful_results

        return wrapper

    return decorator


# Utility functions for common parallel patterns
async def parallel_map(
    func: Callable, items: List[Any], max_workers: int = 10
) -> List[Any]:
    """Apply function to items in parallel."""
    processor = ParallelProcessor(ParallelConfig(max_workers=max_workers))
    await processor.initialize()

    tasks = [(f"map_{i}", func, (item,), {}) for i, item in enumerate(items)]
    results = await processor.execute_tasks(tasks)

    await processor.close()

    # Extract successful results in order
    successful_results = []
    for result in results:
        if result.success:
            successful_results.append(result.result)
        else:
            logger.error(f"Parallel map task failed: {result.error}")

    return successful_results


async def parallel_filter(
    func: Callable, items: List[Any], max_workers: int = 10
) -> List[Any]:
    """Filter items using function in parallel."""
    processor = ParallelProcessor(ParallelConfig(max_workers=max_workers))
    await processor.initialize()

    tasks = [(f"filter_{i}", func, (item,), {}) for i, item in enumerate(items)]
    results = await processor.execute_tasks(tasks)

    await processor.close()

    # Extract successful results in order
    successful_results = []
    for result in results:
        if result.success:
            if result.result:  # Keep items where function returns True
                successful_results.append(result.args[0][0])  # Get original item
        else:
            logger.error(f"Parallel filter task failed: {result.error}")

    return successful_results


# Performance monitoring for parallel processing
async def benchmark_parallel_processing(
    func: Callable,
    test_data: List[Any],
    max_workers_range: List[int] = [1, 2, 4, 8, 16],
) -> Dict[str, Any]:
    """Benchmark parallel processing with different worker counts."""
    benchmark_results = {}

    for workers in max_workers_range:
        start_time = time.time()

        processor = ParallelProcessor(ParallelConfig(max_workers=workers))
        await processor.initialize()

        tasks = [
            (f"benchmark_{i}", func, (item,), {}) for i, item in enumerate(test_data)
        ]
        results = await processor.execute_tasks(tasks)

        end_time = time.time()
        execution_time = end_time - start_time

        # Calculate statistics
        successful_results = [r for r in results if r.success]
        success_rate = len(successful_results) / len(results) * 100

        benchmark_results[workers] = {
            "execution_time": execution_time,
            "success_rate": success_rate,
            "throughput": len(successful_results) / execution_time,
            "avg_task_time": execution_time / len(results),
            "stats": processor.get_stats(),
        }

        await processor.close()

        logger.info(
            f"Benchmark with {workers} workers: {execution_time:.2f}s, {success_rate:.1f}% success"
        )

    # Find optimal worker count
    optimal_workers = max(
        benchmark_results.keys(), key=lambda w: benchmark_results[w]["throughput"]
    )

    return {
        "optimal_workers": optimal_workers,
        "benchmark_results": benchmark_results,
        "recommendation": f"Use {optimal_workers} workers for best throughput",
    }
