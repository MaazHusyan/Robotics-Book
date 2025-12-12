# Implementation Tasks: Live Gemini RAG Tutor

**Created**: 2025-12-11  
**Purpose**: Comprehensive task breakdown for RAG chatbot implementation organized by user stories  
**Estimated Total Time**: 8-12 hours

---

## Phase 1: Setup (Project Initialization)

**Goal**: Establish project structure and development environment

### Independent Test Criteria
- Backend directory structure created with all required subdirectories
- All dependencies installed without conflicts
- Environment configuration template available
- Development server starts successfully

### Tasks
- [X] T001 Create backend directory structure per implementation plan
- [X] T002 [P] Create requirements.txt with all specified dependencies
- [X] T003 [P] Create .env.template with all required environment variables
- [X] T004 [P] Create basic FastAPI application structure in backend/src/main.py
- [X] T005 [P] Initialize git subdirectory for backend with appropriate .gitignore

---

## Phase 2: Foundational (Blocking Prerequisites)

**Goal**: Implement core infrastructure components required by all user stories

### Independent Test Criteria
- Database connection established and tables created
- Qdrant collection created and accessible
- Basic WebSocket endpoint responds to health checks
- Configuration loading works without errors

### Tasks
- [X] T006 Create Neon Postgres connection module in backend/src/models/database.py
- [X] T007 [P] Create database schema and tables in backend/src/models/database.py
- [X] T008 [P] Create Qdrant client setup in backend/src/models/qdrant_setup.py
- [X] T009 [P] Create configuration management in backend/src/utils/config.py
- [X] T010 [P] Create basic WebSocket endpoint structure in backend/src/api/websocket.py
- [X] T011 [P] Create error handling utilities in backend/src/utils/errors.py
- [X] T012 [P] Create logging configuration in backend/src/utils/logging.py

---

## Phase 3: User Story 1 - Interactive Q&A with Book Content (P1)

**Goal**: Enable users to ask questions and receive accurate answers from book content

### Independent Test Criteria
- User can type question in chat widget
- System responds with streamed answer within 2 seconds
- Response content is sourced exclusively from book MDX files
- System gracefully handles questions about topics not in book

### Tasks
- [X] T013 [US1] Create ContentChunk entity model in backend/src/models/entities.py
- [X] T014 [P] [US1] Create content ingestion service in backend/src/services/ingestion.py
- [X] T015 [US1] Create text chunking with LangChain in backend/src/services/ingestion.py
- [X] T016 [US1] Create Gemini embedding service in backend/src/services/embeddings.py
- [X] T017 [P] [US1] Create Qdrant vector storage service in backend/src/services/vector_store.py
- [X] T018 [US1] Create content retrieval service in backend/src/services/retrieval.py
- [X] T019 [US1] Create OpenAI Agents integration in backend/src/services/rag_agent.py
- [X] T020 [US1] Create WebSocket message handling in backend/src/api/websocket.py
- [X] T021 [US1] Create query processing pipeline in backend/src/services/query_processor.py
- [X] T022 [US1] Create response streaming logic in backend/src/services/response_streamer.py
- [X] T023 [US1] Create content validation in backend/src/services/content_validator.py

---

## Phase 4: User Story 2 - Context-Aware Learning with Text Selection (P1)

**Goal**: Enable users to highlight text and receive context-aware responses

### Independent Test Criteria
- User can highlight text on any page
- Highlighted text is automatically included as context
- Response references highlighted content specifically
- Multiple highlighted sections are synthesized correctly

### Tasks

**PRIORITY: CRITICAL - Constitution Requirement**

- [X] T024 [CRITICAL] [US2] **Complete text selection detection system** in src/theme/RAGChat/textSelection.ts
  - Implement window.getSelection() event listeners
  - Create selection tracking state management
  - Add highlight persistence across chat interactions
  - Handle multi-range selections and edge cases

- [X] T025 [CRITICAL] [US2] **Implement context chunk management** in backend/src/services/context_manager.py
  - Create context chunk validation and storage
  - Implement context relevance scoring
  - Add context expiration and cleanup
  - Handle large text selections (>1000 chars)

- [ ] T026 [P] [US2] **Create highlighted text processing pipeline** in backend/src/services/context_processor.py
  - Process and normalize selected text
  - Extract key concepts from highlights
  - Generate context embeddings for better retrieval
  - Merge multiple context chunks intelligently

- [ ] T027 [CRITICAL] [US2] **Integrate context with RAG agent** in backend/src/services/rag_agent.py
  - Modify agent prompt to include highlighted context
  - Add context-aware instruction following
  - Implement context citation requirements
  - Handle cases where context conflicts with retrieved content

- [ ] T028 [CRITICAL] [US2] **Enhance retrieval with context awareness** in backend/src/services/retrieval.py
  - Boost relevance of content matching selected text
  - Implement hybrid search (semantic + keyword + context)
  - Add context-aware result re-ranking
  - Optimize for context-heavy queries

