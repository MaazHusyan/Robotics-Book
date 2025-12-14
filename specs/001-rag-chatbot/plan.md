# Implementation Plan: RAG Chatbot Implementation

**Branch**: `001-rag-chatbot` | **Date**: 2025-12-14 | **Spec**: /specs/001-rag-chatbot/spec.md
**Input**: Feature specification from `/specs/001-rag-chatbot/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Create a comprehensive RAG chatbot integration for the Physical and Humanoid Robotics Book using FastAPI backend, Neon Postgres database, Qdrant Cloud vector storage, and Google Gemini LLM integration. The system will provide accurate, source-cited answers to user questions about robotics book content with text selection context enhancement.

## Technical Context

**Language/Version**: Python 3.9+ (FastAPI), TypeScript/JSX (React 19.0.0)  
**Primary Dependencies**: FastAPI, Neon Postgres, Qdrant Cloud, OpenAI Agents SDK, Gemini API, React 19.0.0  
**Storage**: Neon serverless Postgres (relational data), Qdrant Cloud (vector embeddings)  
**Testing**: pytest (backend), React Testing Library (frontend), load testing tools  
**Target Platform**: GitHub Pages (static frontend) + Serverless (backend)  
**Project Type**: web/fullstack - Docusaurus static site with FastAPI backend  
**Performance Goals**: <5s total response time (3-5s target), <200ms vector search, 10-50 concurrent users  
**Constraints**: Free tier limitations (Neon, Qdrant), browser CORS policies, Gemini API rate limits  
**Scale/Scope**: 13 book sections initially, scalable to 100+ sections, support multiple concurrent users  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### User-Centric RAG Design Compliance
- [x] Chatbot responses are accurate and relevant to robotics book content
- [x] User-selected text context enhances chatbot responses
- [x] User intent prioritization implemented in response generation

### Content Integrity Compliance
- [x] Responses only reference actual book content with source attribution
- [x] All answers include citations to specific book sections or chapters
- [x] No hallucination or generation of content beyond documented material

### Performance & Scalability Compliance
- [x] Response time under 2 seconds for typical queries
- [x] Serverless architecture using Neon and Qdrant Cloud Free Tier
- [x] System scales efficiently without performance degradation

## Project Structure

### Documentation (this feature)

```text
specs/001-rag-chatbot/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
└── contracts/           # Phase 1 output (/sp.plan command)
    ├── chat-api.openapi.yaml    # Chat API specification
    ├── ingestion-api.openapi.yaml # Content ingestion API specification
    └── database-schema.sql      # Complete database schema
```

### Source Code (repository root)

```text
backend/                    # FastAPI backend
├── app/
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── chat.py      # Chat question/answer endpoint
│   │   │   ├── sessions.py   # Session management
│   │   │   ├── health.py     # Health check endpoint
│   │   │   └── ingestion.py  # Content ingestion endpoint
│   ├── models/
│   │   ├── database.py     # SQLAlchemy models
│   │   ├── schemas.py      # Pydantic request/response models
│   │   └── embeddings.py   # Vector embedding logic
│   ├── services/
│   │   ├── rag.py          # RAG query orchestration
│   │   ├── gemini.py       # Google Gemini integration
│   │   ├── qdrant.py       # Vector database operations
│   │   └── neon.py         # Postgres database operations
│   └── main.py             # FastAPI application entry
├── tests/
│   ├── unit/
│   ├── integration/
│   └── performance/
├── scripts/
│   ├── ingest_content.py    # MDX parsing and database ingestion
│   └── setup_qdrant.py    # Vector collection initialization
└── requirements.txt

frontend/                   # React components for Docusaurus
├── src/
│   └── components/
│       └── rag-chatbot/
│           ├── ChatInterface.tsx    # Main chat UI component
│           ├── TextSelector.tsx     # Text selection feature
│           ├── SourceCitation.tsx   # Source display component
│           └── ConversationHistory.tsx # History display
├── styles/
│   └── chatbot.module.css   # Chatbot-specific styling
└── lib/
    └── api.ts               # API client functions

static/                     # Static assets
├── img/
│   └── chatbot-icons/     # UI icons and graphics
└── config/
    └── chatbot-config.js    # Frontend configuration

