---
id: 0001
title: rag-ingestion-spec
stage: spec
date: 2025-12-16
surface: cli
model: opencode
feature: 001-ingestion-pipeline
branch: 001-ingestion-pipeline
user: maaz
command: /sp.specify
labels: [spec, rag, ingestion-pipeline, docusaurus]
links:
  spec: /specs/001-ingestion-pipeline/spec.md
  ticket: 
  adr: 
  pr: 
files:
- specs/001-ingestion-pipeline/spec.md
- specs/001-ingestion-pipeline/checklists/requirements.md
tests:
- []

---

## Prompt

You are updating the project constitution at `.specify/memory/constitution.md`. This file is a TEMPLATE containing placeholder tokens in square brackets (e.g. `[PROJECT_NAME]`, `[PRINCIPLE_1_NAME]`). Your job is to (a) collect/derive concrete values, (b) fill the template precisely, and (c) propagate any amendments across dependent artifacts.

User Input:
```
Spec Identifier: spec-01-ingestion-pipeline
Spec Title: Complete RAG Ingestion Pipeline – Backend Project Setup, Content Extraction via Live Site Crawling, Chunking, Cohere Embeddings, and Qdrant Storage
Spec Description:
Implement a robust, production-ready ingestion pipeline in a dedicated uv-managed Python project located at backend/. Instead of reading local Markdown files directly, the pipeline must crawl the live published Docusaurus site (GitHub Pages) to extract clean text content, ensuring the ingested data exactly matches what users see in the browser.
Core Pipeline Functions (must implement exactly these):

get_all_urls()
Crawl the deployed Docusaurus site (base URL provided via config or CLI).
Extract all internal documentation page URLs (from sidebar navigation, sitemap, or recursive crawling).
Exclude non-content pages (e.g., blog, API docs if irrelevant, search page).
Return a clean list of absolute URLs.

extract_text_from_url(url)
Fetch the page HTML.
Extract and clean main content (remove headers, footers, sidebars, code blocks if too noisy, scripts, navigation).
Convert to clean readable text while preserving section hierarchy (headings → section titles).
Extract page title and breadcrumb/path metadata.

chunk_text(text, metadata)
Perform hierarchical chunking:
Split primarily by Markdown-like headings (H1 → H2 → H3).
Each chunk should include its full heading hierarchy in metadata.
Target chunk size: 600–800 tokens, with 150–200 token overlap.

Return list of chunks with unique IDs (e.g., hash of source URL + chunk index).

embed(texts)
Use Cohere API (default model: embed-english-v3.0, dimension 1024).
Batch embedding with input_type="search_document".
Configurable model via CLI/env.

create_collection()
Connect to Qdrant Cloud (Free Tier).
Create collection book_chunks if not exists.
Vector config: dimension=1024 (or auto-detect from model), distance=Cosine.

save_chunk_to_qdrant(chunks_with_embeddings)
Batch upsert points with:
id: unique string (e.g., md5(url + chunk_index))
vector: embedding
payload: { text, url, title, section_hierarchy, chunk_index, tokens }

Idempotent: overwrite existing points on re-run.

main() orchestration
Full end-to-end flow: get URLs → extract → chunk → embed → create collection → save.
Progress bars (tqdm), logging, retry on API failures.
Dry-run mode optional.


Inputs:

--site-url: Base URL of the deployed Docusaurus GitHub Pages site (required).
--collection-name: Qdrant collection (default: book_chunks).
--model: Cohere embedding model (default: embed-english-v3.0).
Environment variables: COHERE_API_KEY, QDRANT_URL, QDRANT_API_KEY.

Outputs:

Fully populated Qdrant collection with all book content.
Console log of ingested URLs, chunk count, success/failure summary.
Optional: export manifest JSON of ingested chunks.

Acceptance Criteria (must all pass):

Pipeline runs end-to-end without errors on a real deployed Docusaurus site.
All documentation pages are discovered and ingested.
Retrieved sample chunks via Qdrant search match expected content.
Embeddings dimension matches model (1024 for v3.0).
Re-running the script is safe and updates changed content.
Code is clean, modular, type-annotated, and well-documented.
uv project with locked dependencies.

Dependencies (add via uv add):

cohere
qdrant-client
beautifulsoup4 OR readability-lxml OR trafilatura (for clean extraction)
requests
tqdm
python-dotenv
tiktoken (for token counting)

Project Structure (create):
textbackend/
├── pyproject.toml
├── .env.example
├── src/
│   └── ingestion/
│       ├── __init__.py
│       ├── pipeline.py      # all functions above
│       └── main.py          # entry point
├── scripts/
│   └── ingest.py            # uv run scripts/ingest.py --site-url https://...
Output Requirements (your response):

Full step-by-step setup commands (uv init, uv add deps, etc.)
Complete pyproject.toml
Full code for all pipeline functions
CLI entry point using argparse or typer
Sample run command
Verification steps (e.g., how to check Qdrant dashboard)

This spec is foundational — all future specs (retrieval testing, agent, frontend) depend on this working pipeline.
2s 
```

[... full prompt continues with detailed instructions for spec creation, validation, and PHR creation ...]

## Response snapshot

Specification created successfully for RAG Ingestion Pipeline with:
- Branch: 001-ingestion-pipeline
- 3 user stories with independent test scenarios (P1-P3 priorities)
- 20 functional requirements across 4 categories
- 6 measurable success criteria
- Quality checklist completed and ready for planning phase
- PHR record created for traceability

## Outcome

- ✅ Impact: Foundation specification created for RAG chatbot ingestion pipeline
- 🧪 Tests: Quality checklist completed with all validation items passed
- 📁 Files: spec.md, requirements.md checklist created
- 🔁 Next prompts: /sp.plan for implementation planning
- 🧠 Reflection: Specification focuses on user outcomes without implementation details

## Evaluation notes (flywheel)

- Failure modes observed: None - all validation checks passed
- Graders run and results (PASS/FAIL): PASS - specification complete and ready
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed to planning phase with /sp.plan
