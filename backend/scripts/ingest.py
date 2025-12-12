#!/usr/bin/env python3
"""
Content ingestion script for Robotics Book RAG chatbot.
Processes MDX files from docs directory and stores them in vector database.
"""

import os
import sys
import asyncio
import argparse
import hashlib
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import time
from datetime import datetime

# Add backend src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

try:
    # Add backend src to path first
    backend_src = os.path.join(os.path.dirname(__file__), "..", "src")
    if backend_src not in sys.path:
        sys.path.insert(0, backend_src)

    from services.ingestion import ingestion_service
    from services.embeddings import embedding_service
    from services.vector_store import vector_store
    from models.database import get_db_connection
    from utils.config import get_config
    from utils.errors import IngestionError, ValidationError
except ImportError as e:
    print(f"Import error: {e}")
    print(
        "Make sure you're running this script from backend directory with all dependencies installed."
    )
    sys.exit(1)


class ProgressTracker:
    """Tracks ingestion progress and provides status updates."""

    def __init__(self, total_files: int = 0):
        self.total_files = total_files
        self.processed_files = 0
        self.failed_files = 0
        self.skipped_files = 0
        self.total_chunks = 0
        self.start_time = time.time()
        self.current_file = ""
        self.current_batch = 0
        self.total_batches = 0

    def start_batch(self, batch_num: int, total_batches: int, batch_size: int):
        """Start processing a new batch."""
        self.current_batch = batch_num
        self.total_batches = total_batches
        print(f"\n🔄 Batch {batch_num}/{total_batches} ({batch_size} files)")

    def update_file_progress(self, file_path: str, status: str, chunks: int = 0):
        """Update progress for a single file."""
        self.current_file = str(file_path)

        if status == "processed":
            self.processed_files += 1
            self.total_chunks += chunks
            file_name = (
                Path(file_path).name if isinstance(file_path, str) else file_path.name
            )
            print(f"  ✅ {file_name} → {chunks} chunks")
        elif status == "skipped":
            self.skipped_files += 1
            file_name = (
                Path(file_path).name if isinstance(file_path, str) else file_path.name
            )
            print(f"  ⏭️  {file_name} → skipped")
        elif status == "failed":
            self.failed_files += 1
            file_name = (
                Path(file_path).name if isinstance(file_path, str) else file_path.name
            )
            print(f"  ❌ {file_name} → failed")

    def get_progress_summary(self) -> Dict[str, Any]:
        """Get current progress summary."""
        elapsed_time = time.time() - self.start_time
        files_completed = self.processed_files + self.failed_files + self.skipped_files

        return {
            "total_files": self.total_files,
            "processed_files": self.processed_files,
            "failed_files": self.failed_files,
            "skipped_files": self.skipped_files,
            "files_completed": files_completed,
            "completion_percentage": (files_completed / self.total_files * 100)
            if self.total_files > 0
            else 0,
            "total_chunks": self.total_chunks,
            "elapsed_time": elapsed_time,
            "current_file": self.current_file,
            "current_batch": f"{self.current_batch}/{self.total_batches}",
            "estimated_remaining": self._estimate_remaining_time(),
        }

    def _estimate_remaining_time(self) -> float:
        """Estimate remaining time based on current progress."""
        files_completed = self.processed_files + self.failed_files + self.skipped_files
        if files_completed == 0:
            return 0

        elapsed_time = time.time() - self.start_time
        avg_time_per_file = elapsed_time / files_completed
        remaining_files = self.total_files - files_completed
        return avg_time_per_file * remaining_files

    def print_summary(self):
        """Print progress summary."""
        summary = self.get_progress_summary()
        print(f"\n📊 Progress Summary:")
        print(
            f"   Files: {summary['processed_files']} processed, {summary['failed_files']} failed, {summary['skipped_files']} skipped"
        )
        print(
            f"   Progress: {summary['completion_percentage']:.1f}% ({summary['files_completed']}/{summary['total_files']})"
        )
        print(f"   Chunks: {summary['total_chunks']} total")
        print(
            f"   Time: {summary['elapsed_time']:.1f}s elapsed, ~{summary['estimated_remaining']:.1f}s remaining"
        )