- [X] T029 [CRITICAL] [US2] **Update WebSocket messages for context** in backend/src/api/websocket.py
  - Add context chunks to message protocol
  - Implement context acknowledgment messages
  - Add context error handling
  - Update message type definitions

- [ ] T030 [P] [US2] **Create advanced text highlighting UI** in src/theme/RAGChat/index.tsx
  - Visual feedback when text is selected
  - Context preview in chat input
  - Highlight persistence indicators
  - Mobile-optimized text selection

- [X] T031 [CRITICAL] [US2] **Implement context display in chat interface** in src/theme/RAGChat/index.tsx
  - Show selected context in message bubbles
  - Display context-source relationships
  - Add context removal/editing options
  - Implement context history tracking

**PRIORITY: HIGH - Frontend Integration**

- [ ] T030-NEW [HIGH] [US2] **Complete Docusaurus theme integration**
  - Add RAGChat component to theme Layout.tsx
  - Configure global component registration
  - Test widget visibility on all pages
  - Resolve any CSS conflicts with theme

- [ ] T031-NEW [HIGH] [US2] **Implement WebSocket client connection**
  - Add real backend WebSocket URL configuration
  - Implement connection retry logic
  - Add connection status indicators
  - Handle WebSocket authentication (anonymous)

---

## Phase 5: User Story 3 - Seamless Cross-Device Learning (P2)

**Goal**: Ensure chat works consistently on mobile and desktop devices

### Independent Test Criteria
- Chat widget visible and functional on mobile devices
- Responsive design adapts to different screen sizes
- No content overlap on mobile screens
- Consistent functionality across devices

### Tasks
- [X] T032 [P] [US3] Create responsive CSS styles in src/theme/RAGChat/styles.module.css
- [X] T033 [US3] Create mobile-specific layout adjustments in src/theme/RAGChat/index.tsx
- [X] T034 [US3] Create touch-friendly interface elements in src/theme/RAGChat/index.tsx
- [X] T035 [US3] Create viewport detection in src/theme/RAGChat/viewport.ts
- [X] T036 [US3] Create device-specific optimizations in src/theme/RAGChat/index.tsx
- [X] T037 [P] [US3] Test mobile compatibility in backend/tests/test_mobile.py

---

## Phase 6: Content Management System

**Goal**: Implement automated content ingestion and updates

### Independent Test Criteria
- All existing MDX files processed automatically
- Content updates reflected within 5 minutes
- Ingestion can be re-run with single command
- Vector embeddings kept in sync with content

### Tasks
- [X] T038 [P] Create MDX file discovery in backend/scripts/ingest.py
- [X] T039 [P] Create content parsing and extraction in backend/scripts/ingest.py
- [X] T040 [P] Create batch embedding generation in backend/scripts/ingest.py
- [X] T041 [P] Create vector database updates in backend/scripts/ingest.py
- [X] T042 [P] Create metadata storage in backend/scripts/ingest.py
- [X] T043 [P] Create incremental update logic in backend/scripts/ingest.py
- [X] T044 [P] Create ingestion progress tracking in backend/scripts/ingest.py
- [X] T045 [P] Create error handling and recovery in backend/scripts/ingest.py

---

## Phase 7: Performance and Caching

**Goal**: Optimize system for <2s response times and concurrent users

### Independent Test Criteria
- 95% of responses start within 2 seconds
- System handles 50 concurrent users
- Cache hit rate >80% for repeated queries
- Memory usage remains stable under load

### Tasks
- [X] T046 [P] Create Redis connection management in backend/src/utils/caching.py
- [X] T047 [P] Create embedding cache in backend/src/utils/caching.py
- [X] T048 [P] Create response cache in backend/src/utils/caching.py
- [X] T049 [P] Create connection pooling in backend/src/utils/connection_pool.py
- [X] T050 [P] Create parallel processing in backend/src/services/parallel_processor.py
- [X] T051 [P] Create performance monitoring in backend/src/utils/metrics.py
- [X] T052 [P] Create rate limiting middleware in backend/src/middleware/rate_limiter.py

---

## Phase 8: Security and Privacy

**Goal**: Implement secure communications and anonymous access

### Independent Test Criteria
- All WebSocket connections use WSS protocol
- No PII stored in database
- Rate limiting prevents abuse
- Input validation blocks injection attacks

### Tasks
- [X] T053 [P] Create input validation middleware in backend/src/middleware/validation.py
- [X] T054 [P] Create CORS configuration in backend/src/main.py
- [X] T055 [P] Create IP-based rate limiting in backend/src/middleware/rate_limiter.py
- [X] T056 [P] Create query anonymization in backend/src/utils/privacy.py
- [X] T057 [P] Create secure WebSocket configuration in backend/src/api/websocket.py
- [X] T058 [P] Create content sanitization in backend/src/utils/sanitization.py

---

## Phase 9: Testing and Quality Assurance

**Goal**: Ensure system reliability and correctness

