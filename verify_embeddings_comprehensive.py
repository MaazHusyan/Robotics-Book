#!/usr/bin/env python3
"""
Comprehensive verification script for your robotics book embeddings
"""
import os
import sys
from pathlib import Path
from qdrant_client import QdrantClient
from dotenv import load_dotenv

# Add backend/src to path
backend_src_path = Path(__file__).parent / 'backend' / 'src'
sys.path.insert(0, str(backend_src_path))

load_dotenv()

def verify_file_structure():
    """Check the file structure in docs directory"""
    print("🔍 ANALYZING FILE STRUCTURE")
    print("=" * 60)

    docs_path = Path("docs")

    if not docs_path.exists():
        print("❌ 'docs' directory doesn't exist!")
        return False

    print(f"📁 Docs directory found at: {docs_path.absolute()}")

    total_files = 0
    file_details = []

    for subdir in docs_path.iterdir():
        if subdir.is_dir():
            print(f"\n📂 Directory: {subdir.name}")
            files = list(subdir.glob("*.*"))
            for file in files:
                size = file.stat().st_size
                print(f"   📄 {file.name} ({file.suffix}) - Size: {size:,} bytes")
                file_details.append({
                    'path': file,
                    'name': file.name,
                    'suffix': file.suffix,
                    'size': size,
                    'directory': subdir.name
                })
                total_files += 1

    print(f"\n📊 Total files found: {total_files}")

    # Check for empty files
    empty_files = [f for f in file_details if f['size'] == 0]
    if empty_files:
        print(f"⚠️  Empty files found: {len(empty_files)}")
        for ef in empty_files:
            print(f"   - {ef['path']}")

    return file_details

def verify_embeddings_in_qdrant():
    """Verify embeddings stored in Qdrant"""
    print("\n🔍 ANALYZING QDRANT EMBEDDINGS")
    print("=" * 60)

    try:
        client = QdrantClient(
            url=os.getenv("QDRANT_URL", "http://localhost:6333"),
            api_key=os.getenv("QDRANT_API_KEY"),
            timeout=30
        )

        collection_name = os.getenv("QDRANT_COLLECTION_NAME", "robotics_book_embeddings")

        # Get collection info
        collection_info = client.get_collection(collection_name)
        total_points = collection_info.points_count

        print(f"📊 Qdrant Collection: {collection_name}")
        print(f"   Total embeddings stored: {total_points:,}")
        print(f"   Vector dimension: {collection_info.config.params.vectors.size}")

        if total_points == 0:
            print("❌ No embeddings found in Qdrant!")
            return None, []

        # Get ALL points to analyze
        all_points = []
        offset = 0
        while True:
            points_batch, next_offset = client.scroll(
                collection_name=collection_name,
                offset=offset,
                limit=1000,
                with_payload=True,
                with_vectors=False
            )
            all_points.extend(points_batch)
            if next_offset is None:
                break
            offset = next_offset

        print(f"   Retrieved all {len(all_points)} embeddings for analysis")

        # Analyze the embeddings
        empty_source_count = 0
        empty_location_count = 0
        unknown_heading_count = 0
        source_files = set()
        sample_chunks = []

        for i, point in enumerate(all_points):
            payload = point.payload

            # Check for empty source information
            if not payload.get('source_file') or payload.get('source_file') == '':
                empty_source_count += 1
            else:
                source_files.add(payload['source_file'])

            if not payload.get('source_location') or payload.get('source_location') == '':
                empty_location_count += 1

            # Check for "unknown" in chunk_id (which indicates heading detection failure)
            chunk_id = payload.get('chunk_id', '')
            if 'unknown' in chunk_id.lower():
                unknown_heading_count += 1

            # Store first few samples for detailed inspection
            if len(sample_chunks) < 5:
                sample_chunks.append({
                    'id': point.id,
                    'chunk_id': chunk_id,
                    'source_file': payload.get('source_file', ''),
                    'source_location': payload.get('source_location', ''),
                    'model': payload.get('model', ''),
                    'dimensionality': payload.get('dimensionality', 0),
                    'text_preview': payload.get('text', '')[:100] if 'text' in payload else 'N/A'
                })

        print(f"\n🔍 EMBEDDING ANALYSIS:")
        print(f"   Empty source_file: {empty_source_count}/{total_points} ({empty_source_count/total_points*100:.1f}%)")
        print(f"   Empty source_location: {empty_location_count}/{total_points} ({empty_location_count/total_points*100:.1f}%)")
        print(f"   Unknown headings in chunk_id: {unknown_heading_count}/{total_points} ({unknown_heading_count/total_points*100:.1f}%)")
        print(f"   Unique source files: {len(source_files)}")

        if source_files:
            print(f"   Source files found:")
            for sf in sorted(source_files):
                print(f"     - {sf}")

        print(f"\n📋 SAMPLE EMBEDDINGS (first 5):")
        for i, sample in enumerate(sample_chunks):
            print(f"   {i+1}. Chunk ID: {sample['chunk_id']}")
            print(f"      Source File: '{sample['source_file']}'")
            print(f"      Location: '{sample['source_location']}'")
            print(f"      Model: {sample['model']}")
            print(f"      Dimensionality: {sample['dimensionality']}")
            print(f"      Text Preview: '{sample['text_preview'][:50]}...'")
            print()

        return collection_info, all_points

    except Exception as e:
        print(f"❌ Error connecting to Qdrant: {str(e)}")
        return None, []