class MDXDiscovery:
    """Discovers and processes MDX files for ingestion."""

    def __init__(self, docs_path: str):
        self.docs_path = Path(docs_path)
        self.processed_files = set()
        self.skipped_files = []
        self.error_files = []
        self.progress_tracker = None

    def discover_mdx_files(self, force: bool = False) -> List[Path]:
        """Discover all MDX files in docs directory."""
        if not self.docs_path.exists():
            raise IngestionError(f"Docs directory not found: {self.docs_path}")

        mdx_files = list(self.docs_path.rglob("*.mdx"))

        if not force:
            # Filter out already processed files
            unprocessed_files = []
            for file_path in mdx_files:
                file_hash = self._get_file_hash(file_path)
                if file_hash not in self.processed_files:
                    unprocessed_files.append(file_path)
            mdx_files = unprocessed_files

        return sorted(mdx_files, key=lambda x: str(x))

    def _get_file_hash(self, file_path: Path) -> str:
        """Get hash of file content and modification time."""
        try:
            stat = file_path.stat()
            content = file_path.read_text(encoding="utf-8")
            content_hash = hashlib.md5(content.encode("utf-8")).hexdigest()
            mtime_hash = str(int(stat.st_mtime))
            return f"{content_hash}_{mtime_hash}"
        except Exception as e:
            print(f"Error hashing file {file_path}: {e}")
            return ""

    def _should_process_file(self, file_path: Path) -> bool:
        """Check if file should be processed."""
        # Skip if in error list
        if file_path in self.error_files:
            return False

        # Skip if too small (likely empty or frontmatter only)
        try:
            if file_path.stat().st_size < 100:
                return False
        except:
            return False

        return True

    async def process_files(
        self, file_paths: List[Path], batch_size: int = 10
    ) -> Dict[str, Any]:
        """Process a list of MDX files with progress tracking."""
        # Initialize progress tracker
        self.progress_tracker = ProgressTracker(len(file_paths))

        results = {
            "total_files": len(file_paths),
            "processed_files": 0,
            "skipped_files": 0,
            "error_files": 0,
            "total_chunks": 0,
            "processing_time": 0,
            "files": [],
        }

        start_time = time.time()
        total_batches = (len(file_paths) + batch_size - 1) // batch_size

        # Process files in batches
        for i in range(0, len(file_paths), batch_size):
            batch = file_paths[i : i + batch_size]
            batch_num = i // batch_size + 1

            self.progress_tracker.start_batch(batch_num, total_batches, len(batch))

            batch_results = await self._process_batch(batch)

            # Update results
            results["processed_files"] += batch_results["processed"]
            results["skipped_files"] += batch_results["skipped"]
            results["error_files"] += batch_results["error"]
            results["total_chunks"] += batch_results["total_chunks"]
            results["files"].extend(batch_results["files"])

            # Print progress summary after each batch
            self.progress_tracker.print_summary()

            # Small delay between batches
            if i + batch_size < len(file_paths):
                await asyncio.sleep(0.5)

        results["processing_time"] = time.time() - start_time

        # Final summary
        print(f"\n🎉 Processing completed!")
        print(f"   Total files: {results['total_files']}")
        print(f"   Processed: {results['processed_files']}")
        print(f"   Skipped: {results['skipped_files']}")
        print(f"   Failed: {results['error_files']}")
        print(f"   Total chunks: {results['total_chunks']}")
        print(f"   Processing time: {results['processing_time']:.1f}s")

        return results

    async def _process_batch(self, file_paths: List[Path]) -> Dict[str, Any]:
        """Process a batch of files."""
        batch_results = {
            "processed": 0,
            "skipped": 0,
            "error": 0,
            "total_chunks": 0,
            "files": [],
        }

        for file_path in file_paths:
            try:
                if not self._should_process_file(file_path):
                    self.skipped_files.append(file_path)
                    batch_results["skipped"] += 1
                    continue

                # Process the file
                file_result = await self._process_single_file(file_path)

                if file_result["success"]:
                    self.processed_files.add(self._get_file_hash(file_path))
                    batch_results["processed"] += 1
                    batch_results["total_chunks"] += file_result["chunks_created"]
                else:
                    self.error_files.append(file_path)
                    batch_results["error"] += 1

                batch_results["files"].append(file_result)

            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
                self.error_files.append(file_path)
                batch_results["error"] += 1
                batch_results["files"].append(
                    {
                        "file_path": str(file_path.relative_to(self.docs_path)),
                        "success": False,
                        "error": str(e),
                        "chunks_created": 0,
                        "processing_time": 0,
                        "size": 0,
                    }
                )

        return batch_results

    async def _process_single_file(self, file_path: Path) -> Dict[str, Any]:
        """Process a single MDX file with enhanced error handling."""
        start_time = time.time()
        relative_path = str(file_path.relative_to(self.docs_path))
        
        try:
            print(f"Processing: {relative_path}")
            
            # Validate file before processing
            validation_result = self._validate_file(file_path)
            if not validation_result['valid']:
                return {
                    "file_path": relative_path,
                    "success": False,
                    "error": f"Validation failed: {validation_result['error']}",
                    "chunks_created": 0,
                    "processing_time": time.time() - start_time,
                    "size": file_path.stat().st_size if file_path.exists() else 0,
                }

            # Use ingestion service to process file
            chunks = await ingestion_service.process_mdx_file(file_path)
            
            # Validate chunks
            chunk_validation = self._validate_chunks(chunks)
            if not chunk_validation['valid']:
                return {
                    "file_path": relative_path,
                    "success": False,
                    "error": f"Chunk validation failed: {chunk_validation['error']}",
                    "chunks_created": 0,
                    "processing_time": time.time() - start_time,
                    "size": file_path.stat().st_size,
                }

            # Update progress tracker
            if self.progress_tracker:
                self.progress_tracker.update_file_progress(file_path, "processed", len(chunks))

            return {
                "file_path": relative_path,
                "success": True,
                "chunks_created": len(chunks),
                "processing_time": time.time() - start_time,
                "size": file_path.stat().st_size,
            }

        except Exception as e:
            # Update progress tracker
            if self.progress_tracker:
                self.progress_tracker.update_file_progress(file_path, "failed")
            
            # Log detailed error information
            error_info = {
                "file_path": relative_path,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "timestamp": datetime.now().isoformat(),
                "file_size": file_path.stat().st_size if file_path.exists() else 0
            }
            
            print(f"❌ Error processing {relative_path}: {e}")
            await self._log_processing_error(error_info)

            return {
                "file_path": relative_path,
                "success": False,
                "error": str(e),
                "chunks_created": 0,
                "processing_time": time.time() - start_time,
                "size": file_path.stat().st_size if file_path.exists() else 0,
            }

    def _validate_file(self, file_path: Path) -> Dict[str, Any]:
        """Validate file before processing."""
        try:
            # Check if file exists
            if not file_path.exists():
                return {"valid": False, "error": "File does not exist"}
            
            # Check file size
            stat = file_path.stat()
            if stat.st_size == 0:
                return {"valid": False, "error": "File is empty"}
            
            if stat.st_size > 10 * 1024 * 1024:  # 10MB limit
                return {"valid": False, "error": "File too large (>10MB)"}
            
            # Check if file is readable
            try:
                content = file_path.read_text(encoding='utf-8')
                if not content.strip():
                    return {"valid": False, "error": "File contains no content"}
                
                # Check for minimum content length
                if len(content.strip()) < 100:
                    return {"valid": False, "error": "File content too short (<100 chars)"}
                    
            except UnicodeDecodeError:
                return {"valid": False, "error": "File encoding not supported (use UTF-8)"}
            
            return {"valid": True}
            
        except Exception as e:
            return {"valid": False, "error": f"Validation error: {str(e)}"}

    def _validate_chunks(self, chunks: List[Any]) -> Dict[str, Any]:
        """Validate generated chunks."""
        if not chunks:
            return {"valid": False, "error": "No chunks generated"}
        
        if len(chunks) > 100:  # Reasonable limit
            return {"valid": False, "error": "Too many chunks generated (>100)"}
        
        # Validate each chunk
        for i, chunk in enumerate(chunks):
            if not hasattr(chunk, 'content') or not chunk.content.strip():
                return {"valid": False, "error": f"Chunk {i} has no content"}
            
            if len(chunk.content) > 2000:  # Max chunk size
                return {"valid": False, "error": f"Chunk {i} too long (>2000 chars)"}
        
        return {"valid": True}

    async def _log_processing_error(self, error_info: Dict[str, Any]):
        """Log processing errors for recovery analysis."""
        try:
            error_log_file = Path("processing_errors.jsonl")
            
            # Append error to log file
            with open(error_log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(error_info) + "\n")
                
        except Exception as e:
            print(f"Failed to log processing error: {e}")

    async def retry_failed_files(self, failed_files: List[str], max_retries: int = 3) -> Dict[str, Any]:
        """Retry processing failed files with exponential backoff."""
        if not failed_files:
            return {"retried": 0, "successful": 0, "still_failed": 0}
        
        print(f"\n🔄 Retrying {len(failed_files)} failed files...")
        
        retry_results = {"retried": 0, "successful": 0, "still_failed": 0}
        
        for file_path_str in failed_files:
            file_path = self.docs_path / file_path_str
            
            for attempt in range(max_retries):
                try:
                    print(f"  Retry {attempt + 1}/{max_retries}: {file_path_str}")
                    
                    # Wait before retry (exponential backoff)
                    if attempt > 0:
                        wait_time = 2 ** attempt
                        print(f"    Waiting {wait_time}s before retry...")
                        await asyncio.sleep(wait_time)
                    
                    # Attempt to process again
                    result = await self._process_single_file(file_path)
                    
                    if result["success"]:
                        retry_results["successful"] += 1
                        print(f"    ✅ Successfully retried {file_path_str}")
                        break
                    else:
                        print(f"    ❌ Retry failed: {result['error']}")
                        
                except Exception as e:
                    print(f"    ❌ Retry error: {e}")
            
            else:
                # All retries failed
                retry_results["still_failed"] += 1
                print(f"    ❌ All retries failed for {file_path_str}")
            
            retry_results["retried"] += 1
        
        print(f"\n📊 Retry Results:")
        print(f"   Retried: {retry_results['retried']}")
        print(f"   Successful: {retry_results['successful']}")
        print(f"   Still failed: {retry_results['still_failed']}")
        
        return retry_results

    async def generate_recovery_report(self) -> Dict[str, Any]:
        """Generate a comprehensive recovery report."""
        try:
            error_log_file = Path("processing_errors.jsonl")
            
            if not error_log_file.exists():
                return {"message": "No error log found"}
            
            # Analyze error patterns
            error_patterns = {}
            recent_errors = []
            
            with open(error_log_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        error_data = json.loads(line.strip())
                        error_type = error_data.get("error_type", "Unknown")
                        
                        # Count error types
                        error_patterns[error_type] = error_patterns.get(error_type, 0) + 1
                        
                        # Keep recent errors (last 50)
                        recent_errors.append(error_data)
                        if len(recent_errors) > 50:
                            recent_errors.pop(0)
                            
                    except json.JSONDecodeError:
                        continue
            
            # Generate recommendations
            recommendations = self._generate_error_recommendations(error_patterns)
            
            report = {
                "generated_at": datetime.now().isoformat(),
                "total_errors": len(recent_errors),
                "error_patterns": error_patterns,
                "recent_errors": recent_errors[-10:],  # Last 10 errors
                "recommendations": recommendations
            }
            
            # Save report
            report_file = Path("recovery_report.json")
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)
            
            print(f"📄 Recovery report generated: {report_file}")
            return report
            
        except Exception as e:
            print(f"Error generating recovery report: {e}")
            return {"error": str(e)}

    def _generate_error_recommendations(self, error_patterns: Dict[str, int]) -> List[str]:
        """Generate recommendations based on error patterns."""
        recommendations = []
        
        if "ValidationError" in error_patterns:
            recommendations.append("Consider updating file validation rules or fixing file format issues")
        
        if "UnicodeDecodeError" in error_patterns:
            recommendations.append("Ensure all MDX files are saved with UTF-8 encoding")
        
        if "FileNotFoundError" in error_patterns:
            recommendations.append("Check file paths and ensure all referenced files exist")
        
        if "MemoryError" in error_patterns:
            recommendations.append("Consider reducing batch size or increasing available memory")
        
        if not recommendations:
            recommendations.append("No specific recommendations - errors appear to be isolated incidents")
        
        return recommendations