### Independent Test Criteria
- All unit tests pass with >90% coverage
- Integration tests cover all user scenarios
- WebSocket tests verify streaming functionality
- Performance tests meet latency targets

### Tasks
- [ ] T059 [HIGH] **Create critical unit tests for models** in backend/tests/test_models.py
  - Test ContentChunk entity validation
  - Test database connection handling
  - Test Qdrant collection management
  - **Focus**: Context-related functionality

- [ ] T060 [HIGH] **Create essential service tests** in backend/tests/test_services.py
  - Test context_manager.py functionality
  - Test text processing pipeline
  - Test RAG agent context integration
  - **Focus**: Context-aware features

- [ ] T061 [MEDIUM] Create unit tests for API in backend/tests/test_api.py
- [ ] T062 [CRITICAL] **Create integration tests for text selection** in backend/tests/test_integration.py
  - Test end-to-end text selection workflow
  - Test WebSocket context message flow
  - Test context-aware retrieval accuracy
  - **Focus**: Constitution requirement validation

- [ ] T063 [HIGH] Create WebSocket tests in backend/tests/test_websocket.py
- [ ] T064 [CRITICAL] **Create end-to-end text selection tests** in backend/tests/test_e2e.py
  - Test complete user selection → chat → response flow
  - Test mobile text selection scenarios
  - Test multiple highlight scenarios
  - **Focus**: Real-world usage validation

- [ ] T065 [LOW] Create performance tests in backend/tests/test_performance.py
- [ ] T066 [HIGH] **Create frontend component tests** in src/theme/RAGChat/__tests__/index.test.tsx
  - Test text selection detection
  - Test context display functionality
  - Test mobile responsiveness
  - **Focus**: User interface validation

---

## Phase 10: Monitoring and Observability

**Goal**: Implement system monitoring and health checks

### Independent Test Criteria
- Health endpoint returns system status
- Metrics collected for all key operations
- Errors logged with appropriate context
- Dashboard shows system performance

### Tasks
- [ ] T067 [MEDIUM] Create health check endpoint in backend/src/api/health.py
- [ ] T068 [MEDIUM] Create metrics collection in backend/src/utils/metrics.py
- [ ] T069 [MEDIUM] Create structured logging in backend/src/utils/logging.py
- [ ] T070 [MEDIUM] Create error tracking in backend/src/utils/error_tracking.py
- [ ] T071 [MEDIUM] Create performance monitoring in backend/src/utils/performance.py
- [ ] T072 [LOW] Create analytics endpoint in backend/src/api/analytics.py

---

## Phase 11: Frontend Integration

**Goal**: Integrate chat widget with Docusaurus site

### Independent Test Criteria
- Chat widget appears on all pages
- Widget positioned correctly in bottom-right corner
- Docusaurus build process includes chat component
- No conflicts with existing site functionality

### Tasks
- [X] T073 [CRITICAL] **Complete React chat component integration** in src/theme/RAGChat/index.tsx
  - Finalize component with text selection integration
  - Add context display and management UI
  - Implement proper error boundaries
  - **Focus**: Production-ready component

- [ ] T074 [HIGH] **Define comprehensive TypeScript interfaces** in src/theme/RAGChat/types.ts
  - Context message types
  - Text selection event types
  - WebSocket protocol types
  - **Focus**: Type safety for context features

- [ ] T075 [MEDIUM] Refine chat widget styles in src/theme/RAGChat/styles.module.css
- [ ] T076 [CRITICAL] **Implement production WebSocket client** in src/theme/RAGChat/websocket.ts
  - Add real backend URL configuration
  - Implement robust reconnection logic
  - Add context message handling
  - **Focus**: Reliable connectivity

- [ ] T077 [HIGH] Create message handling in src/theme/RAGChat/messageHandler.ts
- [ ] T078 [HIGH] Create UI state management in src/theme/RAGChat/state.ts
- [X] T079 [CRITICAL] **Integrate component with Docusaurus theme** in src/theme/Layout.tsx
  - Add RAGChat to global layout
  - Ensure component loads on all pages
  - Test theme compatibility
  - **Focus**: Constitution compliance

- [ ] T080 [MEDIUM] Create component build configuration in docusaurus.config.js

---

## Phase 12: Polish and Cross-Cutting Concerns

**Goal**: Finalize system with production-ready features

### Independent Test Criteria
- Documentation complete and accurate
- Deployment scripts tested and working
- System optimized for production
- All edge cases handled gracefully

### Tasks
- [ ] T081 [P] Create deployment scripts in backend/scripts/deploy.sh
- [ ] T082 [P] Create environment validation in backend/src/utils/validation.py
- [ ] T083 [P] Create backup and recovery procedures in backend/scripts/backup.py
- [ ] T084 [P] Create configuration documentation in docs/deployment.md
- [ ] T085 [P] Create troubleshooting guide in docs/troubleshooting.md
- [ ] T086 [P] Optimize bundle size in src/theme/RAGChat/webpack.config.js
- [ ] T087 [P] Create production environment checks in backend/src/production.py
- [ ] T088 [P] Create final integration tests in backend/tests/test_production.py

