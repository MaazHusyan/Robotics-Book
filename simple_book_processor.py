#!/usr/bin/env python3
"""
Simple script to process book chapters and store embeddings in Qdrant
"""
import os
import sys
import uuid
from pathlib import Path

# Add the project root and backend/src to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'backend' / 'src'))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from backend.src.embedding.services.embedding_service_factory import EmbeddingServiceFactory
from backend.src.embedding.models.content_models import ContentChunk


def read_text_file(file_path):
    """Simple function to read text files"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def chunk_text(text, chunk_size=500):
    """Simple function to chunk text"""
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunk_text = text[i:i + chunk_size]
        if chunk_text.strip():  # Only add non-empty chunks
            chunks.append(chunk_text)
    return chunks


def process_book_chapters():
    """
    Process the specific book chapters and store in Qdrant
    """
    print("🤖 Processing Specific Book Chapters for Qdrant Storage")
    print("=" * 60)
    print("Target directories:")
    print("  - docs/01-introduction/")
    print("  - docs/02-physical-fundamentals/")
    print("  - docs/03-humanoid-design/")
    print("Target collection: Book_Chapters_embadding")
    print()

    # Initialize the service
    service = EmbeddingServiceFactory.create_embedding_service(storage_type="qdrant", collection_name="Book_Chapters_embadding")

    print(f"📦 Using embedding model: {service.config.model}")
    print(f"💾 Storing in Qdrant collection: Book_Chapters_embadding")
    print()

    # Define the chapter directories to process
    chapter_dirs = [
        "docs/01-introduction",
        "docs/02-physical-fundamentals",
        "docs/03-humanoid-design"
    ]

    total_chunks_processed = 0

    for chapter_dir in chapter_dirs:
        dir_path = Path(chapter_dir)

        if not dir_path.exists():
            print(f"❌ Directory not found: {chapter_dir}")
            continue

        print(f"📖 Processing chapter directory: {chapter_dir}")

        # Find all text files in the directory
        txt_files = list(dir_path.glob("*.txt"))

        if not txt_files:
            print(f"   No text files found in {chapter_dir}")
            continue

        print(f"   Found {len(txt_files)} text files to process")

        for file_path in txt_files:
            print(f"   📄 Processing file: {file_path.name}")

            try:
                # Read the file content
                content = read_text_file(file_path)

                # Chunk the content
                text_chunks = chunk_text(content, chunk_size=800)  # Reduced chunk size
                print(f"     Found {len(text_chunks)} content chunks to process")

                # Process each chunk
                for i, chunk_text in enumerate(text_chunks):
                    print(f"     📝 Processing chunk {i+1}/{len(text_chunks)} (size: {len(chunk_text)} chars)")

                    # Create ContentChunk object
                    chunk = ContentChunk(
                        id=f"book-chapter-{dir_path.name}-{file_path.stem}-chunk-{i+1}-{uuid.uuid4()}",
                        text=chunk_text,
                        source_file=file_path.name,
                        source_location=f"{dir_path.name}/{file_path.name}",
                        metadata={
                            "chapter_dir": dir_path.name,
                            "source_file": file_path.name,
                            "chunk_index": i+1,
                            "total_chunks": len(text_chunks),
                            "type": "book_chapter"
                        }
                    )

                    try:
                        # Process the chunk (generate embedding and store in Qdrant)
                        embedding = service.process_content_chunk(chunk)
                        print(f"       ✅ Stored in Qdrant: {embedding.chunk_id[:30]}... (dim: {embedding.dimensionality})")
                        total_chunks_processed += 1
                    except Exception as e:
                        print(f"       ❌ Error processing chunk: {str(e)}")

            except Exception as e:
                print(f"   ❌ Error reading file {file_path}: {str(e)}")

    print()
    print("🎉 Book chapter embedding process completed!")
    print(f"📊 Total chunks processed and stored in Qdrant: {total_chunks_processed}")
    print(f"🎯 Collection: Book_Chapters_embadding")
    print()
    print("💡 Your book chapters are now stored in Qdrant and ready for chatbot retrieval!")


if __name__ == "__main__":
    process_book_chapters()