class ErrorRecoveryManager:
    """Manages error recovery and retry logic for ingestion."""
    
    def __init__(self):
        self.error_log = []
        self.retry_queue = []
        
    async def handle_ingestion_error(self, error_info: Dict[str, Any]):
        """Handle ingestion errors with appropriate recovery strategy."""
        self.error_log.append(error_info)
        
        # Determine recovery strategy based on error type
        error_type = error_info.get('error_type', 'Unknown')
        
        if error_type in ['ValidationError', 'FileNotFoundError']:
            # These are likely unrecoverable without user intervention
            await self._log_unrecoverable_error(error_info)
        elif error_type in ['ConnectionError', 'TimeoutError']:
            # These might be recoverable with retry
            self.retry_queue.append(error_info)
        else:
            # Unknown errors - log for manual review
            await self._log_unknown_error(error_info)
    
    async def _log_unrecoverable_error(self, error_info: Dict[str, Any]):
        """Log errors that require manual intervention."""
        print(f"🔴 Unrecoverable error: {error_info['file_path']} - {error_info['error_message']}")
        
    async def _log_unknown_error(self, error_info: Dict[str, Any]):
        """Log unknown errors for analysis."""
        print(f"🟡 Unknown error: {error_info['file_path']} - {error_info['error_message']}")
        
    def get_recovery_summary(self) -> Dict[str, Any]:
        """Get summary of errors and recovery actions."""
        return {
            'total_errors': len(self.error_log),
            'retry_queue_size': len(self.retry_queue),
            'error_types': self._analyze_error_types(),
            'recommended_actions': self._get_recommended_actions()
        }
    
    def _analyze_error_types(self) -> Dict[str, int]:
        """Analyze error types in the log."""
        types = {}
        for error in self.error_log:
            error_type = error.get('error_type', 'Unknown')
            types[error_type] = types.get(error_type, 0) + 1
        return types
    
    def _get_recommended_actions(self) -> List[str]:
        """Get recommended actions based on error analysis."""
        actions = []
        error_types = self._analyze_error_types()
        
        if error_types.get('ValidationError', 0) > 0:
            actions.append("Review and fix file format issues")
        
        if error_types.get('ConnectionError', 0) > 2:
            actions.append("Check network connectivity and service availability")
        
        if len(self.retry_queue) > 5:
            actions.append("Consider running retry process for failed files")
        
        return actions

        except Exception as e:
            return {
                "file_path": str(file_path.relative_to(self.docs_path)),
                "success": False,
                "error": str(e),
                "chunks_created": 0,
                "processing_time": 0,
                "size": 0,
            }

    def get_statistics(self) -> Dict[str, Any]:
        """Get discovery statistics."""
        return {
            "processed_files": len(self.processed_files),
            "skipped_files": len(self.skipped_files),
            "error_files": len(self.error_files),
            "total_discovered": len(self.processed_files)
            + len(self.skipped_files)
            + len(self.error_files),
        }


