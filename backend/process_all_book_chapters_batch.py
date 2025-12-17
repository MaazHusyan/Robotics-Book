#!/usr/bin/env python3
"""
Script to process ALL book chapters and store embeddings in Qdrant
This version uses batching to be more efficient with API calls
Chapter directories: @backend/backend/docs/01-introduction/, @backend/backend/docs/02-physical-fundamentals/, @backend/backend/docs/03-humanoid-design/
Collection name: All_Book_Chapters
"""
import os
import sys
import uuid
import re
from pathlib import Path
import logging
import time

# Add the backend/src to the Python path (running from project root)
backend_src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(backend_src_path))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from src.embedding.services.embedding_service_factory import EmbeddingServiceFactory
from src.embedding.models.content_models import ContentChunk
from src.utils.qdrant_storage import QdrantEmbeddingStorage


def chunk_text_by_structure(text, max_chunk_size=1000):
    """
    Split text by document structure (headings, paragraphs) instead of character count
    """
    # Split by common heading patterns
    heading_pattern = r'(?:^|\n)(#{1,6}\s+|\d+[\.\d]*\s+|\*\*[^*]+\*\*|__[^_]+__|\n\s*[A-Z][a-z][^:\n]*[:\n])'

    # First split by headings
    parts = re.split(heading_pattern, text)

    chunks = []
    current_chunk = ""

    for part in parts:
        if len(part.strip()) == 0:
            continue

        # If this part looks like a heading/chapter title
        if re.match(r'^(#{1,6}\s+|\d+[\.\d]*\s+)', part) or len(part) < 100:
            # If current chunk is substantial, save it before starting new one with heading
            if len(current_chunk) > 100:  # If we have a substantial chunk
                chunks.append(current_chunk.strip())
                current_chunk = part
            else:
                current_chunk += " " + part
        else:
            # Regular content - add to current chunk
            if len(current_chunk) + len(part) > max_chunk_size:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = part
            else:
                current_chunk += " " + part

    # Add the last chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    # Further split any chunks that are still too large
    final_chunks = []
    for chunk in chunks:
        if len(chunk) > max_chunk_size * 1.5:  # If still too large
            # Split by paragraphs
            paragraphs = chunk.split('\n\n')
            temp_chunk = ""
            for para in paragraphs:
                if len(temp_chunk) + len(para) > max_chunk_size:
                    if temp_chunk.strip():
                        final_chunks.append(temp_chunk.strip())
                    temp_chunk = para
                else:
                    temp_chunk += "\n\n" + para
            if temp_chunk.strip():
                final_chunks.append(temp_chunk.strip())
        else:
            final_chunks.append(chunk)

    return final_chunks


