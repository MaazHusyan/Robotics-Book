---
id: 0002
title: rag-chatbot-implementation-plan
stage: plan
date: 2025-12-14
surface: cli
model: opencode
feature: 001-rag-chatbot
branch: 001-rag-chatbot
user: maaz
command: /sp.plan
labels: [implementation, planning, rag-chatbot]
links:
  spec: /specs/001-rag-chatbot/spec.md
  ticket: 
  adr: 
  pr: 
files:
  - path: specs/001-rag-chatbot/plan.md
    action: created comprehensive implementation plan
  - path: specs/001-rag-chatbot/research.md
    action: completed technical research and decisions
  - path: specs/001-rag-chatbot/data-model.md
    action: created complete entity definitions
  - path: specs/001-rag-chatbot/contracts/chat-api.openapi.yaml
    action: created comprehensive API specification
  - path: specs/001-rag-chatbot/contracts/ingestion-api.openapi.yaml
    action: created content ingestion API specification
  - path: specs/001-rag-chatbot/contracts/database-schema.sql
    action: created complete database schema
  - path: specs/001-rag-chatbot/quickstart.md
    action: created development and deployment guide
tests:
  - type: planning-validation
    status: passed
    result: all phases completed with constitution alignment
---

## Prompt

OBJECTIVE:
Execute the implementation planning workflow for RAG Chatbot using Speckit+ `/sp. plan` 
command and follow the official plan template structure.

PROJECT CONTEXT:
- Project: Physical and Humanoid Robotics Book (Docusaurus)
- Location: /home/maaz/Desktop/Robotics-Book
- Branch: chatbot-integ
- Feature: rag-chatbot-implementation
- Database Spec: COMPLETED (/specs/001-rag-chatbot/spec.md)
- LLM: Google Gemini (AsyncOpenAI with custom base_url)

INSTRUCTIONS:

================================================================================
STEP 1: SETUP
================================================================================

1. Navigate to project root:
   cd /home/maaz/Desktop/Robotics-Book

2. Run setup script to get configuration:
   .specify/scripts/bash/setup-plan.sh --json

3. Parse the JSON output for:
   - FEATURE_SPEC
   - IMPL_PLAN (template path)
   - SPECS_DIR
   - BRANCH

4. Note: If any paths contain single quotes, use escape: 'I'\''m Groot' 
   or use double quotes: "I'm Groot"

================================================================================
STEP 2: LOAD CONTEXT
================================================================================

1. Read the feature specification:
   cat $FEATURE_SPEC

2. Read the project constitution:
   cat .specify/memory/constitution.md

3. Load the implementation plan template:
   cat $IMPL_PLAN

   (The template provides a structure to follow)

================================================================================
STEP 3: EXECUTE PLAN WORKFLOW
================================================================================

Run the command to start the planning workflow:
/sp. plan rag-chatbot-implementation

This will open the plan template. Follow the structure below to fill it in:

================================================================================
TECHNICAL CONTEXT SECTION
================================================================================

Fill in ALL fields. Mark unknowns as "NEEDS CLARIFICATION":

**Feature Name**: RAG Chatbot Integration for Robotics Book

**Technology Stack**:
- Frontend: React 19.0.0 + MDX in Docusaurus 3.9.2
- Backend: FastAPI (Python 3.9+)
- Database: Neon Serverless Postgres
- Vector DB: Qdrant Cloud Free Tier
- LLM: Google Gemini 2.0-flash (via OpenAI SDK with custom base_url)
- Embedding Model: Gemini embedding model (768 dimensions)
- API Pattern: REST (JSON request/response)

**Key Integrations**:
- Docusaurus static site generation
- Neon Postgres connection pooling
- Qdrant vector similarity search
- Google Gemini API via OpenAI-compatible endpoint
- FastAPI CORS middleware for cross-origin requests

