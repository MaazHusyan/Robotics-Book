---
id: 0002
title: project-hard-reset
stage: constitution
date: 2025-12-14
surface: cli
model: opencode
feature: none
branch: chatbot-integ
user: maaz
command: /sp.constitution
labels: [reset, constitution, cleanup]
links:
  spec: 
  ticket: 
  adr: 
  pr: 
files:
  - path: .specify/memory/constitution.md
    action: reset to template state v2.0.0
  - path: specs/
    action: cleared directory
  - path: history/prompts/001-robotics-book-spec/
    action: removed plan history files
  - path: .specify/templates/plan-template.md
    action: updated to generic template
  - path: .specify/templates/spec-template.md
    action: updated to generic template
  - path: .specify/templates/tasks-template.md
    action: updated to generic template
tests:
  - type: constitution-validation
    status: passed
    result: template placeholders correctly reset
---

## Prompt

HARD RESET ALL CONSTITUTIONS, SPECS, PLAN. reset all the context of this project history and use the only branch chatbot-integ

## Response snapshot

Performed complete project reset:
1. Reset constitution to template state v2.0.0 with fresh placeholders
2. Cleared specs directory (removed 001-robotics-book-spec)
3. Removed plan history files from history/prompts/001-robotics-book-spec/
4. Updated all templates to generic state (removed robotics-specific content)
5. Confirmed working on chatbot-integ branch
6. Created PHR record of reset operation

## Outcome

- ✅ Impact: Complete project context reset achieved
- 🧪 Tests: Constitution template validation passed
- 📁 Files: 6 files modified/reset, 1 directory cleared
- 🔁 Next prompts: Ready for fresh specification creation
- 🧠 Reflection: Successfully cleared all previous project context while preserving template structure

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS - All reset operations completed successfully
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test new specification creation workflow
