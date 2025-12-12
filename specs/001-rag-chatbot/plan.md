# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: [e.g., Python 3.11, Swift 5.9, Rust 1.75 or NEEDS CLARIFICATION]  
**Primary Dependencies**: [e.g., FastAPI, OpenAI Agents SDK, Qdrant, Neon or NEEDS CLARIFICATION]  
**Storage**: [if applicable, e.g., Neon Serverless Postgres, Qdrant Cloud or N/A]  
**Testing**: [e.g., pytest, Jest, cargo test or NEEDS CLARIFICATION]  
**Target Platform**: [e.g., Linux server, embedded device, web app or NEEDS CLARIFICATION]
**Project Type**: [single/web/mobile - determines source structure]  
**Performance Goals**: [domain-specific, e.g., <2s response time, 1000 req/s or NEEDS CLARIFICATION]  
**Constraints**: [domain-specific, e.g., <200ms p95, <100MB memory, offline-capable or NEEDS CLARIFICATION]  
**Scale/Scope**: [domain-specific, e.g., 10k users, 1M documents, 50 chatbot endpoints or NEEDS CLARIFICATION]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Gemini RAG Chatbot Compliance (100% completion requirement)
- [ ] RAG chatbot embedded in published Docusaurus book
- [ ] Chatbot answers any question from whole book content
- [ ] Chatbot accepts selected/highlighted text as extra context
- [ ] Chatbot streams answers in real time via WebSocket
- [ ] OpenAI Agents Python SDK used with Gemini (OpenAI-compatible endpoint)
- [ ] Vectors stored in Qdrant Cloud (free tier)
- [ ] Metadata stored in Neon Serverless Postgres
- [ ] Backend implemented with FastAPI + WebSocket
- [ ] Chatbot is always-on and fully functional

### Optional Bonus Compliance (+100 points)
- [ ] Chatbot can run simple Python/ROS snippets on demand (optional)
- [ ] Python/ROS execution is safe and sandboxed (if implemented)

### Out of Scope Compliance (DO NOT IMPLEMENT)
- [ ] No new chapters beyond existing content
- [ ] No Urdu translation functionality
- [ ] No authentication or user survey system
- [ ] No personalization toggles
- [ ] No opencode subagents
- [ ] No additional MDX files beyond what exists

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |