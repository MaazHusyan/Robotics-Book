import os
import hashlib
import json
import time
from pathlib import Path
from typing import List, Dict, Any
import asyncio
import re

from ..models.entities import ContentChunk, ChunkType
from ..models.qdrant_setup import get_qdrant_client
from ..models.database import get_db_connection
from ..utils.config import get_config


class ContentIngestionService:
    def __init__(self):
        self.settings = get_config()

    def _token_count(self, text: str) -> int:
        """Simple token count approximation."""
        # Approximate: 1 token ≈ 4 characters
        return len(text) // 4

    def _extract_frontmatter(self, content: str) -> tuple[str, Dict[str, Any]]:
        """Extract frontmatter from MDX content."""
        lines = content.split("\n")
        if content.startswith("---"):
            try:
                end_idx = lines[1:].index("---") + 1
                frontmatter_lines = lines[1:end_idx]
                content_lines = lines[end_idx + 1 :]

                # Enhanced frontmatter parsing
                frontmatter = {}
                for line in frontmatter_lines:
                    if ":" in line and not line.strip().startswith("#"):
                        key, value = line.split(":", 1)
                        key = key.strip()
                        value = value.strip().strip("\"'")

                        # Handle array values
                        if (
                            isinstance(value, str)
                            and value.startswith("[")
                            and value.endswith("]")
                        ):
                            value = [
                                item.strip().strip("\"'")
                                for item in value[1:-1].split(",")
                            ]

                        # Handle boolean values
                        if isinstance(value, str) and value.lower() in (
                            "true",
                            "false",
                        ):
                            value = value.lower() == "true"

                        frontmatter[key] = value

                return "\n".join(content_lines), frontmatter
            except (ValueError, IndexError):
                pass
        return content, {}

    def _clean_content(self, content: str) -> str:
        """Clean and normalize content for better chunking."""
        # Remove excessive whitespace
        content = re.sub(r"\n\s*\n\s*\n", "\n\n", content)

        # Clean up MDX syntax that might interfere with embedding
        # Remove import statements
        content = re.sub(r"^import.*?$", "", content, flags=re.MULTILINE)

        # Remove export statements
        content = re.sub(r"^export.*?$", "", content, flags=re.MULTILINE)

        # Remove component references like <ComponentName />
        content = re.sub(r"<[A-Z][a-zA-Z]*[^>]*?/>", "", content)

        # Remove inline JSX expressions
        content = re.sub(r"\{[^}]*\}", "", content)

        # Normalize spacing
        content = re.sub(r" +", " ", content)
        content = re.sub(r"\n +", "\n", content)

        return content.strip()

    def _extract_semantic_sections(self, content: str) -> List[Dict[str, Any]]:
        """Extract semantic sections based on markdown structure."""
        sections = []
        lines = content.split("\n")
        current_section = None
        current_content = []

        for line in lines:
            # Check for headings
            if line.startswith("#"):
                # Save previous section
                if current_section:
                    current_section["content"] = "\n".join(current_content).strip()
                    if current_section["content"]:
                        sections.append(current_section)

                # Start new section
                level = len(line) - len(line.lstrip("#"))
                title = line.lstrip("#").strip()
                current_section = {"level": level, "title": title, "content": []}
                current_content = []
            else:
                current_content.append(line)

        # Save last section
        if current_section:
            current_section["content"] = "\n".join(current_content).strip()
            if current_section["content"]:
                sections.append(current_section)

        return sections

    def _extract_code_blocks(self, content: str) -> List[Dict[str, Any]]:
        """Extract code blocks with language detection."""
        code_blocks = []
        pattern = r"```(\w+)?\n(.*?)\n```"
        matches = re.finditer(pattern, content, re.DOTALL)

        for match in matches:
            language = match.group(1) or "text"
            code = match.group(2).strip()
            if code:
                code_blocks.append(
                    {"language": language, "code": code, "full_match": match.group(0)}
                )

        return code_blocks

    def _extract_tables(self, content: str) -> List[str]:
        """Extract markdown tables."""
        tables = []
        lines = content.split("\n")
        i = 0

        while i < len(lines):
            line = lines[i].strip()
            if "|" in line and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if "|" in next_line and "-" in next_line:
                    # Found table start
                    table_lines = []
                    while i < len(lines) and "|" in lines[i]:
                        table_lines.append(lines[i])
                        i += 1
                    tables.append("\n".join(table_lines))
                else:
                    i += 1
            else:
                i += 1

        return tables

    def _extract_lists(self, content: str) -> List[str]:
        """Extract markdown lists."""
        lists = []
        lines = content.split("\n")
        current_list = []
        in_list = False

        for line in lines:
            stripped = line.strip()
            if stripped.startswith(("-", "*", "+")) or re.match(r"^\d+\.", stripped):
                if not in_list:
                    in_list = True
                    current_list = []
                current_list.append(line)
            elif in_list and not stripped:
                current_list.append(line)
            elif in_list:
                # End of list
                if current_list:
                    lists.append("\n".join(current_list))
                current_list = []
                in_list = False

        # Add final list if exists
        if in_list and current_list:
            lists.append("\n".join(current_list))

        return lists

    def _create_semantic_chunks(
        self,
        content: str,
        sections: List[Dict[str, Any]],
        code_blocks: List[Dict[str, Any]],
        tables: List[str],
        lists: List[str],
        frontmatter: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Create chunks based on semantic structure."""
        chunks = []

        # Add title and description from frontmatter as first chunk if available
        if frontmatter.get("title") or frontmatter.get("description"):
            title_chunk = {
                "content": f"Title: {frontmatter.get('title', '')}\n\nDescription: {frontmatter.get('description', '')}",
                "type": ChunkType.SECTION,
                "metadata": {"source": "frontmatter"},
            }
            chunks.append(title_chunk)

        # Process sections with headings
        for section in sections:
            if section["content"]:
                section_chunk = {
                    "content": f"## {section['title']}\n\n{section['content']}",
                    "type": ChunkType.SECTION,
                    "metadata": {"level": section["level"], "title": section["title"]},
                }
                chunks.append(section_chunk)

        # Process code blocks separately
        for code_block in code_blocks:
            code_chunk = {
                "content": f"Code example ({code_block['language']}):\n\n```{code_block['language']}\n{code_block['code']}\n```",
                "type": ChunkType.CODE,
                "metadata": {"language": code_block["language"]},
            }
            chunks.append(code_chunk)

        # Process tables
        for table in tables:
            table_chunk = {
                "content": f"Table:\n\n{table}",
                "type": ChunkType.SECTION,
                "metadata": {"type": "table"},
            }
            chunks.append(table_chunk)

        # Process lists
        for list_content in lists:
            list_chunk = {
                "content": list_content,
                "type": ChunkType.LIST,
                "metadata": {"type": "list"},
            }
            chunks.append(list_chunk)

        # If no semantic chunks found, fall back to simple text splitting
        if not chunks:
            simple_chunks = self._simple_text_splitter(content)
            for chunk_text in simple_chunks:
                chunks.append(
                    {
                        "content": chunk_text,
                        "type": self._determine_chunk_type(chunk_text),
                        "metadata": {"method": "simple_split"},
                    }
                )

        return chunks

    def _determine_chunk_type(self, content: str) -> ChunkType:
        """Determine chunk type based on content."""
        content_lower = content.lower().strip()

        # Code blocks
        if "```" in content or content.startswith("    "):
            return ChunkType.CODE

        # Lists
        lines = [line.strip() for line in content.split("\n") if line.strip()]
        if lines and any(
            line.startswith(("-", "*", "+", "1.", "2.", "3.")) for line in lines
        ):
            return ChunkType.LIST

        # Sections (headings)
        if any(line.startswith("#") for line in lines):
            return ChunkType.SECTION

        return ChunkType.PARAGRAPH

    def _simple_text_splitter(
        self, content: str, chunk_size: int = 800, overlap: int = 200
    ) -> List[str]:
        """Simple text splitter without langchain dependency."""
        if len(content) <= chunk_size:
            return [content]

        chunks = []
        start = 0

        while start < len(content):
            # Find the best break point
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

    async def process_mdx_file(self, file_path: Path) -> List[ContentChunk]:
        """Process a single MDX file and return content chunks."""
        try:
            # Read file content
            with open(file_path, "r", encoding="utf-8") as f:
                raw_content = f.read()

            # Extract frontmatter
            content, frontmatter = self._extract_frontmatter(raw_content)

            # Clean content for better processing
            cleaned_content = self._clean_content(content)

            # Extract semantic elements for better chunking
            sections = self._extract_semantic_sections(cleaned_content)
            code_blocks = self._extract_code_blocks(cleaned_content)
            tables = self._extract_tables(cleaned_content)
            lists = self._extract_lists(cleaned_content)

            # Create enhanced chunks based on semantic structure
            chunks = self._create_semantic_chunks(
                cleaned_content, sections, code_blocks, tables, lists, frontmatter
            )

            # Create ContentChunk objects
            content_chunks = []
            relative_path = str(file_path.relative_to(Path(self.settings.DOCS_ROOT)))
            chapter = file_path.parent.name
            section = file_path.stem

            for i, chunk_data in enumerate(chunks):
                chunk_text = chunk_data["content"]
                if len(chunk_text.strip()) < 50:  # Skip very short chunks
                    continue

                chunk = ContentChunk(
                    content=chunk_text,
                    source_file=relative_path,
                    chapter=chapter,
                    section=section,
                    chunk_index=i,
                    chunk_type=chunk_data.get(
                        "type", self._determine_chunk_type(chunk_text)
                    ),
                    token_count=self._token_count(chunk_text),
                    embedding_id=None,
                )
                content_chunks.append(chunk)

            return content_chunks

        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            return []

    async def discover_mdx_files(self, docs_path: str) -> List[Path]:
        """Discover all MDX files in docs directory."""
        docs_root = Path(docs_path)
        if not docs_root.exists():
            raise FileNotFoundError(f"Docs directory not found: {docs_path}")

        mdx_files = list(docs_root.rglob("*.mdx"))
        print(f"Found {len(mdx_files)} MDX files")
        return mdx_files

    async def ingest_all_content(self, force: bool = False) -> Dict[str, int]:
        """Ingest all content from MDX files."""
        print("Starting content ingestion...")

        # Discover files
        mdx_files = await self.discover_mdx_files(self.settings.DOCS_ROOT)

        all_chunks = []
        for file_path in mdx_files:
            print(f"Processing: {file_path}")
            chunks = await self.process_mdx_file(file_path)
            all_chunks.extend(chunks)

        print(f"Created {len(all_chunks)} content chunks")

        # Store in database
        await self._store_chunks_in_db(all_chunks, force)

        # Generate embeddings and store in Qdrant
        await self._store_chunks_in_qdrant(all_chunks)

        return {"files_processed": len(mdx_files), "chunks_created": len(all_chunks)}

    async def _store_chunks_in_db(
        self, chunks: List[ContentChunk], force: bool = False
    ):
        """Store content chunks in PostgreSQL database with enhanced metadata."""
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                if force:
                    cur.execute("DELETE FROM content_chunks")
                    print("Cleared existing content chunks")

                # Prepare batch insert for better performance
                batch_data = []
                for chunk in chunks:
                    # Generate content hash for deduplication
                    content_hash = hashlib.md5(chunk.content.encode()).hexdigest()

                    batch_data.append(
                        (
                            chunk.id,
                            chunk.content,
                            chunk.source_file,
                            chunk.chapter,
                            chunk.section,
                            chunk.chunk_index,
                            chunk.chunk_type.value,
                            chunk.token_count,
                            chunk.embedding_id,
                            content_hash,
                            len(chunk.content),  # content_length
                            len(chunk.content.split()),  # word_count
                            chunk.created_at,
                            chunk.updated_at,
                        )
                    )

                # Batch insert with UPSERT
                insert_query = """
                    INSERT INTO content_chunks 
                    (id, content, source_file, chapter, section, chunk_index, 
                     chunk_type, token_count, embedding_id, content_hash,
                     content_length, word_count, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        content = EXCLUDED.content,
                        chunk_type = EXCLUDED.chunk_type,
                        token_count = EXCLUDED.token_count,
                        embedding_id = EXCLUDED.embedding_id,
                        content_hash = EXCLUDED.content_hash,
                        content_length = EXCLUDED.content_length,
                        word_count = EXCLUDED.word_count,
                        updated_at = EXCLUDED.updated_at
                """

                cur.executemany(insert_query, batch_data)
                conn.commit()
                print(f"Stored {len(chunks)} chunks in database")

                # Update statistics
                await self._update_database_stats(cur)

        except Exception as e:
            conn.rollback()
            print(f"Error storing chunks in database: {e}")
            raise
        finally:
            conn.close()

    async def _update_database_stats(self, cursor):
        """Update database statistics and indexes."""
        try:
            # Update chapter statistics
            cursor.execute("""
                INSERT INTO chapter_stats (chapter, chunk_count, total_tokens, last_updated)
                SELECT 
                    chapter,
                    COUNT(*) as chunk_count,
                    SUM(token_count) as total_tokens,
                    NOW() as last_updated
                FROM content_chunks 
                GROUP BY chapter
                ON CONFLICT (chapter) DO UPDATE SET
                    chunk_count = EXCLUDED.chunk_count,
                    total_tokens = EXCLUDED.total_tokens,
                    last_updated = EXCLUDED.last_updated
            """)

            # Update file statistics
            cursor.execute("""
                INSERT INTO file_stats (source_file, chunk_count, total_tokens, last_updated)
                SELECT 
                    source_file,
                    COUNT(*) as chunk_count,
                    SUM(token_count) as total_tokens,
                    NOW() as last_updated
                FROM content_chunks 
                GROUP BY source_file
                ON CONFLICT (source_file) DO UPDATE SET
                    chunk_count = EXCLUDED.chunk_count,
                    total_tokens = EXCLUDED.total_tokens,
                    last_updated = EXCLUDED.last_updated
            """)

            print("Updated database statistics")

        except Exception as e:
            print(f"Error updating database stats: {e}")

    async def get_database_stats(self) -> Dict[str, Any]:
        """Get comprehensive database statistics."""
        conn = get_db_connection()
        try:
            stats = {}

            with conn.cursor() as cur:
                # Basic counts
                cur.execute("SELECT COUNT(*) FROM content_chunks")
                stats["total_chunks"] = cur.fetchone()[0]

                cur.execute("SELECT COUNT(DISTINCT chapter) FROM content_chunks")
                stats["total_chapters"] = cur.fetchone()[0]

                cur.execute("SELECT COUNT(DISTINCT source_file) FROM content_chunks")
                stats["total_files"] = cur.fetchone()[0]

                # Token statistics
                cur.execute(
                    "SELECT SUM(token_count), AVG(token_count), MAX(token_count), MIN(token_count) FROM content_chunks"
                )
                token_stats = cur.fetchone()
                stats["token_stats"] = {
                    "total": token_stats[0] or 0,
                    "average": round(token_stats[1] or 0, 1),
                    "max": token_stats[2] or 0,
                    "min": token_stats[3] or 0,
                }

                # Chunk type distribution
                cur.execute(
                    "SELECT chunk_type, COUNT(*) FROM content_chunks GROUP BY chunk_type"
                )
                stats["chunk_types"] = dict(cur.fetchall())

                # Recent activity
                cur.execute("SELECT MAX(updated_at) FROM content_chunks")
                stats["last_updated"] = cur.fetchone()[0]

            return stats

        except Exception as e:
            print(f"Error getting database stats: {e}")
            return {"error": str(e)}
        finally:
            conn.close()

    async def cleanup_orphaned_metadata(self) -> Dict[str, Any]:
        """Clean up orphaned metadata entries."""
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                # Find chunks without embeddings
                cur.execute("""
                    SELECT id, source_file FROM content_chunks 
                    WHERE embedding_id IS NULL OR embedding_id = ''
                """)
                orphaned_chunks = cur.fetchall()

                # Find chunks with invalid embedding IDs (not in vector store)
                # This would require checking against Qdrant, for now just report
                stats = {
                    "chunks_without_embeddings": len(orphaned_chunks),
                    "orphaned_details": [
                        {"id": row[0], "file": row[1]} for row in orphaned_chunks[:10]
                    ],  # Limit to first 10 for reporting
                }

                print(f"Found {len(orphaned_chunks)} chunks without embeddings")
                return stats

        except Exception as e:
            print(f"Error cleaning up orphaned metadata: {e}")
            return {"error": str(e)}
        finally:
            conn.close()

    async def detect_file_changes(self, docs_path: str) -> Dict[str, Any]:
        """Detect which files have changed since last ingestion."""
        docs_root = Path(docs_path)
        changes = {
            "new_files": [],
            "modified_files": [],
            "deleted_files": [],
            "unchanged_files": [],
        }

        try:
            # Get file modification tracking from database
            conn = get_db_connection()
            try:
                with conn.cursor() as cur:
                    # Create file tracking table if not exists
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS file_tracking (
                            file_path VARCHAR(255) PRIMARY KEY,
                            file_hash VARCHAR(64) NOT NULL,
                            last_modified TIMESTAMP WITH TIME ZONE,
                            last_ingested TIMESTAMP WITH TIME ZONE,
                            file_size INTEGER
                        )
                    """)

                    # Get existing file records
                    cur.execute(
                        "SELECT file_path, file_hash, last_modified, file_size FROM file_tracking"
                    )
                    existing_files = {
                        row[0]: {"hash": row[1], "modified": row[2], "size": row[3]}
                        for row in cur.fetchall()
                    }
            finally:
                conn.close()

            # Check all MDX files
            current_files = set()
            for mdx_file in docs_root.rglob("*.mdx"):
                relative_path = str(mdx_file.relative_to(docs_root))
                current_files.add(relative_path)

                try:
                    # Calculate file hash and stats
                    file_content = mdx_file.read_text(encoding="utf-8")
                    file_hash = hashlib.md5(file_content.encode()).hexdigest()
                    file_size = mdx_file.stat().st_size
                    last_modified = datetime.fromtimestamp(mdx_file.stat().st_mtime)

                    if relative_path not in existing_files:
                        # New file
                        changes["new_files"].append(
                            {
                                "path": relative_path,
                                "hash": file_hash,
                                "size": file_size,
                                "modified": last_modified,
                            }
                        )
                    else:
                        existing = existing_files[relative_path]
                        if (
                            existing["hash"] != file_hash
                            or existing["size"] != file_size
                        ):
                            # Modified file
                            changes["modified_files"].append(
                                {
                                    "path": relative_path,
                                    "hash": file_hash,
                                    "size": file_size,
                                    "modified": last_modified,
                                    "previous_hash": existing["hash"],
                                }
                            )
                        else:
                            # Unchanged file
                            changes["unchanged_files"].append(relative_path)

                except Exception as e:
                    print(f"Error processing file {relative_path}: {e}")

            # Find deleted files
            for existing_path in existing_files:
                if existing_path not in current_files:
                    changes["deleted_files"].append(existing_path)

            return changes

        except Exception as e:
            print(f"Error detecting file changes: {e}")
            return {"error": str(e)}

    async def incremental_ingestion(self, docs_path: str) -> Dict[str, Any]:
        """Perform incremental ingestion based on file changes."""
        print("Starting incremental ingestion...")

        try:
            # Detect changes
            changes = await self.detect_file_changes(docs_path)

            if "error" in changes:
                return changes

            files_to_process = changes["new_files"] + changes["modified_files"]

            if not files_to_process:
                print("No files to process - everything is up to date")
                return {
                    "success": True,
                    "files_processed": 0,
                    "chunks_created": 0,
                    "changes_detected": changes,
                }

            print(f"Found {len(files_to_process)} files to process:")
            print(f"  New files: {len(changes['new_files'])}")
            print(f"  Modified files: {len(changes['modified_files'])}")
            print(f"  Deleted files: {len(changes['deleted_files'])}")

            # Process changed files
            docs_root = Path(docs_path)
            all_chunks = []

            for file_info in files_to_process:
                file_path = docs_root / file_info["path"]
                try:
                    chunks = await self.process_mdx_file(file_path)
                    all_chunks.extend(chunks)

                    # Update file tracking
                    await self._update_file_tracking(file_info)

                except Exception as e:
                    print(f"Error processing {file_info['path']}: {e}")

            # Handle deleted files
            if changes["deleted_files"]:
                await self._handle_deleted_files(changes["deleted_files"])

            # Store new chunks
            if all_chunks:
                await self._store_chunks_in_db(all_chunks, force=False)
                await self._store_chunks_in_qdrant(all_chunks)

            return {
                "success": True,
                "files_processed": len(files_to_process),
                "chunks_created": len(all_chunks),
                "changes_detected": changes,
            }

        except Exception as e:
            print(f"Error during incremental ingestion: {e}")
            return {"success": False, "error": str(e)}

    async def _update_file_tracking(self, file_info: Dict[str, Any]):
        """Update file tracking information."""
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO file_tracking 
                    (file_path, file_hash, last_modified, last_ingested, file_size)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (file_path) DO UPDATE SET
                        file_hash = EXCLUDED.file_hash,
                        last_modified = EXCLUDED.last_modified,
                        last_ingested = EXCLUDED.last_ingested,
                        file_size = EXCLUDED.file_size
                """,
                    (
                        file_info["path"],
                        file_info["hash"],
                        file_info["modified"],
                        datetime.now(),
                        file_info["size"],
                    ),
                )
                conn.commit()
        except Exception as e:
            print(f"Error updating file tracking: {e}")
            conn.rollback()
        finally:
            conn.close()

    async def _handle_deleted_files(self, deleted_files: List[str]):
        """Handle files that have been deleted."""
        conn = get_db_connection()
        qdrant_client = get_qdrant_client()

        try:
            # Get chunks for deleted files
            with conn.cursor() as cur:
                placeholders = ",".join(["%s"] * len(deleted_files))
                cur.execute(
                    f"""
                    SELECT embedding_id FROM content_chunks 
                    WHERE source_file IN ({placeholders})
                """,
                    deleted_files,
                )
                embedding_ids = [row[0] for row in cur.fetchall() if row[0]]

                # Delete from database
                cur.execute(
                    f"""
                    DELETE FROM content_chunks 
                    WHERE source_file IN ({placeholders})
                """,
                    deleted_files,
                )

                # Delete from file tracking
                cur.execute(
                    f"""
                    DELETE FROM file_tracking 
                    WHERE file_path IN ({placeholders})
                """,
                    deleted_files,
                )

                conn.commit()

            # Delete from vector store
            if embedding_ids:
                qdrant_client.delete(
                    collection_name=self.settings.QDRANT_COLLECTION,
                    points_selector=embedding_ids,
                )
                print(f"Deleted {len(embedding_ids)} vectors for removed files")

            print(f"Handled {len(deleted_files)} deleted files")

        except Exception as e:
            print(f"Error handling deleted files: {e}")
            if conn:
                conn.rollback()
        finally:
            conn.close()


# Singleton instance
ingestion_service = ContentIngestionService()