def read_book_content_from_text(file_path):
    """
    Read and chunk text files with structure preservation
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    # Split by common document structure
    chunks = []

    # Look for chapter/section patterns
    chapter_patterns = [
        r'(?:^|\n)\s*Chapter\s+\d+[.:]?\s*[^\n]*',
        r'(?:^|\n)\s*Section\s+\d+[.:]?\s*[^\n]*',
        r'(?:^|\n)\s*\d+\.\d*\s+[A-Z][^\n]*',  # Numbered sections
        r'(?:^|\n)\s*#{1,3}\s*[^\n]*',  # Markdown headings
    ]

    # Split by the most significant structure first
    text_parts = [text]
    for pattern in chapter_patterns:
        new_parts = []
        for part in text_parts:
            splits = re.split(pattern, part)
            new_parts.extend([p for p in splits if p.strip()])
        text_parts = new_parts

    # Process each part
    for i, part in enumerate(text_parts):
        if len(part.strip()) < 50:
            continue

        # Break down by structure
        sub_chunks = chunk_text_by_structure(part, max_chunk_size=1200)

        for j, sub_chunk in enumerate(sub_chunks):
            if len(sub_chunk.strip()) < 50:
                continue

            # Try to identify structure from content
            chapter_match = re.search(r'Chapter\s+(\d+)', part[:200], re.IGNORECASE)
            section_match = re.search(r'Section\s+([\d.]+)', part[:200], re.IGNORECASE)

            chapter_num = chapter_match.group(1) if chapter_match else "unknown"
            section_num = section_match.group(1) if section_match else "unknown"

            chunks.append({
                "id": f"chapter-{Path(file_path).parent.name}-part{i}-sub{j}-{uuid.uuid4()}",
                "text": sub_chunk,
                "source_file": Path(file_path).name,
                "source_location": f"part{i}_sub{j}",
                "metadata": {
                    "chapter_dir": Path(file_path).parent.name,
                    "chapter": chapter_num,
                    "section": section_num,
                    "part": i,
                    "sub_part": j,
                    "file": Path(file_path).name,
                    "type": "book_chapter",
                    "full_path": str(file_path)
                }
            })

    return chunks


def process_batch_with_rate_limit(service, chunks, batch_size=5, max_retries=2, base_delay=30):
    """
    Process content chunks in batches with rate limiting
    For trial keys, process one at a time with significant delays
    """
    total_processed = 0

    for i, content_data in enumerate(chunks):
        print(f"     📝 Processing chunk {i+1}/{len(chunks)} (size: {len(content_data['text'])} chars)")

        chunk = ContentChunk(
            id=content_data["id"],
            text=content_data["text"],
            source_file=content_data["source_file"],
            source_location=content_data["source_location"],
            metadata=content_data["metadata"]
        )

        # Process with rate limiting - one at a time for trial keys
        for attempt in range(max_retries):
            try:
                embedding = service.process_content_chunk(chunk)
                print(f"       ✅ Stored in Qdrant: {embedding.chunk_id[:25]}... (dim: {embedding.dimensionality})")
                total_processed += 1

                # Wait between API calls to respect rate limits for trial key
                print(f"       ⏳ Waiting 5 seconds before next API call...")
                time.sleep(5)
                break  # Success, move to next chunk
            except Exception as e:
                if "429" in str(e) or "Rate Limit" in str(e):
                    # Rate limit error - wait and retry with exponential backoff
                    delay = base_delay * (2 ** attempt)  # Exponential backoff, starting with 30s
                    print(f"       ⏰ Rate limit hit, waiting {delay}s before retry {attempt+1}/{max_retries}")
                    time.sleep(delay)
                    if attempt == max_retries - 1:  # Last attempt
                        print(f"       ❌ Failed after {max_retries} attempts: {str(e)}")
                        # Wait before continuing to next chunk
                        time.sleep(3)
                else:
                    # Other error - don't retry
                    print(f"       ❌ Error processing chunk: {str(e)}")
                    # Wait before continuing to next chunk
                    time.sleep(1)
                    break  # Move to next chunk regardless of error

    return total_processed


def process_all_book_chapters():
    """
    Process ALL book chapters and store in All_Book_Chapters collection
    """
    print("🤖 Processing ALL Book Chapters for Qdrant Storage")
    print("=" * 60)
    print("Target directories:")
    print("  - @backend/backend/docs/01-introduction/")
    print("  - @backend/backend/docs/02-physical-fundamentals/")
    print("  - @backend/backend/docs/03-humanoid-design/")
    print("Target collection: All_Book_Chapters")
    print()

    # Initialize the service with Qdrant storage specifically for all book chapters
    service = EmbeddingServiceFactory.create_embedding_service(storage_type="qdrant", collection_name="All_Book_Chapters")

    print(f"📦 Using embedding model: {service.config.model}")
    print(f"💾 Storing in Qdrant collection: All_Book_Chapters")
    print()

    # Define the chapter directories to process (relative to backend/backend/)
    base_path = Path(__file__).parent / "backend" / "docs"
    chapter_dirs = [
        base_path / "01-introduction",
        base_path / "02-physical-fundamentals",
        base_path / "03-humanoid-design"
    ]

    total_chunks_processed = 0

    for chapter_dir in chapter_dirs:
        if not chapter_dir.exists():
            print(f"❌ Directory not found: {chapter_dir}")
            continue

        print(f"📖 Processing chapter directory: {chapter_dir}")

        # Find all supported files in the directory
        files = list(chapter_dir.glob("*.txt"))

        if not files:
            print(f"   No .txt files found in {chapter_dir}")
            continue

        print(f"   Found {len(files)} .txt files to process")

        for file_path in files:
            print(f"   📄 Processing file: {file_path.name}")

            # Process the text file
            file_chunks = read_book_content_from_text(str(file_path))

            print(f"     Found {len(file_chunks)} content chunks to process")

            # Process chunks with rate limiting
            processed_count = process_batch_with_rate_limit(service, file_chunks)
            total_chunks_processed += processed_count

    print()
    print("🎉 All book chapters embedding process completed!")
    print(f"📊 Total chunks processed and stored in Qdrant: {total_chunks_processed}")
    print(f"🎯 Collection: All_Book_Chapters")
    print()
    print("💡 The embeddings are now ready for semantic search and retrieval!")
    print("   Your chatbot can now answer questions grounded in all book chapters.")


if __name__ == "__main__":
    process_all_book_chapters()