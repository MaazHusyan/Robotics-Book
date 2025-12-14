---
id: 0001
title: rag-chatbot-database-spec
stage: spec
date: 2025-12-14
surface: cli
model: opencode
feature: 001-rag-chatbot
branch: 001-rag-chatbot
user: maaz
command: /sp.specify
labels: [database, rag-chatbot, specification]
links:
  spec: /specs/001-rag-chatbot/spec.md
  ticket: 
  adr: 
  pr: 
files:
  - path: specs/001-rag-chatbot/spec.md
    action: created comprehensive database specification
  - path: specs/001-rag-chatbot/checklists/requirements.md
    action: created quality checklist
tests:
  - type: specification-validation
    status: passed
    result: all requirements testable and measurable
---

## Prompt

rag-chatbot OBJECTIVE:
Create detailed Database Specification for RAG Chatbot.

PROJECT CONTEXT:
- Project: Physical and Humanoid Robotics Book (Docusaurus 3.9.2)
- Location: /home/maaz/Desktop/Robotics-Book
- Branch: chatbot-integ
- Backend: FastAPI
- Postgres: Neon Serverless (connection string in .env)
- Vector DB: Qdrant Cloud (Free Tier)
- LLM: Google Gemini (custom integration - not OpenAI)

TASK: Create comprehensive Database Specification

INSTRUCTIONS:

1. Navigate to project root:
   cd /home/maaz/Desktop/Robotics-Book

2. Use Speckit+ to create database specification:
   /sp. specify rag-chatbot-database

3. This will open a specification template for "rag-chatbot-database".
   Fill in all sections completely with the following details:

================================================================================
SECTION A: DATABASE OVERVIEW
================================================================================

Title: RAG Chatbot Database Specification
Purpose: Store book content, conversation history, and embedding metadata for 
         semantic search in RAG chatbot system
Scope: Neon Postgres (SQL) + Qdrant Cloud (Vector DB)
Dependencies: 
  - Neon Serverless Postgres instance (connection via .env NEON_DATABASE_URL)
  - Qdrant Cloud Free Tier (connection via .env QDRANT_API_KEY and QDRANT_URL)

================================================================================
SECTION B: NEON POSTGRES SCHEMA
================================================================================

Database Name: robotics_book (or from NEON_DATABASE_URL)

TABLE 1: books_content
Purpose: Store all book content from Docusaurus (chapters, sections, text)
Columns:
  - id (UUID PRIMARY KEY, auto-generated)
  - chapter_number (INTEGER, e.g., 1, 2, 3)
  - chapter_title (VARCHAR(255), e.g., "Introduction")
  - section_number (INTEGER, e.g., 1, 2, 3, 4, 5)
  - section_title (VARCHAR(255), e.g., "History and Evolution")
  - content_text (TEXT, actual MDX content)
  - content_hash (VARCHAR(64), MD5/SHA256 hash for deduplication)
  - source_file (VARCHAR(255), path like "docs/01-introduction/01-history.mdx")
  - word_count (INTEGER)
  - created_at (TIMESTAMP DEFAULT NOW())
  - updated_at (TIMESTAMP DEFAULT NOW())
  - is_active (BOOLEAN DEFAULT true, for soft deletes)

Indexes:
  - PRIMARY KEY on id
  - INDEX on chapter_number, section_number
  - FULL TEXT INDEX on content_text (for text search)
  - UNIQUE INDEX on content_hash (prevent duplicates)

