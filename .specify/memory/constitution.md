<!--
Sync Impact Report:
- Version change: 1.1.0 → 3.0.0 (MAJOR - complete scope reset to single-focus RAG chatbot)
- Modified principles: All previous bonus features removed, replaced with single RAG chatbot requirement
- Added sections: Gemini RAG Chatbot (sole deliverable), Optional Python/ROS Execution Bonus
- Removed sections: Integrated RAG Chatbot (50 points), opencode Code Subagents (50 points), Authentication + Background Survey (50 points), Personalization Toggle (50 points), Urdu Translation Toggle (50 points), Content Protection, Single Branch Discipline, Git Discipline, opencode Exclusive Usage, Feature Scope Limitation
- Templates requiring updates: ✅ plan-template.md, ✅ spec-template.md, ✅ tasks-template.md - all reset to RAG-only focus
- Follow-up TODOs: Regenerate existing specs/*/plan.md and tasks.md files
-->

# Physical & Humanoid Robotics Book with Live RAG Tutor Constitution

## Sole Deliverable

### Gemini RAG Chatbot (100% completion requirement)
The project passes and is considered 100% complete the moment a fully working, always-on, Gemini-powered RAG chatbot is embedded in the published Docusaurus book that can:

**Core Requirements (Mandatory):**
- Answer any question from the whole book content using RAG
- Accept selected/highlighted text as extra context
- Stream answers in real time via WebSocket
- Use OpenAI Agents Python SDK with Gemini (OpenAI-compatible endpoint)
- Store vectors in Qdrant Cloud (free tier)
- Store metadata in Neon Serverless Postgres
- Be implemented with FastAPI + WebSocket backend

**Integration Requirements:**
- Embedded directly in the published Docusaurus book
- Always-on and fully functional
- Real-time streaming responses
- Context-aware from user selections

## Optional Bonus (+100 points)

### Python/ROS Snippet Execution
Chatbot gains ability to run simple Python/ROS snippets on demand. This is optional and not mandatory for project completion.

## Out of Scope (Forever Declared)

The following features are officially out of scope and must not be implemented:
- All 7-chapter / 28-module content requirements → cancelled
- Urdu translation → cancelled  
- Authentication / Better Auth / survey → cancelled
- Personalization toggle → cancelled
- opencode subagents → cancelled
- Any remaining MDX files beyond what already exist → optional cosmetic only

## Content Rules

### Existing Chapters
- Existing chapters (1–3 or however many exist) stay as-is and are sufficient
- No new chapters are required
- Existing /docs/ folder content remains unchanged

## Governance

### Human Authority
Human owner has final authority over all project decisions.

### Amendment Process
Amendments only via new constitutional specification with clear justification.

### Versioning
Semantic versioning applies:
- MAJOR: Backward incompatible scope changes (like this reset)
- MINOR: New features added within current scope
- PATCH: Clarifications and non-semantic refinements

**Version**: 3.0.0 | **Ratified**: 2025-12-10 | **Last Amended**: 2025-12-10