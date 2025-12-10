# Implementation Plan: Full Reader Enhancement Suite – 200 Bonus Points

**Branch**: `002-enhanced-reader` | **Date**: 2025-12-10 | **Spec**: /specs/002-enhanced-reader/spec.md
**Input**: Feature specification from `/specs/002-enhanced-reader/spec.md`

**Note**: This template is filled in by `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Create a comprehensive reader enhancement suite implementing 200 bonus points across four core features: authentication with background survey, RAG chatbot, content personalization, and Urdu translation. The solution uses Better Auth, OpenAI Agents/ChatKit, FastAPI, Neon Postgres with pgvector, Qdrant Cloud, and opencode Code Subagents while strictly protecting existing /docs/ content.

## Technical Context

**Language/Version**: TypeScript/JavaScript (Node.js 18+), Python 3.11+  
**Primary Dependencies**: Better Auth, OpenAI Agents/ChatKit SDKs, FastAPI, Neon Serverless Postgres, Qdrant Cloud, Docusaurus v3+  
**Storage**: Neon Serverless Postgres with pgvector extension, Qdrant Cloud Free Tier for vector storage  
**Testing**: Jest, Cypress, Playwright for frontend; pytest for backend  
**Target Platform**: Vercel/Netlify (static hosting) + Railway/Render (backend services)  
**Project Type**: web/full-stack - Docusaurus static site with FastAPI backend services  
**Performance Goals**: <2s page load, <500ms API response, 1000 concurrent users  
**Constraints**: Must not modify existing /docs/ folder, all new code in designated directories, authentication required for enhanced features  
**Scale/Scope**: 10,000+ concurrent users, 200+ pages of content, real-time chatbot responses  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Integrated RAG Chatbot Compliance (50 points)
- [ ] RAG chatbot embedded using OpenAI Agents/ChatKit SDKs
- [ ] FastAPI backend implemented for chatbot functionality
- [ ] Neon Serverless Postgres with pgvector configured for embeddings
- [ ] Qdrant Cloud Free Tier used for vector storage
- [ ] Chatbot answers questions about book content
- [ ] Chatbot processes user-selected/highlighted text only
- [ ] Integration via sidebar widget or dedicated /chat page
- [ ] Chatbot only visible to logged-in users

### opencode Code Subagents Compliance (50 points)
- [ ] opencode CLI used as exclusive AI agent throughout project
- [ ] All mentions of "Claude" replaced with "opencode"
- [ ] Reusable opencode Code Subagents created and utilized for all backend logic
- [ ] Agent Skills implemented for repeatable tasks
- [ ] Consistent tooling maintained across development activities

### Authentication + Background Survey Compliance (50 points)
- [ ] Better Auth implemented for signup/signin functionality
- [ ] Email/password authentication supported
- [ ] Optional Google OAuth authentication provided
- [ ] Custom signup form collects 5-7 questions about software/hardware/robotics background
- [ ] User profiles created and managed
- [ ] Background information stored for personalization use
- [ ] Authentication system integrated with Docusaurus

### Personalization Toggle Compliance (50 points)
- [ ] Per-chapter personalization toggle buttons implemented at the top of every future chapter
- [ ] Content adaptation based on user background (beginner/intermediate/expert)
- [ ] Advanced modules shown for expert users
- [ ] Personalization toggle functional for logged-in users only
- [ ] User preferences stored and applied consistently across chapters
- [ ] Content rewritten/explained according to user's background level

### Urdu Translation Toggle Compliance (50 points)
- [ ] Per-chapter Urdu translation toggle buttons implemented at the top of every future chapter
- [ ] OpenAI API integrated for translation functionality
- [ ] Original English content preserved
- [ ] Translations provided as overlays or toggles
- [ ] Translation system functional for logged-in users only
- [ ] Urdu translation instant (page-level translation)

### Content Protection Requirements
- [ ] Existing /docs/ folder and all current files remain sacred and untouchable
- [ ] No changes to folder's files content and structure without explicit permission
- [ ] New chapter/module generation only with explicit human owner request
- [ ] Features completely invisible and inactive until human owner explicitly requests chapter generation

### Code Location Requirements
- [ ] All new code lives only in /src/features/enhanced-reader/
- [ ] Backend code lives only in /backend/
- [ ] Book ingestion scripts live only in /scripts/ingest-book.ts
- [ ] Authentication code lives only in /auth/
- [ ] No code modifications allowed outside these designated directories

### Feature Visibility Requirements
- [ ] Chatbot only visible to logged-in users
- [ ] Personalization buttons appear only for logged-in users
- [ ] Urdu translation buttons appear only for logged-in users
- [ ] All enhanced features invisible to anonymous visitors

## Project Structure

### Documentation (this feature)

```text
specs/002-enhanced-reader/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── api-schema.md
│   ├── auth-flow.md
│   ├── chatbot-api.md
│   └── personalization-rules.md
└── checklists/
    ├── requirements.md    # Already created
    └── testing.md        # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