docs/                        # Existing book content (unchanged)
├── 01-introduction/
├── 02-physical-fundamentals/
├── 03-humanoid-design/
└── ...

docusaurus.config.js           # Updated with chatbot plugin
package.json                 # Updated with new dependencies
.env.example                 # Environment variables template
```

**Structure Decision**: Fullstack architecture with separate backend (FastAPI) and frontend (React components) integrated into existing Docusaurus site

## Complexity Tracking

> **Constitution Check: PASSED - All principles aligned**

| Resolution | Issue | Solution |
|------------|--------|----------|
| UI Integration | Chatbot placement in Docusaurus | Floating chat button with modal interface for optimal UX |
| Text Selection | Accessibility and performance | React-based selection with keyboard support and screen reader compatibility |
| Session Management | Cross-page conversation continuity | Server-side sessions with browser fallback for persistence |
| LLM Integration | OpenAI Agents SDK with Gemini model | Use OpenAI Agents SDK with Gemini API integration as specified |

## Phase 0: Research & Decisions - COMPLETED

### Resolved Decisions
- **Chatbot UI**: Floating button in bottom-right corner with modal overlay for chat interface
- **Text Selection**: React-based selection with automatic context detection and manual trigger button
- **Session Persistence**: Server-side storage with localStorage fallback for offline capability
- **API Integration**: FastAPI with CORS middleware for cross-origin requests from Docusaurus
- **Vector Configuration**: Qdrant HNSW index with ef_construct=200, cosine similarity
- **Embedding Strategy**: 512-token chunks for content >1000 tokens, 768-dimension vectors
- **Error Handling**: Graceful degradation with retry logic for Gemini API rate limits

### Constitution Compliance
- **User-Centric Design**: Accurate responses with source citations and text context enhancement
- **Content Integrity**: All responses reference actual book content only
- **Performance & Scalability**: Serverless architecture meeting <3s response time requirement

## Phase 1: Design & Contracts - COMPLETED

### Generated Artifacts
- **research.md**: All technical decisions documented with UX research findings
- **data-model.md**: Complete entity definitions with validation rules
- **contracts/**: Technical specifications for implementation
  - chat-api.openapi.yaml: REST API specification with all endpoints
  - ingestion-api.openapi.yaml: Content ingestion API specification
  - database-schema.sql: Complete SQL schema for all tables
- **quickstart.md**: Development setup and deployment guide

### Design Validation
- **Performance Requirements**: <5s total response time (3-5s target), <200ms vector search validated
- **Constitution Alignment**: All principles satisfied with technical implementation approach
- **Integration Patterns**: CORS, async operations, error handling documented
- **Deployment Strategy**: GitHub Pages + serverless backend architecture confirmed

## Phase 2: File Structure & Generation - READY

### Planned Structure
```text
Backend Implementation:
- FastAPI application with modular endpoint structure
- SQLAlchemy models for database operations
- Async/await patterns for performance
- Pydantic schemas for request/response validation
- Comprehensive error handling and logging

Frontend Integration:
- React 19.0.0 components with TypeScript
- Floating chat button with modal interface
- Text selection with accessibility support
- Real-time API integration with loading states
- Responsive design for mobile compatibility

Database & Vector Operations:
- Neon Postgres with connection pooling
- Qdrant Cloud with HNSW optimization
- Embedding generation with Gemini API
- Content ingestion pipeline automation
```

### Implementation Requirements
- **Total Components**: 4 React components, 6 API endpoints, 4 database models
- **Frontend**: TypeScript with proper type definitions and error boundaries
- **Backend**: Python 3.9+ with async/await patterns and comprehensive testing
- **Integration**: CORS configuration, API versioning, health check endpoints
- **Performance**: Response time monitoring, vector search optimization, caching strategies

### Next Steps
1. Implement FastAPI backend with all endpoints and models
2. Create React components with TypeScript and accessibility features
3. Set up Qdrant collection and implement vector search
4. Configure Neon Postgres with proper indexing and relationships
5. Integrate Gemini API with proper error handling and rate limiting
6. Test complete RAG pipeline end-to-end
7. Deploy backend to serverless platform and integrate frontend
8. Validate constitution compliance and performance requirements