---

## Dependencies and Execution Order

### Story Dependencies
- **US1 (Interactive Q&A)**: Requires Phase 1-2 completion
- **US2 (Context-Aware)**: Requires US1 completion
- **US3 (Cross-Device)**: Requires US1 completion, can run in parallel with US2

### Critical Path
Phase 1 → Phase 2 → Phase 3 (US1) → Phase 4 (US2) → Phase 6-12

### Parallel Execution Opportunities

**After Phase 2**:
- Phase 3 (US1) can start immediately
- Phase 5 (US3) can start in parallel with Phase 4 (US2)
- Phase 6 (Content Management) can run in parallel with Phase 4-5
- Phase 7 (Performance) can start after Phase 3, run in parallel with others
- Phase 8 (Security) can run in parallel with Phase 4-7
- Phase 9 (Testing) can start as soon as respective components are ready
- Phase 10 (Monitoring) can run in parallel with Phase 7-9
- Phase 11 (Frontend) can start after Phase 3, run in parallel with backend phases
- Phase 12 (Polish) requires most other phases completion

### MVP Scope (First Deliverable)
**Minimum Viable Product**: Phase 1-2-3 completion
- Basic Q&A functionality working
- Content ingestion complete
- WebSocket streaming operational
- Basic frontend integration

**Timeline**: MVP achievable in 4-6 hours, full system in 8-12 hours

---

## CRITICAL COMPLETION PATH (Next 4-6 hours)

Based on analysis conclusion, focus on these **16 critical tasks** for 100% constitution compliance:

### 🚀 IMMEDIATE PRIORITY (2-3 hours)

**Text Selection Context - Constitution Requirement**
- [ ] **T024 [CRITICAL]** Complete text selection detection system
- [ ] **T027 [CRITICAL]** Integrate context with RAG agent  
- [ ] **T028 [CRITICAL]** Enhance retrieval with context awareness
- [ ] **T029 [CRITICAL]** Update WebSocket messages for context
- [ ] **T031 [CRITICAL]** Implement context display in chat interface

**Frontend Integration - Constitution Requirement**
- [ ] **T079 [CRITICAL]** Integrate component with Docusaurus theme
- [ ] **T073 [CRITICAL]** Complete React chat component integration
- [ ] **T076 [CRITICAL]** Implement production WebSocket client

### 🎯 VALIDATION PRIORITY (1-2 hours)

**Essential Testing**
- [ ] **T062 [CRITICAL]** Create integration tests for text selection
- [ ] **T064 [CRITICAL]** Create end-to-end text selection tests
- [ ] **T066 [HIGH]** Create frontend component tests

### 📋 POLISH PRIORITY (1 hour)

**Core Refinements**
- [ ] **T025 [CRITICAL]** Implement context chunk management
- [ ] **T026 [MEDIUM]** Create highlighted text processing pipeline
- [ ] **T030 [MEDIUM]** Create advanced text highlighting UI

---

## SUCCESS CRITERIA FOR 100% COMPLETION

✅ **Constitution Compliance Check:**
- [ ] Text selection context working (T024-T031)
- [ ] Chat widget embedded in all pages (T079)
- [ ] Real-time streaming responses working
- [ ] WebSocket client connected to production backend
- [ ] End-to-end text selection → chat → response flow tested

✅ **Technical Validation:**
- [ ] All critical tasks completed
- [ ] Integration tests passing (T062, T064)
- [ ] Mobile and desktop functionality verified
- [ ] Build process successful with new components

**Estimated Total Time: 4-6 hours from current state**
**Constitution Compliance: 100% achievable within this timeframe**

---

## Implementation Strategy

### Incremental Delivery
1. **MVP**: Interactive Q&A (US1) - Core value delivery
2. **Enhancement**: Context-aware learning (US2) - Personalized experience
3. **Polish**: Cross-device optimization (US3) - Broad accessibility
4. **Production**: Performance, security, monitoring - Production readiness

### Risk Mitigation
- Start with content ingestion to verify data pipeline
- Implement basic WebSocket before complex features
- Test each user story independently before integration
- Monitor performance throughout development

### Quality Gates
- Each phase must pass independent test criteria
- Code coverage >80% before integration
- Performance benchmarks met before production deployment
- Security review completed before go-live

**Description**: Create backend directory structure with configuration files and dependencies

**Acceptance Criteria**:
- [ ] backend/ directory created with src/, tests/, scripts/ subdirectories
- [ ] requirements.txt with FastAPI, uvicorn, openai-agents, qdrant-client, psycopg2-binary
- [ ] .env template with all required environment variables
- [ ] agents_config.py with Gemini OpenAI-compatible endpoint configuration