# Enhanced Reader Feature Implementation
src/features/enhanced-reader/          # Main feature code
├── components/                    # React components for UI
│   ├── AuthButton.tsx
│   ├── ChatWidget.tsx
│   ├── PersonalizationToggle.tsx
│   └── UrduTranslationToggle.tsx
├── hooks/                         # Custom React hooks
│   ├── useAuth.ts
│   ├── usePersonalization.ts
│   └── useTranslation.ts
├── services/                      # API integration services
│   ├── authService.ts
│   ├── chatbotService.ts
│   ├── personalizationService.ts
│   └── translationService.ts
├── utils/                         # Utility functions
│   ├── backgroundSurvey.ts
│   ├── contentAdapter.ts
│   └── opencodeSubagents.ts
└── types/                         # TypeScript definitions
    ├── user.ts
    ├── chat.ts
    └── content.ts

backend/                              # FastAPI backend services
├── app/
│   ├── main.py                     # FastAPI application entry
│   ├── middleware/                  # Authentication, CORS, etc.
│   ├── routers/                     # API endpoints
│   │   ├── auth.py
│   │   ├── chatbot.py
│   │   ├── personalization.py
│   │   └── translation.py
│   └── models/                      # Database models
│       ├── user.py
│       ├── chat.py
│       └── content.py
├── services/                      # Business logic services
│   ├── auth_service.py
│   ├── rag_service.py
│   ├── personalization_service.py
│   └── translation_service.py
├── database/                      # Database configuration
│   ├── connection.py
│   └── migrations/
├── vector_store/                  # Qdrant integration
│   ├── client.py
│   └── embeddings.py
└── opencode_agents/               # opencode Code Subagents
    ├── chatbot_agent.py
    ├── content_processor.py
    ├── user_profiler.py
    └── translation_agent.py

auth/                                 # Better Auth integration
├── auth.config.ts                 # Better Auth configuration
├── providers/                     # Auth providers
│   ├── credentials.ts
│   └── google.ts
└── hooks/                        # Auth hooks
    ├── after-signup.ts
    └── before-signin.ts

