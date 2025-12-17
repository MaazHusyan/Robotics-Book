import re
from typing import List, Optional
from backend.src.embedding.models.content_models import ContentChunk


class ContentChunker:
    """
    Service for splitting content into chunks suitable for embedding.
    """

    def __init__(self, max_tokens: int = 4000, overlap_ratio: float = 0.1):
        """
        Initialize the content chunker.

        Args:
            max_tokens: Maximum number of tokens per chunk (default Cohere limit)
            overlap_ratio: Ratio of overlap between chunks to maintain context
        """
        self.max_tokens = max_tokens
        self.overlap_ratio = overlap_ratio
        # Rough estimation: 1 token ~ 4 characters for English text
        self.max_chars = int(max_tokens * 4)

    def chunk_text(self, text: str, source_file: str = "", source_location: str = "") -> List[ContentChunk]:
        """
        Split text into chunks of appropriate size for embedding.

        Args:
            text: The text to be chunked
            source_file: The source file name
            source_location: The location within the source

        Returns:
            List of ContentChunk objects
        """
        if not text.strip():
            return []

        chunks = []
        text_length = len(text)
        start_idx = 0

        while start_idx < text_length:
            # Determine the end index
            end_idx = start_idx + self.max_chars

            # If we're near the end, just take the remainder
            if end_idx >= text_length:
                chunk_text = text[start_idx:]
                chunk = ContentChunk(
                    text=chunk_text,
                    source_file=source_file,
                    source_location=f"{source_location}:{start_idx}-{end_idx}" if source_location else f"position:{start_idx}-{end_idx}",
                    metadata={"start_idx": start_idx, "end_idx": end_idx, "is_final": True}
                )
                chunks.append(chunk)
                break

            # Try to split at sentence boundary
            chunk_text = text[start_idx:end_idx]

            # Find the last sentence ending in the chunk
            sentence_endings = [chunk_text.rfind('. '), chunk_text.rfind('? '), chunk_text.rfind('! '), chunk_text.rfind('\n')]
            sentence_end = max(sentence_endings)

            # If no sentence ending found, try word boundary
            if sentence_end == -1:
                word_endings = [chunk_text.rfind(' '), chunk_text.rfind('\t')]
                sentence_end = max(word_endings)

            # If still no good split point, just take the max chunk
            if sentence_end > 0:
                actual_end = start_idx + sentence_end + 1
                chunk_text = text[start_idx:actual_end]
            else:
                actual_end = end_idx
                chunk_text = text[start_idx:actual_end]

            # Create the chunk
            chunk = ContentChunk(
                text=chunk_text,
                source_file=source_file,
                source_location=f"{source_location}:{start_idx}-{actual_end}" if source_location else f"position:{start_idx}-{actual_end}",
                metadata={"start_idx": start_idx, "end_idx": actual_end}
            )
            chunks.append(chunk)

            # Move start index forward, considering overlap
            overlap_size = int(self.max_chars * self.overlap_ratio)
            start_idx = max(actual_end - overlap_size, start_idx + 1)

            # Safety check to prevent infinite loop
            if actual_end <= start_idx:
                start_idx += 1

        return chunks

    def chunk_by_paragraphs(self, text: str, source_file: str = "", source_location: str = "") -> List[ContentChunk]:
        """
        Split text by paragraphs, combining small paragraphs as needed.

        Args:
            text: The text to be chunked
            source_file: The source file name
            source_location: The location within the source

        Returns:
            List of ContentChunk objects
        """
        paragraphs = re.split(r'\n\s*\n', text)
        chunks = []
        current_chunk_text = ""
        current_start_idx = 0

        for i, paragraph in enumerate(paragraphs):
            # Check if adding this paragraph would exceed the limit
            if len(current_chunk_text + paragraph) > self.max_chars and current_chunk_text:
                # Save the current chunk
                chunk = ContentChunk(
                    text=current_chunk_text.strip(),
                    source_file=source_file,
                    source_location=f"{source_location}:paragraphs_{current_start_idx}-{i-1}" if source_location else f"paragraphs:{current_start_idx}-{i-1}",
                    metadata={"paragraph_start": current_start_idx, "paragraph_end": i-1}
                )
                chunks.append(chunk)

                # Start a new chunk with the current paragraph
                current_chunk_text = paragraph + "\n\n"
                current_start_idx = i
            else:
                current_chunk_text += paragraph + "\n\n"

        # Add the final chunk if there's content left
        if current_chunk_text.strip():
            chunk = ContentChunk(
                text=current_chunk_text.strip(),
                source_file=source_file,
                source_location=f"{source_location}:paragraphs_{current_start_idx}-{len(paragraphs)-1}" if source_location else f"paragraphs:{current_start_idx}-{len(paragraphs)-1}",
                metadata={"paragraph_start": current_start_idx, "paragraph_end": len(paragraphs)-1}
            )
            chunks.append(chunk)

        return chunks