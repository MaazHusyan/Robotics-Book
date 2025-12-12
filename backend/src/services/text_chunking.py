import re
from typing import List, Tuple

from ..models.entities import ChunkType


class RoboticsTextChunker:
    """Specialized text chunker for robotics educational content."""

    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def _token_count(self, text: str) -> int:
        """Simple token count approximation."""
        # Approximate: 1 token ≈ 4 characters
        return len(text) // 4

    def _clean_content(self, content: str) -> str:
        """Clean MDX content for better chunking."""
        # Remove frontmatter
        if content.startswith("---"):
            try:
                end_idx = content[3:].find("---")
                if end_idx != -1:
                    content = content[end_idx + 6 :]  # Skip closing ---
            except:
                pass

        # Clean up excessive whitespace
        content = re.sub(r"\n{3,}", "\n\n", content)
        content = re.sub(r" {2,}", " ", content)

        return content.strip()

    def _identify_content_type(self, chunk: str) -> ChunkType:
        """Identify type of content in a chunk."""
        chunk_lower = chunk.lower()

        # Code blocks
        if re.search(r"```[\w]*\n.*?```", chunk, re.DOTALL):
            return ChunkType.CODE

        # Inline code or technical terms
        if chunk.count("`") >= 2:
            return ChunkType.CODE

        # Mathematical expressions
        if re.search(r"\$.*?\$", chunk) or re.search(r"\\\(.*?\\\)", chunk):
            return ChunkType.CODE

        # Lists
        list_patterns = [
            r"^\s*[-*+]\s+",  # Bullet lists
            r"^\s*\d+\.\s+",  # Numbered lists
            r"^\s*[a-zA-Z]\.\s+",  # Lettered lists
        ]
        if any(re.search(pattern, chunk, re.MULTILINE) for pattern in list_patterns):
            return ChunkType.LIST

        # Headers and sections
        if re.search(r"^#+\s+", chunk, re.MULTILINE):
            return ChunkType.SECTION

        # Definitions or key terms
        if re.search(r"\*\*.*?\*\s*:", chunk):  # **Bold Term**: definition
            return ChunkType.SECTION

        return ChunkType.PARAGRAPH

    def _simple_text_splitter(
        self, content: str, chunk_size: int = 800, overlap: int = 200
    ) -> List[str]:
        """Simple text splitter without external dependencies."""
        if len(content) <= chunk_size:
            return [content]

        chunks = []
        start = 0

        while start < len(content):
            # Find best break point
            end = start + chunk_size

            if end >= len(content):
                chunks.append(content[start:])
                break

            # Look for paragraph break
            paragraph_break = content.rfind("\n\n", start, end)
            if paragraph_break > start:
                end = paragraph_break + 2
            else:
                # Look for sentence break
                sentence_break = content.rfind(". ", start, end)
                if sentence_break > start:
                    end = sentence_break + 2
                else:
                    # Look for word break
                    word_break = content.rfind(" ", start, end)
                    if word_break > start:
                        end = word_break

            chunks.append(content[start:end].strip())

            # Next chunk with overlap
            start = max(start + 1, end - overlap)

        return [chunk for chunk in chunks if chunk.strip()]

    def _preserve_context(
        self, chunks: List[str], original_content: str
    ) -> List[Tuple[str, ChunkType]]:
        """Preserve context and identify chunk types."""
        result = []

        for i, chunk in enumerate(chunks):
            # Skip very short chunks
            if len(chunk.strip()) < 50:
                continue

            # Add context from previous/next chunks if needed
            if len(chunk) < 300 and i > 0:
                # Add some context from previous chunk
                prev_chunk = chunks[i - 1]
                context_overlap = min(100, len(prev_chunk))
                chunk = prev_chunk[-context_overlap:] + "\n\n" + chunk

            chunk_type = self._identify_content_type(chunk)
            result.append((chunk.strip(), chunk_type))

        return result

    def chunk_mdx_content(self, content: str) -> List[Tuple[str, ChunkType]]:
        """
        Chunk MDX content while preserving educational context.

        Returns:
            List of tuples: (chunk_text, chunk_type)
        """
        # Clean content first
        cleaned_content = self._clean_content(content)

        # Use simple text splitter
        chunks = self._simple_text_splitter(
            cleaned_content, self.chunk_size, self.chunk_overlap
        )
        chunks_with_types = self._preserve_context(chunks, cleaned_content)

        return chunks_with_types

    def get_chunk_statistics(self, chunks: List[Tuple[str, ChunkType]]) -> dict:
        """Get statistics about generated chunks."""
        if not chunks:
            return {}

        chunk_texts = [chunk[0] for chunk in chunks]
        chunk_types = [chunk[1] for chunk in chunks]

        token_counts = [self._token_count(chunk) for chunk in chunk_texts]

        return {
            "total_chunks": len(chunks),
            "avg_chunk_size": sum(len(chunk) for chunk in chunk_texts)
            / len(chunk_texts),
            "avg_token_count": sum(token_counts) / len(token_counts),
            "min_tokens": min(token_counts),
            "max_tokens": max(token_counts),
            "chunk_type_distribution": {
                chunk_type.value: chunk_types.count(chunk_type)
                for chunk_type in ChunkType
            },
        }


# Singleton instance
text_chunker = RoboticsTextChunker()
