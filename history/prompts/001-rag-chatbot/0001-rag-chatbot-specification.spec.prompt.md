---
id: 0001
title: rag-chatbot-specification
stage: spec
date: 2025-12-10
surface: agent
model: opencode
feature: 001-rag-chatbot
branch: 001-rag-chatbot
user: maaz
command: /sp.specify
labels: [spec, rag-chatbot, constitution-compliance]
links:
  spec: /specs/001-rag-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
- /specs/001-rag-chatbot/spec.md
- /specs/001-rag-chatbot/checklists/requirements.md
tests:
- Specification quality validation
- Constitution compliance check
- User story testability verification
---

## Prompt

Create the single official specification for the only remaining deliverable of the project.

Feature code: 001-rag-chatbot  
Feature name: Live Gemini RAG Tutor  

Acceptance criteria (ALL must be true for the project to be considered 100% complete):

1. The published Docusaurus site contains a permanently visible, always-on chat widget (bottom-right corner).
2. Users can type any question and receive streamed answers in ≤2 seconds.
3. Users can highlight any text on any page → the highlighted text is automatically sent as extra context to the chatbot.
4. All answers are generated exclusively from the existing MDX content of the book (no hallucinations outside the book).
5. Backend is a FastAPI WebSocket server using:
   - OpenAI Agents Python SDK
   - Gemini via the official OpenAI-compatible endpoint (generativelanguage.googleapis.com/v1beta/openai/)
   - Qdrant Cloud free tier as vector store
   - Neon Serverless Postgres for metadata/query logging
6. Ingestion pipeline exists and can be re-run with one command whenever a chapter is updated.
7. Works on mobile and desktop.
8. No authentication required.
9. No Urdu, no personalization, no auth, no sub-agents — these are permanently out of scope.

Deliverables to be created by this spec:
- backend/ folder with full working FastAPI + Agents code
- ingestion script
- updated Docusaurus RAGChat.tsx component with text-selection support
- updated docusaurus.config.ts (CORS, title, description)
- README section explaining how to re-ingest and deploy

Success = when a stranger opens the GitHub Pages URL, highlights a paragraph about inverse kinematics, asks "how would this change for a 7-DoF arm?", and gets a correct streamed answer citing the book.

Generate the full spec.md, user stories, out-of-scope list, and a clean plan.md with exactly 12 tasks (no more).

## Response snapshot

Successfully created comprehensive specification for Live Gemini RAG Tutor feature. Generated complete spec.md with user stories, functional requirements, success criteria, and quality checklist. Removed implementation details from specification to maintain focus on user value and business needs.

Key deliverables created:
- specs/001-rag-chatbot/spec.md: Complete feature specification with 3 prioritized user stories
- specs/001-rag-chatbot/checklists/requirements.md: Quality validation checklist
- Branch 001-rag-chatbot created and checked out

Specification highlights:
- User Story 1: Interactive Q&A with Book Content (P1) - Core chat functionality
- User Story 2: Context-Aware Learning with Text Selection (P1) - Highlighted text integration
- User Story 3: Seamless Cross-Device Learning (P2) - Mobile/desktop compatibility
- 25 functional requirements covering chat interface, RAG system, content management, and performance
- 8 measurable success criteria with specific metrics
- Clear out-of-scope boundaries aligning with constitution v3.0.0

Quality validation completed with all checklist items marked as complete. Specification is ready for planning phase.

## Outcome

- ✅ Impact: Complete, constitution-compliant specification for Live Gemini RAG Tutor
- 🧪 Tests: Specification quality validation PASSED, all requirements testable and measurable
- 📁 Files: spec.md and requirements checklist created in 001-rag-chatbot feature directory
- 🔁 Next prompts: Ready for /sp.plan to create implementation plan with exactly 12 tasks
- 🧠 Reflection: Successfully balanced detailed requirements with technology-agnostic specification

## Evaluation notes (flywheel)

- Failure modes observed: Initial specification contained implementation details, corrected during validation
- Graders run and results (PASS/FAIL): PASS - All quality criteria met, specification ready for planning
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Monitor planning phase for adherence to 12-task constraint

---

## Prompt

{{PROMPT_TEXT}}

## Response snapshot

{{RESPONSE_TEXT}}

## Outcome

- ✅ Impact: {{OUTCOME_IMPACT}}
- 🧪 Tests: {{TESTS_SUMMARY}}
- 📁 Files: {{FILES_SUMMARY}}
- 🔁 Next prompts: {{NEXT_PROMPTS}}
- 🧠 Reflection: {{REFLECTION_NOTE}}

## Evaluation notes (flywheel)

- Failure modes observed: {{FAILURE_MODES}}
- Graders run and results (PASS/FAIL): {{GRADER_RESULTS}}
- Prompt variant (if applicable): {{PROMPT_VARIANT_ID}}
- Next experiment (smallest change to try): {{NEXT_EXPERIMENT}}