class ContentIngester:
    """Main content ingestion orchestrator."""

    def __init__(self):
        self.config = get_config()
        self.discovery = MDXDiscovery(self.config.DOCS_ROOT)

    async def ingest_all_content(
        self, force: bool = False, batch_size: int = 10, cleanup: bool = False
    ) -> Dict[str, Any]:
        """Ingest all content from MDX files."""
        print(f"Starting content ingestion (force={force}, cleanup={cleanup})")

        start_time = time.time()

        try:
            # Cleanup if requested
            if cleanup:
                await self._cleanup_existing_content()

            # Discover files
            file_paths = self.discovery.discover_mdx_files(force)

            if not file_paths:
                raise IngestionError("No MDX files found to process")

            # Process files
            process_results = await self.discovery.process_files(file_paths, batch_size)

            # Update vector store
            if process_results["total_chunks"] > 0:
                await self._update_vector_store()

            processing_time = time.time() - start_time

            results = {
                "success": True,
                "total_files": process_results["total_files"],
                "processed_files": process_results["processed_files"],
                "skipped_files": process_results["skipped_files"],
                "error_files": process_results["error_files"],
                "total_chunks": process_results["total_chunks"],
                "processing_time": processing_time,
                "files": process_results["files"],
                "discovery_stats": self.discovery.get_statistics(),
            }

            print(
                f"✅ Ingestion completed: {results['processed_files']} files processed, {results['total_chunks']} chunks created"
            )
            return results

        except Exception as e:
            print(f"❌ Ingestion failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "processing_time": time.time() - start_time,
            }

    async def _update_vector_store(self):
        """Update vector store with new content."""
        try:
            # This would trigger reindexing of the vector store
            # For now, just log that vector store should be updated
            print("Vector store update placeholder - would trigger reindexing")
        except Exception as e:
            print(f"Vector store update failed: {e}")

    async def _cleanup_existing_content(self):
        """Clean up existing content."""
        try:
            # Clear vector store
            await vector_store.delete_by_filter({})
            print("Cleaned up existing vector store content")
        except Exception as e:
            print(f"Cleanup failed: {e}")

    async def get_ingestion_status(self) -> Dict[str, Any]:
        """Get current ingestion status."""
        try:
            # Get vector store info
            vector_info = await vector_store.get_collection_info()

            # Get database stats
            conn = get_db_connection()
            db_stats = {}
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT COUNT(*) FROM content_chunks")
                    chunk_count = cur.fetchone()[0]
                    db_stats["chunk_count"] = chunk_count
            except Exception as e:
                print(f"Failed to get database stats: {e}")
            finally:
                conn.close()

            return {
                "vector_store": vector_info,
                "database": db_stats,
                "discovery": self.discovery.get_statistics(),
                "last_updated": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            return {"error": str(e), "last_updated": datetime.utcnow().isoformat()}


async def main():
    """Main ingestion script entry point."""
    parser = argparse.ArgumentParser(
        description="Ingest MDX content into RAG vector database"
    )
    parser.add_argument("--docs-path", default="../docs", help="Path to docs directory")
    parser.add_argument(
        "--force", action="store_true", help="Force reprocessing of all files"
    )
    parser.add_argument(
        "--batch-size", type=int, default=10, help="Batch size for processing"
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Clean up existing content before ingestion",
    )
    parser.add_argument("--status", action="store_true", help="Show ingestion status")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    try:
        ingester = ContentIngester()

        if args.status:
            status = await ingester.get_ingestion_status()
            print(json.dumps(status, indent=2))
        else:
            results = await ingester.ingest_all_content(
                force=args.force, batch_size=args.batch_size, cleanup=args.cleanup
            )

            if args.verbose:
                print(json.dumps(results, indent=2))
            else:
                print(
                    f"✅ Ingestion completed: {results['processed_files']} files, {results['total_chunks']} chunks"
                )

    except KeyboardInterrupt:
        print("\nIngestion interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Ingestion failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
