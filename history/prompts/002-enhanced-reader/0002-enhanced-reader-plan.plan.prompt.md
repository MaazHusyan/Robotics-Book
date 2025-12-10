---
id: 0002
title: "enhanced-reader-plan"
stage: plan
date: 2025-12-10
surface: opencode
model: opencode-cli
feature: 002-enhanced-reader
branch: 002-enhanced-reader
user: maaz
command: /sp.plan
labels: [plan, enhanced-reader, implementation-phases, technical-architecture]
links:
  spec: /specs/002-enhanced-reader/spec.md
  ticket: 
  adr: 
  pr: 
files:
  - /specs/002-enhanced-reader/plan.md
tests:
  - Constitution compliance validation
  - Technical architecture review
  - Implementation phase planning
---

## Prompt

Plan the full implementation of feature enhanced-reader-experience-001 in 7 safe phases:
1. Project setup & Better Auth integration
2. User profile + background survey
3. FastAPI backend skeleton + Neon + Qdrant
4. Book ingestion pipeline (MDX → chunks → embeddings)
5. RAG chatbot backend + opencode Subagents
6. Docusaurus frontend components (chat widget + toggle buttons)
7. Testing, CI ingestion script, final documentation

Every phase must respect the rule: zero changes to existing /docs/ content.
Output plan to .specify/specs/enhanced-reader-experience-001/plan.md

## Response snapshot

Successfully created comprehensive 7-phase implementation plan for "Full Reader Enhancement Suite – 200 Bonus Points":

**Plan Structure**: Complete technical architecture with strict governance compliance
**7 Implementation Phases**:
1. Project setup & Better Auth integration
2. User profile + background survey  
3. FastAPI backend skeleton + Neon + Qdrant
4. Book ingestion pipeline (MDX → chunks → embeddings)
5. RAG chatbot backend + opencode Subagents
6. Docusaurus frontend components (chat widget + toggle buttons)
7. Testing, CI ingestion script, final documentation

**Technical Decisions**:
- TypeScript/JavaScript frontend with Python FastAPI backend
- Better Auth for authentication (email/password + Google OAuth)
- OpenAI Agents/ChatKit + Neon pgvector + Qdrant Cloud for RAG
- Strict directory separation per constitution
- Enhanced features gated by authentication

**Constitution Compliance**: All requirements addressed with zero /docs/ folder modifications
**Project Structure**: Detailed implementation plan with designated code locations
**Implementation Strategy**: MVP first approach with incremental delivery

## Outcome

- ✅ Impact: Comprehensive 7-phase implementation plan created for 200-point bonus suite
- 🧪 Tests: Constitution compliance validated, technical architecture defined
- 📁 Files: 1 file created (plan.md with detailed implementation phases)
- 🔁 Next prompts: /sp.tasks to create detailed task breakdown
- 🧠 Reflection: Plan addresses all governance requirements while enabling full feature implementation

## Evaluation notes (flywheel)

- Failure modes observed: None - planning completed successfully
- Graders run and results (PASS/FAIL): PASS - All constitution requirements met
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed to task generation with /sp.tasks