#!/usr/bin/env python3
"""
Script to process specific book chapters and store embeddings in Qdrant
Chapter directories: @docs/01-introduction/, @docs/02-physical-fundamentals/, @docs/03-humanoid-design/
Collection name: Book_Chapters_embadding
"""
import os
import sys
import uuid
import re
from pathlib import Path
import logging

# Add the backend/src to the Python path (running from project root)
backend_src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(backend_src_path))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from src.embedding.services.cohere_service import CohereEmbeddingService
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


def read_book_content_from_pdf(file_path):
    """
    Read and chunk PDF files with structure preservation
    """
    try:
        import PyPDF2
    except ImportError:
        print("PyPDF2 not installed. Install with: pip install PyPDF2")
        return []

    chunks = []
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        full_text = ""

        # Extract text from all pages
        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text()
            full_text += f"\nPAGE_{page_num + 1}\n{page_text}\n"

        # Extract potential chapter/section headings
        # Common patterns for chapters and sections
        chapter_patterns = [
            r'(?:^|\n)\s*Chapter\s+\d+[.:]?\s*[^\n]*\n',
            r'(?:^|\n)\s*Section\s+\d+[.:]?\s*[^\n]*\n',
            r'(?:^|\n)\s*\d+\.\d*\s+[A-Z][^\n]*\n',  # Numbered sections
            r'(?:^|\n)\s*#{1,3}\s*[^\n]+\n',  # Markdown headings
        ]

        # Find chapter breaks and create chunks around them
        text_parts = [full_text]  # Start with full text as single part

        for pattern in chapter_patterns:
            new_parts = []
            for part in text_parts:
                # Split by this pattern
                splits = re.split(pattern, part)
                new_parts.extend(splits)
            text_parts = [p for p in new_parts if p.strip()]

        # Now chunk each part appropriately
        for i, part in enumerate(text_parts):
            if len(part.strip()) < 50:  # Skip very small parts
                continue

            # Break down large parts by structure
            sub_chunks = chunk_text_by_structure(part, max_chunk_size=1200)

            for j, sub_chunk in enumerate(sub_chunks):
                if len(sub_chunk.strip()) < 50:  # Skip very small chunks
                    continue

                # Try to identify chapter/section from content
                chapter_match = re.search(r'Chapter\s+(\d+)', part[:200], re.IGNORECASE)
                section_match = re.search(r'Section\s+([\d.]+)', part[:200], re.IGNORECASE)

                chapter_num = chapter_match.group(1) if chapter_match else "unknown"
                section_num = section_match.group(1) if section_match else "unknown"

                chunks.append({
                    "id": f"chapter-{Path(file_path).parent.name}-ch{chapter_num}-sec{section_num}-part{i}-sub{j}-{uuid.uuid4()}",
                    "text": sub_chunk,
                    "source_file": Path(file_path).name,
                    "source_location": f"ch{chapter_num}_sec{section_num}_part{i}_sub{j}",
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


def read_book_content_from_docx(file_path):
    """
    Read and chunk docx files with structure preservation
    """
    try:
        import docx
    except ImportError:
        print("python-docx not installed. Install with: pip install python-docx")
        return []

    doc = docx.Document(file_path)
    full_text = []

    # Extract text while preserving structure
    for para in doc.paragraphs:
        full_text.append(para.text)

    text = '\n\n'.join(full_text)

    # Process the text similar to the text file method
    chunks = []

    # Look for chapter/section patterns
    chapter_patterns = [
        r'(?:^|\n)\s*Chapter\s+\d+[.:]?\s*[^\n]*',
        r'(?:^|\n)\s*Section\s+\d+[.:]?\s*[^\n]*',
        r'(?:^|\n)\s*\d+\.\d*\s+[A-Z][^\n]*',  # Numbered sections
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
                "id": f"chapter-{Path(file_path).parent.name}-ch{chapter_num}-sec{section_num}-part{i}-sub{j}-{uuid.uuid4()}",
                "text": sub_chunk,
                "source_file": Path(file_path).name,
                "source_location": f"ch{chapter_num}_sec{section_num}_part{i}_sub{j}",
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


def process_specific_chapters():
    """
    Process the specific book chapters and store in Book_Chapters_embadding collection
    """
    print("🤖 Processing Specific Book Chapters for Qdrant Storage")
    print("=" * 60)
    print("Target directories:")
    print("  - @docs/01-introduction/")
    print("  - @docs/02-physical-fundamentals/")
    print("  - @docs/03-humanoid-design/")
    print("Target collection: Book_Chapters_embadding")
    print()

    # Initialize the service with Qdrant storage specifically for book chapters
    service = CohereEmbeddingService(storage_type="qdrant", collection_name="Book_Chapters_embadding")

    print(f"📦 Using Cohere model: {service.config.model}")
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
        chapter_path = Path(chapter_dir)

        if not chapter_path.exists():
            print(f"❌ Directory not found: {chapter_dir}")
            continue

        print(f"📖 Processing chapter directory: {chapter_dir}")

        # Find all supported files in the directory
        files = (
            list(chapter_path.glob("*.txt")) +
            list(chapter_path.glob("*.pdf")) +
            list(chapter_path.glob("*.docx"))
        )

        if not files:
            print(f"   No supported files found in {chapter_dir}")
            continue

        print(f"   Found {len(files)} files to process")

        for file_path in files:
            print(f"   📄 Processing file: {file_path.name}")

            # Determine file type and use appropriate reader
            if file_path.suffix.lower() == '.pdf':
                file_chunks = read_book_content_from_pdf(str(file_path))
            elif file_path.suffix.lower() == '.txt':
                file_chunks = read_book_content_from_text(str(file_path))
            elif file_path.suffix.lower() == '.docx':
                file_chunks = read_book_content_from_docx(str(file_path))
            else:
                print(f"   ❌ Unsupported file format: {file_path.suffix}")
                continue

            print(f"     Found {len(file_chunks)} content chunks to process")

            # Process each chunk
            for i, content_data in enumerate(file_chunks):
                print(f"     📝 Processing chunk {i+1}/{len(file_chunks)} (size: {len(content_data['text'])} chars)")

                chunk = ContentChunk(
                    id=content_data["id"],
                    text=content_data["text"],
                    source_file=content_data["source_file"],
                    source_location=content_data["source_location"],
                    metadata=content_data["metadata"]
                )

                try:
                    embedding = service.process_content_chunk(chunk)
                    print(f"       ✅ Stored in Qdrant: {embedding.chunk_id[:25]}... (dim: {embedding.dimensionality})")
                    total_chunks_processed += 1
                except Exception as e:
                    print(f"       ❌ Error processing chunk: {str(e)}")

    print()
    print("🎉 Chapter embedding process completed!")
    print(f"📊 Total chunks processed and stored in Qdrant: {total_chunks_processed}")
    print(f"🎯 Collection: Book_Chapters_embadding")
    print()
    print("💡 The embeddings are now ready for semantic search and retrieval!")
    print("   Your chatbot can now answer questions grounded in these specific chapters.")


if __name__ == "__main__":
    process_specific_chapters()