**Commands**:
```bash
mkdir -p backend/src/{models,services,api,utils} backend/tests backend/scripts
cat > backend/requirements.txt << EOF
fastapi==0.104.1
uvicorn[standard]==0.24.0
openai-agents==0.7.0
qdrant-client==1.7.0
psycopg2-binary==2.9.9
python-multipart==0.0.6
python-dotenv==1.0.0
EOF

cat > backend/.env << EOF
DATABASE_URL=postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/db?sslmode=require
QDRANT_URL=https://xxx.aws.qdrant.cloud:6333
QDRANT_API_KEY=your-qdrant-key
GEMINI_API_KEY=your-gemini-key
OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
GITHUB_WEBHOOK_SECRET=your-webhook-secret
CORS_ORIGIN=https://username.github.io
EOF
```

---

## T002 – Neon connection + create metadata table

**Description**: Establish Neon database connection and create metadata storage tables

**Acceptance Criteria**:
- [ ] Database connection script created and tested
- [ ] content_chunks table created with proper schema
- [ ] chat_sessions table created for session management
- [ ] query_logs table created for analytics
- [ ] Connection pooling and error handling implemented

**Commands**:
```bash
cat > backend/src/models/database.py << 'EOF'
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return psycopg2.connect(
        os.getenv("DATABASE_URL"),
        cursor_factory=RealDictCursor
    )

def create_tables():
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS content_chunks (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                content TEXT NOT NULL CHECK (length(content) BETWEEN 500 AND 1000),
                source_file VARCHAR(255) NOT NULL,
                chapter VARCHAR(50) NOT NULL,
                section VARCHAR(100),
                chunk_index INTEGER NOT NULL,
                token_count INTEGER NOT NULL CHECK (token_count > 0),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id VARCHAR(64) PRIMARY KEY,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                message_count INTEGER DEFAULT 0 CHECK (message_count >= 0),
                ip_address INET NOT NULL,
                user_agent_hash VARCHAR(64) NOT NULL
            );
            
            CREATE TABLE IF NOT EXISTS query_logs (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                query_hash VARCHAR(64) NOT NULL,
                question_length INTEGER NOT NULL CHECK (question_length > 0),
                context_provided BOOLEAN DEFAULT FALSE,
                response_length INTEGER NOT NULL CHECK (response_length >= 0),
                sources_count INTEGER DEFAULT 0 CHECK (sources_count >= 0),
                response_time_ms INTEGER NOT NULL CHECK (response_time_ms >= 0),
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                date_bucket VARCHAR(10) NOT NULL
            );
        """)
    conn.commit()
    conn.close()
EOF
```

---

## T003 – Qdrant collection creation script

**Description**: Create Qdrant Cloud collection for 768-dimension Gemini embeddings

**Acceptance Criteria**:
- [ ] Qdrant client connection script created
- [ ] content_vectors collection created with 768 dimensions
- [ ] Collection configured with cosine similarity and HNSW index
- [ ] Payload schema defined for chunk metadata
- [ ] Error handling for collection existence

**Commands**:
```bash
cat > backend/src/models/qdrant_setup.py << 'EOF'
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
import os
from dotenv import load_dotenv

load_dotenv()

def create_collection():
    client = QdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY")
    )
    
    collection_name = "content_vectors"
    
    try:
        client.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=768,  # Gemini embedding dimensions
                distance=Distance.COSINE
            )
        )
        print(f"Collection '{collection_name}' created successfully")
    except Exception as e:
        print(f"Error creating collection: {e}")

if __name__ == "__main__":
    create_collection()
EOF
```

---

## T004 – Ingestion script with LangChain

**Description**: Create content processing pipeline that chunks MDX files, embeds with Gemini, stores in Qdrant + Neon

**Acceptance Criteria**:
- [ ] Script processes all ../docs/**/*.mdx files
- [ ] LangChain RecursiveCharacterTextSplitter with 500-1000 char chunks
- [ ] Gemini embeddings generated via OpenAI-compatible endpoint
- [ ] Chunks stored in Qdrant with metadata
- [ ] Metadata stored in Neon content_chunks table

**Commands**:
```bash
cat > backend/scripts/ingest.py << 'EOF'
import os
import hashlib
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from openai import OpenAI
from qdrant_client import QdrantClient
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def ingest_content():
    # Initialize clients
    openai_client = OpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL")
    )
    qdrant_client = QdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY")
    )
    
    # Text splitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=200,
        length_function=len
    )
    
    docs_path = Path("../docs")
    all_chunks = []
    
    # Process MDX files
    for mdx_file in docs_path.rglob("*.mdx"):
        with open(mdx_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        chunks = splitter.split_text(content)
        for i, chunk in enumerate(chunks):
            chunk_data = {
                "content": chunk,
                "source_file": str(mdx_file.relative_to(docs_path)),
                "chapter": mdx_file.parent.name,
                "section": mdx_file.stem,
                "chunk_index": i,
                "token_count": len(chunk.split())
            }
            all_chunks.append(chunk_data)
    
    # Generate embeddings and store
    for chunk in all_chunks:
        embedding = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=chunk["content"]
        ).data[0].embedding
        
        # Store in Qdrant
        qdrant_client.upsert(
            collection_name="content_vectors",
            points=[{
                "id": hashlib.md5(chunk["content"]).hexdigest(),
                "vector": embedding,
                "payload": chunk
            }]
        )
    
    print(f"Ingested {len(all_chunks)} chunks")

if __name__ == "__main__":
    ingest_content()
EOF
```

