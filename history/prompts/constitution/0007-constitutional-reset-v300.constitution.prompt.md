---
id: 0007
title: constitutional-reset-v300
stage: constitution
date: 2025-12-10
surface: opencode
model: opencode
feature: none
branch: main
user: maaz
command: /sp.constitution
labels: [constitution, reset, v300, rag-chatbot]
links:
  spec: 
  ticket: 
  adr: 
  pr: 
files:
  - .specify/memory/constitution.md
  - .specify/templates/spec-template.md
  - .specify/templates/plan-template.md
  - .specify/templates/tasks-template.md
tests:
  - No tests required for constitutional reset
---

## Prompt

Total constitutional reset to v3.0.0 – single-focus project.

New reality (non-negotiable):

Project name: "Physical & Humanoid Robotics Book with Live RAG Tutor"
Only one deliverable now counts: a fully working, always-on, Gemini-powered RAG chatbot embedded in the published Docusaurus book that can:
• Answer any question from the whole book content
• Accept selected/highlighted text as extra context
• Stream answers in real time via WebSocket
• Use OpenAI Agents Python SDK + Gemini (OpenAI-compatible endpoint)
• Store vectors in Qdrant Cloud (free tier)
• Store metadata in Neon Serverless Postgres
• Be implemented with FastAPI + WebSocket

Everything else is now officially declared out of scope forever:
• All 7-chapter / 28-module content requirements → cancelled
• Urdu translation → cancelled
• Authentication / Better Auth / survey → cancelled
• Personalization toggle → cancelled
• opencode subagents → cancelled
• Any remaining MDX files beyond what already exist → optional cosmetic only

Constitution v3.0.0 rules:
1. The project passes and is considered 100% complete the moment the RAG chatbot is live and working.
2. Existing chapters (1–3 or however many you have) stay as-is and are sufficient.
3. No new chapters are required.
4. The only acceptable bonus (+100 points) is making the chatbot also able to run simple Python/ROS snippets on demand (optional, not mandatory).

Version bump: 3.0.0 (MAJOR – complete scope reset)
Ratification date: keep original, last amended = today.

Completely overwrite and reset these files to match the new reality:
• .specify/templates/spec-template.md
• .specify/templates/plan-template.md
• .specify/templates/tasks-template.md
• all existing specs/*/plan.md and tasks.md (regenerate or delete)

Produce a clean Sync Impact Report that shows every old requirement marked as "removed – out of scope".

Give me a commit message like "chore: constitutional reset v3.0.0 – sole focus on Gemini RAG chatbot".

## Response snapshot

Constitutional reset v3.0.0 completed successfully. Updated:
- Constitution to single-focus RAG chatbot deliverable
- All template files to remove out-of-scope requirements
- Deleted existing plan.md and tasks.md files from specs
- Created comprehensive Sync Impact Report

## Outcome

- ✅ Impact: Complete scope reset to RAG chatbot-only focus
- 🧪 Tests: No tests required for constitutional reset
- 📁 Files: Updated constitution.md, all template files, deleted out-of-scope specs
- 🔁 Next prompts: New spec creation for RAG chatbot implementation
- 🧠 Reflection: Major simplification achieved - project now has clear, achievable goal

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Create new RAG chatbot specification