TABLE 2: conversations
Purpose: Store chat history between users and chatbot
Columns:
  - id (UUID PRIMARY KEY, auto-generated)
  - session_id (VARCHAR(255), unique session identifier)
  - user_query (TEXT, user's question)
  - chatbot_response (TEXT, chatbot's answer)
  - selected_text (TEXT, NULL, user-selected text if applicable)
  - selected_text_section_id (UUID, FK to books_content.id if from a section)
  - gemini_model_used (VARCHAR(50), e.g., "gemini-2.0-flash")
  - tokens_used (INTEGER, for cost tracking)
  - response_time_ms (INTEGER, for performance monitoring)
  - confidence_score (FLOAT between 0-1, RAG relevance score)
  - is_helpful (BOOLEAN NULL, user feedback)
  - created_at (TIMESTAMP DEFAULT NOW())

Indexes:
  - PRIMARY KEY on id
  - INDEX on session_id (for retrieving conversation history)
  - INDEX on created_at (for time-based queries)
  - FOREIGN KEY session_id → sessions.id (see TABLE 4)
  - FOREIGN KEY selected_text_section_id → books_content.id

TABLE 3: embeddings_metadata
Purpose: Store metadata about which book sections have been embedded
Columns:
  - id (UUID PRIMARY KEY, auto-generated)
  - books_content_id (UUID FK, reference to books_content.id)
  - qdrant_vector_id (VARCHAR(255), vector ID in Qdrant)
  - embedding_model (VARCHAR(50), e.g., "text-embedding-3-small")
  - chunk_index (INTEGER, if content was chunked, which chunk)
  - chunk_size (INTEGER, number of tokens in chunk)
  - vector_dimension (INTEGER, e.g., 1536 for OpenAI embeddings)
  - metadata_json (JSONB, additional metadata)
  - created_at (TIMESTAMP DEFAULT NOW())
  - last_synced_at (TIMESTAMP, when this was last updated in Qdrant)
  - is_indexed (BOOLEAN DEFAULT false, confirmation flag)

Indexes:
  - PRIMARY KEY on id
  - FOREIGN KEY on books_content_id
  - INDEX on qdrant_vector_id (for lookups from vector results)
  - UNIQUE INDEX on (books_content_id, chunk_index)

TABLE 4: sessions
Purpose: Track user sessions for conversation continuity
Columns:
  - id (VARCHAR(255) PRIMARY KEY)
  - user_identifier (VARCHAR(255), could be IP, user-agent hash, or account ID)
  - created_at (TIMESTAMP DEFAULT NOW())
  - last_activity_at (TIMESTAMP DEFAULT NOW())
  - browser_info (JSONB, user agent, device info for analytics)
  - is_active (BOOLEAN DEFAULT true)
  - conversation_count (INTEGER DEFAULT 0)

Indexes:
  - PRIMARY KEY on id
  - INDEX on created_at (for session expiry cleanup)
  - INDEX on user_identifier

================================================================================
SECTION C: QDRANT CLOUD VECTOR COLLECTION
================================================================================

Collection Name: robotics_book_embeddings

Vector Configuration:
  - Vector Size: 768 or 1536 (depending on embedding model used)
  - Distance Metric: "cosine" (for semantic similarity)
  - Quantization: Disabled initially (enable if storage is an issue)

Payload Schema (metadata stored with vectors):
  - books_content_id (UUID): reference to Neon books_content.id
  - chapter_number (Integer): which chapter
  - section_number (Integer): which section
  - section_title (Text): section name for display
  - chapter_title (Text): chapter name
  - content_chunk (Text): actual text chunk
  - source_file (Text): where it came from
  - word_count (Integer): for statistics
  - created_at (Datetime): when indexed

Indexing Strategy:
  - Create HNSW index for fast similarity search
  - Set ef_construct = 200 for quality
  - Set ef = 200 for search precision

Search Performance Target:
  - Query time: < 200ms for typical searches
  - Return top-k: 3-5 most relevant documents

================================================================================
SECTION D: DATA FLOW & RELATIONSHIPS
================================================================================

1. INGESTION FLOW:
   Docusaurus MDX files
   → Extract content (chapter, section, text)
   → Store in books_content table (Neon)
   → Generate embeddings using Gemini or OpenAI API
   → Store vectors in Qdrant
   → Store metadata reference in embeddings_metadata table (Neon)

2. QUERY FLOW (RAG):
   User Question
   → Generate embedding for question
   → Search Qdrant vectors (semantic similarity)
   → Get top-k results with payload (books_content_id)
   → Fetch full content from Neon (books_content table)
   → Build context for Gemini model
   → Send to Gemini with RAG context
   → Return response + source attribution

3. CONVERSATION TRACKING:
   User input
   → Create/retrieve session_id
   → Store user query in conversations table
   → Execute RAG query
   → Store response in conversations table
   → Optional: store selected_text if user selected text

================================================================================
SECTION E: DATA VOLUME & SCALING ESTIMATES
================================================================================

Current Book Content:
  - Chapters: 3
  - Sections: 13
  - Approximate words: 6,500
  - Estimated tokens: ~8,000-10,000

Initial Neon Postgres:
  - books_content: ~13-20 rows (one per section)
  - conversations: ~0 initially, grows with usage
  - embeddings_metadata: ~13-20 rows (or more if chunked)
  - sessions: ~0 initially, grows with visitors

Qdrant Storage:
  - If using 1536-dim vectors: ~13-100 vectors initially
  - If chunked (512 tokens per chunk): ~20-40 vectors
  - Free tier limit: check Qdrant documentation

Scaling Strategy (if content grows):
  - Chunk large sections (> 1000 tokens) into 512-token chunks
  - Store chunks with chunk_index in embeddings_metadata
  - Neon auto-scaling handles query growth
  - Qdrant can be upgraded to paid tier if needed

================================================================================
SECTION F: MIGRATION & SETUP STEPS
================================================================================

When Implementation Begins:
1. Create tables in Neon using SQL migration script
2. Create Qdrant collection via API
3. Write ingestion script to:
   - Read MDX files from docs/
   - Parse chapters and sections
   - Insert into books_content
   - Generate embeddings
   - Insert into Qdrant
   - Store metadata in embeddings_metadata

Existing Data Handling:
  - All 13 existing chapters will be migrated
  - Content extracted from MDX files
  - No data loss during migration

================================================================================
SECTION G: SECURITY & COMPLIANCE
================================================================================

- Neon connection: Use SSL (sslmode=require in connection string)
- Credentials: Store in .env file (never commit to git)
- Data: User conversations are semi-persistent (consider retention policy)
- Privacy: No personal data stored (sessions use hashed identifiers)
- Compliance: No special compliance needed for educational content

================================================================================
SECTION H: PERFORMANCE REQUIREMENTS
================================================================================

- Book content retrieval: < 100ms
- Vector search (Qdrant): < 200ms
- Embedding generation: depends on model (Gemini typically < 1s)
- Total RAG response time: < 3-5 seconds
- Concurrent users: Neon and Qdrant Free Tier can handle 10-50 concurrent
- Storage: Neon free tier has sufficient storage for book content

================================================================================

4. After filling all sections, SAVE the specification file.

5. Create a Prompt History Record (PHR) for this work:
   /sp. phr specify rag-chatbot-database-spec
   
   Document in PHR:
   - Objective: Created comprehensive database specification for RAG chatbot
   - Decisions Made:
     * Four Neon tables: books_content, conversations, embeddings_metadata, sessions
     * One Qdrant collection: robotics_book_embeddings
     * Cosine distance metric for semantic similarity
     * Chunk strategy for large content sections
   - Rationale:
     * Neon for relational data (content, history) with ACID guarantees
     * Qdrant for vector similarity search (semantic RAG retrieval)
     * Four tables provide flexibility for conversations, metadata, and session tracking
   - Next Phase: PLAN phase to break down implementation
   - Status: Database specification complete and ready for implementation planning

6. Verify completion:
   - Specification file exists and is complete
   - PHR record is created
   - All sections have been filled with actual content (not templates)
   - Database design is clear and implementable

ACCEPTANCE CRITERIA:
✅ Complete Neon Postgres schema defined (4 tables, all columns, relationships)
✅ Qdrant collection structure fully specified
✅ Data flow diagrams/descriptions clear
✅ Performance requirements documented
✅ Migration strategy outlined
✅ PHR record documenting this specification created
✅ Specification is ready for PLAN phase

SUCCESS INDICATORS:
- Any developer can read spec and understand table structure
- SQL migration scripts can be written from this spec
- Qdrant collection can be created from this spec
- Relationships between Neon and Qdrant are clear
- Performance expectations are realistic for free tiers

## Response snapshot

Successfully created comprehensive RAG Chatbot Database Specification:
- Created feature branch 001-rag-chatbot
- Defined 4 user stories with priorities P1-P2
- Specified complete Neon Postgres schema with 4 tables
- Defined Qdrant Cloud collection configuration
- Documented data flow architecture and performance requirements
- Created quality checklist showing all validation criteria passed
- Specification is technology-agnostic and implementation-ready

## Outcome

- ✅ Impact: Comprehensive database specification created for RAG chatbot feature
- 🧪 Tests: Specification validation passed - all requirements testable and measurable
- 📁 Files: 2 files created (spec.md + requirements checklist)
- 🔁 Next prompts: Ready for planning phase (/sp.plan)
- 🧠 Reflection: Successfully balanced technical requirements with user experience needs

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS - All specification quality criteria met
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test planning workflow with new specification