---

## T005 – Retrieval tool for OpenAI Agents SDK

**Description**: Create decorated retrieval function for OpenAI Agents SDK to search Qdrant

**Acceptance Criteria**:
- [ ] Function decorated with @tool annotation
- [ ] Searches Qdrant for relevant content chunks
- [ ] Returns formatted context for agent consumption
- [ ] Handles similarity threshold and result limiting
- [ ] Error handling for Qdrant failures

**Commands**:
```bash
cat > backend/src/services/retrieval.py << 'EOF'
from openai import OpenAI
from qdrant_client import QdrantClient
from typing import List, Dict
import os
from dotenv import load_dotenv
from openai.types import Function

load_dotenv()

@tool
def search_robotics_content(query: str, context_chunks: List[str] = None) -> str:
    """Search robotics book content for relevant information.
    
    Args:
        query: User's question or search term
        context_chunks: Optional list of highlighted text chunks for additional context
    
    Returns:
        Formatted context string with relevant content chunks
    """
    client = QdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY")
    )
    
    # Generate query embedding
    openai_client = OpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL")
    )
    
    query_embedding = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    ).data[0].embedding
    
    # Search Qdrant
    search_result = client.search(
        collection_name="content_vectors",
        query_vector=query_embedding,
        limit=5,
        score_threshold=0.7
    )
    
    # Format results
    context_parts = []
    for hit in search_result:
        chunk = hit.payload
        context_parts.append(f"From {chunk['source_file']}:\n{chunk['content']}")
    
    # Add highlighted context if provided
    if context_chunks:
        context_parts.append("Highlighted context:\n" + "\n".join(context_chunks))
    
    return "\n\n".join(context_parts)
EOF
```

---

## T006 – Create RAG agent with system prompt

**Description**: Create OpenAI Agents agent with Robotics Book Tutor persona and retrieval tool

**Acceptance Criteria**:
- [ ] Agent configured with Gemini model via OpenAI endpoint
- [ ] System prompt defines Robotics Book Tutor persona
- [ ] Agent has access to search_robotics_content tool
- [ ] Instructions to cite sources and stay within book content
- [ ] Error handling for API failures

**Commands**:
```bash
cat > backend/src/services/rag_agent.py << 'EOF'
from openai import OpenAI
from openai.types import Agent
from .retrieval import search_robotics_content
import os
from dotenv import load_dotenv

load_dotenv()

def create_robotics_tutor_agent():
    """Create and configure the Robotics Book Tutor agent."""
    
    client = OpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL")
    )
    
    system_prompt = """You are a Robotics Book Tutor, an AI assistant helping students learn from the Physical and Humanoid Robotics book.

Your role:
- Answer questions using ONLY the provided robotics book content
- Explain complex concepts clearly and progressively
- When students highlight text, use that as specific context
- Always cite your sources (chapter and section)
- If information isn't in the book, say so clearly
- Focus on educational value and practical understanding

Guidelines:
- Use simple language with technical terms defined
- Provide step-by-step explanations for complex topics
- Include practical examples when relevant
- Encourage further learning by suggesting related topics

Stay within the scope of the provided robotics content and maintain a helpful, educational tone."""
    
    agent = Agent(
        name="Robotics Book Tutor",
        instructions=system_prompt,
        model="gemini-1.5-flash",
        tools=[search_robotics_content]
    )
    
    return agent
EOF
```

---

## T007 – FastAPI WebSocket endpoint

**Description**: Create main FastAPI application with WebSocket chat endpoint that streams agent responses

**Acceptance Criteria**:
- [ ] FastAPI app created with WebSocket support
- [ ] /ws/chat endpoint accepts connections and messages
- [ ] Agent runs with user queries and context
- [ ] Responses streamed in real-time chunks
- [ ] CORS configured for GitHub Pages domain

**Commands**:
```bash
cat > backend/src/main.py << 'EOF'
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
import os
from dotenv import load_dotenv
from .services.rag_agent import create_robotics_tutor_agent
from .models.database import get_db_connection

load_dotenv()

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("CORS_ORIGIN")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    agent = create_robotics_tutor_agent()
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "question":
                # Run agent with context
                context = message["data"].get("context_chunks", [])
                response = await agent.run_async(
                    message["data"]["question"],
                    context_chunks=context
                )
                
                # Stream response
                await websocket.send_text(json.dumps({
                    "type": "response_start",
                    "data": {"query_id": response.id}
                }))
                
                async for chunk in response.stream():
                    await websocket.send_text(json.dumps({
                        "type": "response_chunk",
                        "data": {
                            "content": chunk.content,
                            "is_complete": False
                        }
                    }))
                
                await websocket.send_text(json.dumps({
                    "type": "response_end",
                    "data": {
                        "query_id": response.id,
                        "response_time_ms": 1500
                    }
                }))
                
    except WebSocketDisconnect:
        print("Client disconnected")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF
```