def analyze_mdx_files():
    """Analyze MDX files to understand the structure issue"""
    print("\n🔍 ANALYZING MDX FILE STRUCTURE")
    print("=" * 60)

    docs_path = Path("docs")
    mdx_files = list(docs_path.rglob("*.mdx"))

    print(f"Found {len(mdx_files)} MDX files")

    for file_path in mdx_files[:3]:  # Check first 3 files
        print(f"\n📄 Analyzing: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            lines = content.split('\n')
            print(f"   Total lines: {len(lines)}")

            # Look for frontmatter
            if lines and lines[0].strip() == '---':
                print("   ✓ Contains frontmatter (YAML between ---)")
                # Find end of frontmatter
                frontmatter_end = -1
                for i, line in enumerate(lines[1:], 1):
                    if line.strip() == '---':
                        frontmatter_end = i
                        break
                if frontmatter_end > 0:
                    print(f"   Frontmatter ends at line {frontmatter_end + 1}")
                    content_after_frontmatter = '\n'.join(lines[frontmatter_end + 1:])
                else:
                    content_after_frontmatter = content
            else:
                content_after_frontmatter = content

            # Look for headings
            import re
            heading_pattern = r'^(#{1,6})\s+(.+)$'
            headings = []
            for i, line in enumerate(content_after_frontmatter.split('\n'), 1):
                match = re.match(heading_pattern, line.strip())
                if match:
                    headings.append((i, match.group(1), match.group(2)))

            if headings:
                print(f"   Found {len(headings)} headings:")
                for line_num, level, title in headings[:3]:  # Show first 3
                    print(f"     L{line_num}: {level} {title}")
            else:
                print("   ⚠️  No markdown headings found!")
                print("   First few lines:")
                for i, line in enumerate(content.split('\n')[:10]):
                    print(f"     {i+1:2d}: {line[:50]}{'...' if len(line) > 50 else ''}")

        except Exception as e:
            print(f"   ❌ Error reading file: {str(e)}")

def identify_issues():
    """Identify the specific issues causing empty source info"""
    print("\n⚠️  IDENTIFIED ISSUES")
    print("=" * 60)

    print("1. 🎯 ISSUE: Frontmatter in MDX files")
    print("   - Your MDX files have YAML frontmatter between ---")
    print("   - The heading detection regex may not work properly with frontmatter")
    print("   - Solution: Skip frontmatter before looking for headings")

    print("\n2. 🔍 ISSUE: Regex pattern problem")
    print("   - Current pattern: r'#{1,3}\\s+([^\\n]+)'")
    print("   - May not match all heading formats in your files")

    print("\n3. 📁 ISSUE: Processing directory mismatch")
    print("   - Check if you're running the right script for your collection")
    print("   - Make sure you're processing the right Qdrant collection")

def main():
    """Main verification function"""
    print("🤖 ROBOTICS BOOK EMBEDDING VERIFICATION")
    print("=" * 60)

    # Verify file structure
    file_details = verify_file_structure()

    # Analyze MDX files
    analyze_mdx_files()

    # Verify embeddings in Qdrant
    collection_info, all_points = verify_embeddings_in_qdrant()

    # Identify issues
    identify_issues()

    print(f"\n✅ VERIFICATION COMPLETE")
    print(f"   - File structure: {'✅' if file_details else '❌'}")
    print(f"   - Qdrant connection: {'✅' if collection_info else '❌'}")
    print(f"   - MDX analysis: Completed")

    if all_points:
        total = len(all_points)
        empty_source = sum(1 for p in all_points if not p.payload.get('source_file'))
        empty_location = sum(1 for p in all_points if not p.payload.get('source_location'))
        unknown_heading = sum(1 for p in all_points if 'unknown' in p.payload.get('chunk_id', '').lower())

        print(f"\n📊 SUMMARY STATISTICS:")
        print(f"   Total embeddings: {total:,}")
        print(f"   Missing source_file: {empty_source:,} ({empty_source/total*100:.1f}%)")
        print(f"   Missing source_location: {empty_location:,} ({empty_location/total*100:.1f}%)")
        print(f"   Unknown headings: {unknown_heading:,} ({unknown_heading/total*100:.1f}%)")

if __name__ == "__main__":
    main()