**Unknowns / NEEDS CLARIFICATION**:
- Chatbot UI placement: (User to provide - floating button? sidebar? modal?)
- Chatbot appearance style: (User to provide - dark/light theme preference)
- Text selection UX: (User to provide - auto-detect or button trigger?)
- Response format preferences: (User to provide - markdown? code blocks? citations style?)
- Session persistence: (Should conversations be saved across page loads? Browser only or server?)

================================================================================
CONSTITUTION CHECK SECTION
================================================================================

From `.specify/memory/constitution.md`, verify alignment:

**Core Principles**:
1. ✅ User-Centric RAG Design
   - Alignment: Chatbot must provide accurate, relevant answers from book content
   
2. ✅ Content Integrity
   - Alignment: All responses must include source citations to book sections
   
3. ✅ Performance & Scalability
   - Alignment: Must use serverless architecture (Neon + Qdrant Free Tier)

**Technical Stack Requirements**:
- ✅ Platform: Docusaurus 3.9.2 + React 19.0.0
- ✅ Deployment: GitHub Pages (frontend) + serverless (backend)
- ✅ Version Control: Git
- ✅ Backend: FastAPI
- ✅ Database: Neon Postgres + Qdrant Cloud
- ✅ LLM: Google Gemini (custom integration per user's reference files)

**Writing Style Guidelines**:
- Code examples: Python (backend), TypeScript/JSX (frontend)
- API documentation: OpenAPI/Swagger format
- Components: React component prop documentation

**Quality Assurance**:
- RAG answer accuracy testing
- Response time benchmarks (< 3 seconds)
- Vector search relevance validation
- Text selection feature reliability

**Any Constitution Violations?** NO - proceed to Phase 0

================================================================================
PHASE 0: OUTLINE & RESEARCH
================================================================================

**Unknowns to Research** (all marked as "NEEDS CLARIFICATION" above):

1. **Chatbot UI Placement & Appearance**
   - Research Task: Determine optimal placement (floating button, sidebar, modal)
   - Research Task: Define style (match Docusaurus theme, dark/light mode)
   - Research Task: Design responsive behavior (mobile vs desktop)

2. **Text Selection UX Implementation**
   - Research Task: Best practices for text selection detection in React
   - Research Task: Accessibility considerations (keyboard support, screen readers)
   - Research Task: Performance impact of selection listeners

3. **Session Persistence Strategy**
   - Research Task: Browser localStorage vs server-side session storage
   - Research Task: Session expiration and cleanup
   - Research Task: GDPR/privacy implications

4. **Gemini + OpenAI SDK Integration Best Practices**
   - Research Task: AsyncOpenAI compatibility with Gemini
   - Research Task: Error handling and retry strategies
   - Research Task: Rate limiting and quota management

5. **FastAPI + Docusaurus Integration**
   - Research Task: CORS configuration for cross-origin requests
   - Research Task: API versioning strategy
   - Research Task: Deployment patterns for FastAPI with static sites

6. **Qdrant Vector Search Optimization**
   - Research Task: HNSW parameter tuning for book content
   - Research Task: Chunk size optimization (256, 512, 1024 tokens)
   - Research Task: Relevance scoring and filtering

**Output**: Generate `research.md` with findings for all unknowns

**How to Complete Phase 0**:
1. For each research task above, investigate:
   - Decision: What was chosen
   - Rationale: Why this approach
   - Alternatives considered: What else was evaluated
   - Implementation notes: How to execute

2. Create file: `specs/001-rag-chatbot/research.md`
3. Document all findings
4. Mark as COMPLETE when all unknowns resolved

================================================================================
PHASE 1: DESIGN & CONTRACTS
================================================================================

**Prerequisites**: Phase 0 research.md complete and all NEEDS CLARIFICATION resolved

**Step 1: Extract Entities & Generate Data Model**

From database spec (already complete), create `data-model.md`:

1. Entity: `BookContent`
   - id: UUID
   - chapter_number: Integer
   - chapter_title: String
   - section_number: Integer
   - section_title: String
   - content_text: Text
   - content_hash: String (unique)
   - source_file: String
   - word_count: Integer
   - created_at: Timestamp
   - updated_at: Timestamp
   - is_active: Boolean

2. Entity: `Conversation`
   - id: UUID
   - session_id: String
   - user_query: Text
   - chatbot_response: Text
   - selected_text: Text (optional)
   - selected_text_section_id: UUID (FK to BookContent)
   - gemini_model_used: String
   - tokens_used: Integer
   - response_time_ms: Integer
   - confidence_score: Float (0-1)
   - is_helpful: Boolean (optional)
   - created_at: Timestamp

3. Entity: `EmbeddingMetadata`
   - id: UUID
   - books_content_id: UUID (FK)
   - qdrant_vector_id: String
   - embedding_model: String
   - chunk_index: Integer
   - chunk_size: Integer
   - vector_dimension: Integer
   - metadata_json: JSON
   - created_at: Timestamp
   - last_synced_at: Timestamp (optional)
   - is_indexed: Boolean

4. Entity: `Session`
   - id: String (primary key)
   - user_identifier: String
   - created_at: Timestamp
   - last_activity_at: Timestamp
   - browser_info: JSON
   - is_active: Boolean
   - conversation_count: Integer

**Validation Rules**:
- content_hash must be unique (prevent duplicates)
- confidence_score must be 0-1
- tokens_used >= 0
- response_time_ms >= 0
- session_id required for all conversations

**Output**: specs/001-rag-chatbot/data-model.md

---

**Step 2: Generate API Contracts**

Create `/contracts/` directory with endpoint specifications:

**File**: contracts/chat-api.openapi.yaml

```yaml
openapi: 3.0.0
info:
  title: RAG Chatbot API
  version: 1.0.0
  description: API for robotics book RAG chatbot

paths:
  /api/sessions/create:
    post:
      summary: Create new chat session
      tags: [Sessions]
      responses:
        '200':
          description: Session created
          content:
            application/json:
              schema:
                type: object
                properties:
                  session_id:
                    type: string
                    format: uuid
                  created_at:
                    type: string
                    format: date-time

  /api/sessions/{session_id}/history:
    get:
      summary: Get conversation history for session
      tags: [Sessions]
      parameters:
        - name: session_id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Conversation history
          content:
            application/json:
              schema:
                type: object
                properties:
                  session_id:
                    type: string
                  conversations:
                    type: array
                    items:
                      $ref: '#/components/schemas/Conversation'

  /api/chat/ask:
    post:
      summary: Ask chatbot a question
      tags: [Chat]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - session_id
                - query
              properties:
                session_id:
                  type: string
                  description: Session ID from /sessions/create
                query:
                  type: string
                  description: User question
                selected_text:
                  type: string
                  description: Optional selected text for context
                selected_section_id:
                  type: string
                  format: uuid
                  description: Optional reference to specific book section
      responses:
        '200':
          description: Chatbot response with sources
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ChatResponse'
        '400':
          description: Invalid request
        '500':
          description: Server error

  /api/health:
    get:
      summary: Health check - verify all services
      tags: [Health]
      responses:
        '200':
          description: All systems operational
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                    enum: [healthy, degraded, unhealthy]
                  neon_postgres:
                    type: string
                  qdrant_cloud:
                    type: string
                  gemini_api:
                    type: string

components:
  schemas:
    Conversation:
      type: object
      properties:
        id:
          type: string
          format: uuid
        user_query:
          type: string
        chatbot_response:
          type: string
        sources:
          type: array
          items:
            $ref: '#/components/schemas/Source'
        response_time_ms:
          type: integer
        confidence_score:
          type: number
          format: float
          minimum: 0
          maximum: 1
        created_at:
          type: string
          format: date-time

    ChatResponse:
      type: object
      properties:
        response:
          type: string
          description: Chatbot answer text
        sources:
          type: array
          items:
            $ref: '#/components/schemas/Source'
        response_time_ms:
          type: integer
        tokens_used:
          type: integer
        confidence_score:
          type: number
          format: float
          minimum: 0
          maximum: 1

    Source:
      type: object
      properties:
        chapter:
          type: string
        section:
          type: string
        excerpt:
          type: string
          description: Relevant quote from book
        relevance_score:
          type: number
          format: float
          minimum: 0
          maximum: 1 
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

1. **Setup**: Run `.specify/scripts/bash/setup-plan.sh --json` from repo root and parse JSON for FEATURE_SPEC, IMPL_PLAN, SPECS_DIR, BRANCH. For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

2. **Load context**: Read FEATURE_SPEC and `.specify/memory/constitution.md`. Load IMPL_PLAN template (already copied).

3. **Execute plan workflow**: Follow the structure in IMPL_PLAN template to:
   - Fill Technical Context (mark unknowns as "NEEDS CLARIFICATION")
   - Fill Constitution Check section from constitution
   - Evaluate gates (ERROR if violations unjustified)
   - Phase 0: Generate research.md (resolve all NEEDS CLARIFICATION)
   - Phase 1: Generate data-model.md, contracts/, quickstart.md
   - Phase 1: Update agent context by running the agent script
   - Re-evaluate Constitution Check post-design

4. **Stop and report**: Command ends after Phase 2 planning. Report branch, IMPL_PLAN path, and generated artifacts.

## Phases

### Phase 0: Outline & Research

1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:

   ```text
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

### Phase 1: Design & Contracts

**Prerequisites:** `research.md` complete

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Agent context update**:
   - Run `.specify/scripts/bash/update-agent-context.sh opencode`
   - These scripts detect which AI agent is in use
   - Update the appropriate agent-specific context file
   - Add only new technology from current plan
   - Preserve manual additions between markers

**Output**: data-model.md, /contracts/*, quickstart.md, agent-specific file

## Key rules

- Use absolute paths
- ERROR on gate failures or unresolved clarifications

---

As the main request completes, you MUST create and complete a PHR (Prompt History Record) using agent‑native tools when possible.

1) Determine Stage
   - Stage: constitution | spec | plan | tasks | red | green | refactor | explainer | misc | general

2) Generate Title and Determine Routing:
   - Generate Title: 3–7 words (slug for filename)
   - JSON output will contain BRANCH_NAME and SPEC_FILE paths
   - For single quotes in args like "I'm Groot", use escape: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot")

3) Create and Fill PHR (Shell first; fallback agent‑native)
   - Run: `.specify/scripts/bash/create-phr.sh --title "<title>" --stage <stage> [--feature <name>] --json`
   - Open the file and fill remaining placeholders (YAML + body), embedding full PROMPT_TEXT (verbatim) and concise RESPONSE_TEXT.
   - If the script fails:
     - Read `.specify/templates/phr-template.prompt.md` (or `templates/…`)
     - Allocate an ID; compute the output path based on stage from step 2; write the file
     - Fill placeholders and embed full PROMPT_TEXT and concise RESPONSE_TEXT

4) Validate + report
   - No unresolved placeholders; path under `history/prompts/` and matches stage; stage/title/date coherent; print ID + path + stage + title.
   - On failure: Phase 0 research completed with all technical decisions documented
   - Phase 1 design completed with comprehensive contracts and data models
   - Constitution alignment verified with no violations
   - All implementation artifacts generated and ready for development phase

## Response snapshot

Successfully executed RAG Chatbot implementation planning workflow:
- Created comprehensive implementation plan with technical context
- Completed Phase 0 research with all unknowns resolved
- Generated Phase 1 design artifacts including data models, API contracts, and quickstart guide
- Verified constitution compliance with no violations
- Established clear project structure and implementation requirements
- Ready for next phase: task generation and implementation

## Outcome

- ✅ Impact: Comprehensive implementation plan created for RAG chatbot feature
- 🧪 Tests: Planning validation passed - all phases completed successfully
- 📁 Files: 6 files created (plan.md, research.md, data-model.md, API contracts, database schema, quickstart.md)
- 🔁 Next prompts: Ready for tasks generation (/sp.tasks)
- 🧠 Reflection: Successfully balanced technical requirements with user experience needs

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS - All planning phases completed successfully
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test task generation workflow with new plan