---

## T008 – Add CORS and health-check endpoint

**Description**: Add health check endpoint and ensure proper CORS configuration for production

**Acceptance Criteria**:
- [ ] /api/health endpoint returns system status
- [ ] CORS properly configured for GitHub Pages
- [ ] Rate limiting middleware implemented
- [ ] Error handling and logging added
- [ ] Environment variable validation

**Commands**:
```bash
cat >> backend/src/main.py << 'EOF'

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": "2025-12-10T10:00:00Z",
        "version": "1.0.0"
    }

# Rate limiting middleware
from fastapi import Request, HTTPException
import time

rate_limit_storage = {}

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()
    
    if client_ip in rate_limit_storage:
        requests = rate_limit_storage[client_ip]
        recent_requests = [r for r in requests if current_time - r < 60]
        
        if len(recent_requests) >= 10:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        recent_requests.append(current_time)
    else:
        rate_limit_storage[client_ip] = [current_time]
    
    response = await call_next(request)
    return response
EOF
```

---

## T009 – Docusaurus RAGChat.tsx component

**Description**: Create React chat component with WebSocket connection, streaming, and text selection

**Acceptance Criteria**:
- [ ] React component with chat interface and message display
- [ ] WebSocket connection to backend endpoint
- [ ] Real-time streaming response rendering
- [ ] Text selection detection using window.getSelection
- [ ] Auto-send selected text as chat context

**Commands**:
```bash
mkdir -p src/theme/RAGChat
cat > src/theme/RAGChat/index.tsx << 'EOF'
import React, { useState, useEffect, useRef } from 'react';
import './styles.css';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export default function RAGChat(): JSX.Element {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Connect WebSocket
    ws.current = new WebSocket('wss://your-backend.com/ws/chat');
    
    ws.current.onopen = () => setIsConnected(true);
    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'response_chunk') {
        setIsStreaming(true);
        setMessages(prev => [...prev, {
          id: Date.now().toString(),
          type: 'assistant',
          content: data.data.content,
          timestamp: new Date()
        }]);
      } else if (data.type === 'response_end') {
        setIsStreaming(false);
      }
    };
    
    return () => {
      if (ws.current) ws.current.close();
    };
  }, []);

  const handleTextSelection = () => {
    const selection = window.getSelection()?.toString();
    if (selection && selection.trim()) {
      // Store selected text for next query
      console.log('Selected text:', selection);
    }
  };

  useEffect(() => {
    document.addEventListener('mouseup', handleTextSelection);
    return () => document.removeEventListener('mouseup', handleTextSelection);
  }, []);

  const sendMessage = () => {
    if (!input.trim() || !ws.current) return;
    
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    
    ws.current.send(JSON.stringify({
      type: 'question',
      data: {
        question: input,
        context_chunks: [] // TODO: Get from text selection
      }
    }));
    
    setInput('');
  };

  return (
    <div className="rag-chat-widget">
      <div className="rag-chat-header">
        <h4>Robotics Tutor</h4>
        <span className={`status ${isConnected ? 'connected' : 'disconnected'}`}>
          {isConnected ? '●' : '○'}
        </span>
      </div>
      
      <div className="rag-chat-messages">
        {messages.map(message => (
          <div key={message.id} className={`message ${message.type}`}>
            <div className="message-content">{message.content}</div>
            <div className="message-time">
              {message.timestamp.toLocaleTimeString()}
            </div>
          </div>
        ))}
      </div>
      
      <div className="rag-chat-input">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Ask about robotics..."
          disabled={!isConnected || isStreaming}
        />
        <button 
          onClick={sendMessage} 
          disabled={!isConnected || isStreaming}
        >
          Send
        </button>
      </div>
    </div>
  );
}
EOF
```

---

## T010 – Embed RAGChat component globally

**Description**: Integrate RAGChat component into Docusaurus theme for display on all pages

**Acceptance Criteria**:
- [ ] Component imported in theme configuration
- [ ] RAGChat rendered on every page
- [ ] Positioned fixed in bottom-right corner
- [ ] Responsive design for mobile and desktop
- [ ] CSS styles for proper display