scripts/ingest-book.ts               # Book content ingestion pipeline
```

**Structure Decision**: Full-stack implementation with strict separation of concerns, protected /docs/ content, and designated code locations per constitution

## Complexity Tracking

> **Constitution Check: PASSED - All requirements addressed without violations**

| Resolution | Issue | Solution |
|------------|--------|----------|
| Content protection | Strict rules for /docs/ folder | Designated code locations only |
| Feature visibility | Enhanced features only for logged-in users | Authentication-gated UI components |
| opencode exclusivity | Replace all "Claude" references | opencode Code Subagents architecture |
| Technical stack | Specific technologies required | Detailed technical context defined |

## Phase 0: Research & Decisions - COMPLETED

### Resolved Decisions
- **Authentication**: Better Auth with email/password + Google OAuth
- **RAG Stack**: OpenAI Agents/ChatKit + FastAPI + Neon pgvector + Qdrant Cloud
- **Frontend**: TypeScript React components in Docusaurus
- **Backend**: Python FastAPI with modular services
- **Code Organization**: Strict directory separation per constitution
- **Deployment**: Static site + backend services separation

### Constitution Compliance
- **Content Protection**: All new code in designated directories only
- **Authentication Required**: Enhanced features gated by login
- **opencode Exclusive**: All backend logic uses opencode Code Subagents
- **Feature Scope**: No blog, multiplayer, or payment features

## Phase 1: Design & Contracts - COMPLETED

### Generated Artifacts
- **research.md**: All technical decisions documented
- **data-model.md**: User profiles, chat sessions, content vectors, translation cache
- **contracts/**: Technical specifications for implementation
  - api-schema.md: OpenAPI specification for all endpoints
  - auth-flow.md: Authentication flow diagrams and requirements
  - chatbot-api.md: RAG chatbot API specification
  - personalization-rules.md: Content adaptation logic
- **quickstart.md**: Development and deployment guide

### Design Validation
- **Performance Requirements**: <2s page load, <500ms API response
- **Security Requirements**: Better Auth integration, JWT tokens, secure API endpoints
- **Scalability Requirements**: 10,000+ concurrent users, vector search optimization
- **Accessibility Compliance**: WCAG 2.1 AA standards, screen reader support
- **Content Standards**: Constitution-aligned requirements with strict governance

## Phase 2: Project Setup & Better Auth Integration - READY

### Implementation Requirements
- **Directory Structure**: Create all designated directories
- **Package Management**: package.json with dependencies for frontend and backend
- **Better Auth Setup**: Complete authentication configuration
- **Database Schema**: Neon Postgres with pgvector extension
- **Environment Configuration**: Development and production environment setup

### Key Tasks
1. Create project directory structure per constitution
2. Setup Better Auth with email/password + Google OAuth
3. Configure Neon Postgres database with pgvector
4. Setup Qdrant Cloud vector storage
5. Initialize FastAPI backend with authentication
6. Create Docusaurus plugin structure for enhanced features
7. Setup development environment with TypeScript/Python

## Phase 3: User Profile + Background Survey - READY

### Implementation Requirements
- **User Profile Model**: Store authentication, background survey, preferences
- **Background Survey**: 5-7 questions about software/hardware/robotics experience
- **Profile Management**: CRUD operations for user data
- **Privacy Compliance**: Secure storage of user information

### Key Tasks
1. Design user profile database schema
2. Implement background survey form component
3. Create user profile management APIs
4. Implement survey response processing
5. Add profile data validation and security

## Phase 4: FastAPI Backend Skeleton + Neon + Qdrant - READY

### Implementation Requirements
- **FastAPI Application**: Modular router structure
- **Database Integration**: Neon Postgres with async connection pooling
- **Vector Storage**: Qdrant Cloud client for embeddings
- **API Documentation**: OpenAPI/Swagger documentation
- **Error Handling**: Comprehensive error responses and logging

### Key Tasks
1. Setup FastAPI application structure
2. Implement database connection and models
3. Create Qdrant client and embedding service
4. Design API router structure
5. Implement middleware for authentication and CORS
6. Add comprehensive error handling and logging

## Phase 5: Book Ingestion Pipeline - READY

### Implementation Requirements
- **Content Processing**: MDX to text extraction and chunking
- **Embedding Generation**: OpenAI API for vector embeddings
- **Vector Storage**: Qdrant Cloud for semantic search
- **Incremental Updates**: Pipeline for new content updates
- **Content Protection**: No modifications to existing /docs/ files

### Key Tasks
1. Create MDX parsing and text extraction
2. Implement content chunking strategy
3. Setup OpenAI embedding generation
4. Create Qdrant vector storage service
5. Build ingestion pipeline with TypeScript
6. Add content update monitoring

## Phase 6: RAG Chatbot Backend + opencode Subagents - READY

### Implementation Requirements
- **RAG Architecture**: Retrieval-augmented generation with vector search
- **OpenAI Integration**: Agents/ChatKit SDKs for chatbot logic
- **opencode Subagents**: Reusable code agents for backend logic
- **Context Management**: Chat session history and user context
- **Highlight Processing**: Text selection and contextual queries

### Key Tasks
1. Implement RAG retrieval service
2. Create OpenAI Agents/ChatKit integration
3. Build opencode Code Subagents architecture
4. Implement chat session management
5. Create text highlight processing
6. Add contextual response generation

## Phase 7: Docusaurus Frontend Components - READY

### Implementation Requirements
- **Authentication UI**: Login/signup forms with Better Auth integration
- **Chat Widget**: Floating chat interface for logged-in users
- **Personalization Toggle**: Chapter-level content adaptation buttons
- **Urdu Translation**: Page-level translation toggle functionality
- **Responsive Design**: Mobile-friendly component design

### Key Tasks
1. Create authentication components (login/signup)
2. Build floating chat widget component
3. Implement personalization toggle buttons
4. Create Urdu translation toggle
5. Add user profile management interface
6. Integrate all components with Docusaurus theme

## Next Steps

1. **Phase 2 Execution**: Begin project setup and Better Auth integration
2. **Phase 3 Execution**: Implement user profiles and background survey
3. **Phase 4 Execution**: Build FastAPI backend with database integration
4. **Phase 5 Execution**: Create book ingestion pipeline
5. **Phase 6 Execution**: Implement RAG chatbot with opencode Subagents
6. **Phase 7 Execution**: Build Docusaurus frontend components
7. **Integration Testing**: End-to-end testing of all features
8. **Documentation**: Complete API documentation and deployment guides

### Implementation Strategy

**MVP First Approach**:
1. Complete Phase 2: Project setup and authentication
2. Complete Phase 3: User profiles and basic survey
3. Complete Phase 4: Backend skeleton with database
4. **STOP and VALIDATE**: Test authentication and basic user management
5. Deploy basic authentication system for verification

**Incremental Delivery**:
1. Add RAG chatbot backend (Phase 6)
2. Implement book ingestion pipeline (Phase 5)
3. Create frontend components (Phase 7)
4. Add personalization and translation features
5. Complete integration testing and documentation

**Quality Gates**:
- **Authentication Gate**: Better Auth integration must be complete before user features
- **Backend Gate**: FastAPI skeleton must be complete before RAG implementation
- **Content Protection Gate**: Zero changes to /docs/ folder throughout development
- **Constitution Gate**: All features must comply with strict governance rules