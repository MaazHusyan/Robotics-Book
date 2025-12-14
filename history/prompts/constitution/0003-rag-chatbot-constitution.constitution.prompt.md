---
id: 0003
title: rag-chatbot-constitution
stage: constitution
date: 2025-12-14
surface: cli
model: opencode
feature: rag-chatbot
branch: chatbot-integ
user: maaz
command: /sp.constitution
labels: [constitution, rag-chatbot, integration]
links:
  spec: 
  ticket: 
  adr: 
  pr: 
files:
  - path: .specify/memory/constitution.md
    action: updated with RAG Chatbot principles v2.1.0
  - path: .specify/templates/plan-template.md
    action: updated compliance checks for RAG principles
  - path: .specify/templates/spec-template.md
    action: updated requirements for RAG chatbot feature
  - path: .specify/templates/tasks-template.md
    action: updated path conventions for RAG structure
tests:
  - type: constitution-validation
    status: passed
    result: all placeholders replaced with RAG-specific content
---

## Prompt

OBJECTIVE:
Create a Constitution for the RAG Chatbot Integration feature using Speckit+ and `/sp.` CLI commands.

PROJECT CONTEXT:
- Project: Physical and Humanoid Robotics Book (Docusaurus 3.9.2)
- Location: /home/maaz/Desktop/Robotics-Book
- Branch: chatbot-integ
- Requirement: Build & embed a RAG Chatbot using OpenAI Agents/ChatKit SDKs, FastAPI, Neon Postgres, Qdrant Cloud

TASK: Create RAG Chatbot Constitution

INSTRUCTIONS:

1. Navigate to project root:
   cd /home/maaz/Desktop/Robotics-Book

2. Use Speckit+ to create/update RAG Chatbot Constitution by running:
   /sp. constitution rag-chatbot

3. This will open the constitution template for "rag-chatbot" feature.
   Fill in the following sections based on feature requirements:

   SECTION A: Core Principles (Replace template placeholders)
   - [PRINCIPLE_1_NAME]: "User-Centric RAG Design"
     [PRINCIPLE_1_DESCRIPTION]: Define principle that chatbot answers should be accurate, 
     relevant to book content, and enhanced by user-selected text context.
   
   - [PRINCIPLE_2_NAME]: "Content Integrity"
     [PRINCIPLE_2_DESCRIPTION]: Define principle that chatbot responses should only reference 
     actual book content, with clear source attribution.
   
   - [PRINCIPLE_3_NAME]: "Performance & Scalability"
     [PRINCIPLE_3_DESCRIPTION]: Define principle for fast retrieval and response times 
     using serverless architecture (Neon, Qdrant Free Tier).

   SECTION B: Technical Stack Requirements
   - Platform: Docusaurus 3.9.2 + React 19.0.0 (frontend), FastAPI (backend)
   - Vector DB: Qdrant Cloud Free Tier
   - Database: Neon Serverless Postgres
   - LLM Integration: OpenAI Agents/ChatKit SDKs
   - API Communication: REST API (FastAPI)
   - Deployment: GitHub Pages (frontend), Serverless (backend)

   SECTION C: Writing Style Guidelines
   - Code Examples: Python (FastAPI backend), TypeScript/JSX (React components)
   - API Documentation: OpenAPI/Swagger style
   - Component Documentation: React component prop documentation

   SECTION D: Quality Assurance Requirements
   - RAG answer accuracy (test with sample questions)
   - Response time benchmarks (< 2 seconds for typical queries)
   - Vector search relevance scoring
   - Text selection feature reliability
   - API error handling and resilience

   SECTION E: Development Guidelines
   - AI Usage: All code generation, prompts, and documentation creation via AI
   - Review Process: Code review before merging, test execution for QA
   - Success Metrics: 
     * Chatbot successfully embedded in Docusaurus
     * Can answer book-related questions accurately
     * Text selection feature works reliably
     * Response time under 2 seconds

   SECTION F: Governance
   - Authority: Feature owner (user) makes final decisions
   - Amendment Process: Update via /sp. constitution rag-chatbot
   - Compliance: Follow project's opencode.md spec-driven development rules

4. Save the constitution file when prompted

5. Create a Prompt History Record (PHR) for this work:
   Use: /sp. phr constitutional rag-chatbot-constitution
   
   In the PHR, document:
   - Objective: Created constitution for RAG Chatbot feature
   - Decisions: Core principles, technical stack alignment
   - Rationale: Why these principles support feature goals
   - Status: Constitution complete and ready for Specification phase

6. Confirm completion by checking:
   - Constitution file exists and is properly formatted
   - PHR record is created in history/prompts/
   - All template sections have been filled with actual content

ACCEPTANCE CRITERIA:
✅ RAG Chatbot Constitution document created
✅ All sections filled with meaningful content (not templates)
✅ PHR record documenting this work exists
✅ Constitution aligns with project's opencode.md principles
✅ Ready for next phase: Specification

SUCCESS INDICATORS:
- Constitution file is readable and complete
- Principles are clear and actionable
- Technical stack is well-defined
- QA requirements are measurable
- PHR is properly formatted and indexed

## Response snapshot

Successfully created RAG Chatbot Constitution v2.1.0:
- Replaced all template placeholders with RAG-specific content
- Defined 3 core principles: User-Centric RAG Design, Content Integrity, Performance & Scalability
- Specified complete technical stack (Docusaurus 3.9.2, FastAPI, Qdrant Cloud, Neon, OpenAI)
- Established quality requirements (95% accuracy, <2s response time, 0.8 relevance score)
- Updated all templates to align with new principles
- Created comprehensive governance structure

## Outcome

- ✅ Impact: RAG Chatbot Constitution established with clear principles and technical requirements
- 🧪 Tests: Constitution validation passed - all placeholders replaced with actionable content
- 📁 Files: 4 files updated (constitution + 3 templates)
- 🔁 Next prompts: Ready for specification phase (/sp.specify rag-chatbot)
- 🧠 Reflection: Successfully balanced technical requirements with user experience principles

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS - Constitution fully compliant with requirements
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test specification creation workflow with new constitution