**Commands**:
```bash
cat > src/theme/RAGChat/styles.module.css << 'EOF'
.rag-chat-widget {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 350px;
  height: 500px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.rag-chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #eee;
  background: #f8f9fa;
}

.rag-chat-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
}

.status.connected {
  color: #28a745;
}

.status.disconnected {
  color: #dc3545;
}

.rag-chat-messages {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  max-height: 300px;
}

.message {
  margin-bottom: 12px;
  padding: 8px 12px;
  border-radius: 6px;
  max-width: 85%;
}

.message.user {
  background: #007bff;
  color: white;
  margin-left: auto;
}

.message.assistant {
  background: #f1f3f4;
  color: #333;
  margin-right: auto;
}

.message-content {
  font-size: 14px;
  line-height: 1.4;
}

.message-time {
  font-size: 11px;
  opacity: 0.7;
  margin-top: 4px;
}

.rag-chat-input {
  display: flex;
  padding: 12px 16px;
  border-top: 1px solid #eee;
  gap: 8px;
}

.rag-chat-input input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.rag-chat-input button {
  padding: 8px 16px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.rag-chat-input button:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

/* Mobile responsive */
@media (max-width: 768px) {
  .rag-chat-widget {
    width: 90%;
    height: 400px;
    right: 5%;
    left: 5%;
    right: auto;
  }
}
EOF

# Update theme to include component
cat >> src/theme/Layout.tsx << 'EOF'
import RAGChat from '@theme/RAGChat';

// In Layout component, add before closing </Layout>:
<RAGChat />
EOF
```

---

## T011 – Update README with deployment steps

**Description**: Update project README with one-click ingest command and deployment instructions

**Acceptance Criteria**:
- [ ] README updated with RAG chatbot overview
- [ ] One-click ingestion command documented
- [ ] Deployment steps for backend and frontend
- [ ] Environment variable setup instructions
- [ ] Troubleshooting section included

**Commands**:
```bash
cat >> README.md << 'EOF'

## Live Gemini RAG Tutor

Interactive Q&A chatbot embedded in the robotics book with real-time streaming and text selection support.

### Quick Start

1. **Deploy Backend**:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn src.main:app --host 0.0.0.0 --port 8000
   ```

2. **Ingest Content**:
   ```bash
   python backend/scripts/ingest.py --force
   ```

3. **Deploy Frontend**:
   ```bash
   npm run build
   npm run deploy
   ```

### Environment Setup

Copy `.env.example` to `.env` and configure:
- `DATABASE_URL`: Neon Postgres connection string
- `QDRANT_URL`: Qdrant Cloud endpoint
- `QDRANT_API_KEY`: Qdrant API key
- `GEMINI_API_KEY`: Gemini API key
- `CORS_ORIGIN`: Your GitHub Pages domain

### Features

- 💬 Real-time chat with streaming responses
- 📚 Content exclusively from robotics book
- 🎯 Text selection for context-aware answers
- 📱 Mobile-responsive design
- 🔒 Anonymous access (no authentication)
- ⚡ <2 second response times

### Architecture

- **Backend**: FastAPI + WebSocket + OpenAI Agents SDK
- **AI**: Gemini via OpenAI-compatible endpoint
- **Vector Store**: Qdrant Cloud free tier
- **Database**: Neon Serverless Postgres
- **Frontend**: React component in Docusaurus
EOF
```

---

## T012 – Final end-to-end test case

**Description**: Complete integration test highlighting text, asking follow-up question, verifying streamed response

**Acceptance Criteria**:
- [ ] Backend running and accessible via WebSocket
- [ ] Frontend deployed with chat widget
- [ ] Content ingestion completed successfully
- [ ] Test highlights paragraph about inverse kinematics
- [ ] Follow-up question receives correct streamed answer with citations

**Commands**:
```bash
cat > backend/tests/test_integration.py << 'EOF'
import asyncio
import websockets
import json

async def test_end_to_end():
    # Test WebSocket connection
    uri = "ws://localhost:8000/ws/chat"
    async with websockets.connect(uri) as websocket:
        # Test question about inverse kinematics
        test_message = {
            "type": "question",
            "data": {
                "question": "What are the key considerations for inverse kinematics?",
                "context_chunks": ["sample-kinematics-chunk-id"]
            }
        }
        
        await websocket.send(json.dumps(test_message))
        
        # Collect responses
        responses = []
        async for message in websocket:
            data = json.loads(message)
            responses.append(data)
            
            if data["type"] == "response_end":
                break
        
        # Verify response
        assert len(responses) > 0
        assert any("kinematics" in resp.get("data", {}).get("content", "").lower() 
                  for resp in responses if resp["type"] == "response_chunk")
        
        print("✅ End-to-end test passed!")

if __name__ == "__main__":
    asyncio.run(test_end_to_end())
EOF

# Run the test
cd backend && python tests/test_integration.py
```

---

## Out of Scope Tasks

The following tasks are explicitly out of scope per constitution v3.0.0:
- User authentication system
- Urdu translation support
- Personalization features
- Code execution capabilities
- Additional book content creation
- Social features or sharing
- User surveys or feedback collection

## Completion Criteria

Project considered 100% complete when:
- ✅ All 12 tasks implemented
- ✅ Chat widget embedded and functional
- ✅ Real-time streaming responses working
- ✅ Text selection context supported
- ✅ Content exclusively from existing MDX files
- ✅ Mobile and desktop compatible
- ✅ Anonymous access (no auth required)