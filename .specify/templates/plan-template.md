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
**Primary Dependencies**: [e.g., FastAPI, UIKit, LLVM or NEEDS CLARIFICATION]  
**Storage**: [if applicable, e.g., PostgreSQL, CoreData, files or N/A]  
**Testing**: [e.g., pytest, XCTest, cargo test or NEEDS CLARIFICATION]  
**Target Platform**: [e.g., Linux server, iOS 15+, WASM or NEEDS CLARIFICATION]
**Project Type**: [single/web/mobile - determines source structure]  
**Performance Goals**: [domain-specific, e.g., 1000 req/s, 10k lines/sec, 60 fps or NEEDS CLARIFICATION]  
**Constraints**: [domain-specific, e.g., <200ms p95, <100MB memory, offline-capable or NEEDS CLARIFICATION]  
**Scale/Scope**: [domain-specific, e.g., 10k users, 1M LOC, 50 screens or NEEDS CLARIFICATION]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Educational Clarity Compliance
- [ ] Content uses simple language with technical terms defined on first use
- [ ] Includes practical examples and real-world robotics case studies
- [ ] Progressive concept building with clear learning objectives

### No Visual Diagrams Compliance
- [ ] All explanations are text-based only
- [ ] Complex concepts explained through descriptive text and code examples
- [ ] No diagrams, flowcharts, or visual representations in any files

### Technical Accuracy Compliance
- [ ] All robotics facts verified with reliable sources (IEEE, ROS docs, academic papers)
- [ ] Content is current as of 2025 with proper citations
- [ ] Technical claims have verifiable sources

### Modular Docusaurus Structure Compliance
- [ ] Content organized as modular chapters in MDX format
- [ ] Each chapter independently consumable
- [ ] Logical progression maintained throughout book structure

### Ethical and Inclusive Focus Compliance
- [ ] Robotics ethics discussions included (safety, societal impact, AI bias)
- [ ] Inclusive language used throughout
- [ ] Diverse global examples represented

### Sustainability in Robotics Compliance
- [ ] Examples promote energy-efficient designs
- [ ] Open-source tools highlighted (Gazebo, Arduino, ROS)
- [ ] Sustainable development practices emphasized

### Iterative Spec-Driven Development Compliance
- [ ] All changes follow spec-driven workflow
- [ ] AI-generated content includes minimum 20% human review
- [ ] Traceability and quality control maintained

### Real-World Application Focus Compliance
- [ ] Every technical concept accompanied by practical examples
- [ ] Theory connected to practice through working code examples
- [ ] Industry case studies or hands-on projects included

### Single Branch Discipline Compliance
- [ ] All development occurs exclusively on "opencode-ai" branch
- [ ] No other branches created, checked out, or referenced
- [ ] All /sp.* commands respect branch discipline

### Content Protection Compliance
- [ ] No existing book content files modified without explicit permission
- [ ] Files under /docs/, /src/pages/, and MDX files protected
- [ ] Placeholder content replacement only when authorized

### PHR Enforcement Compliance
- [ ] Every /sp.* command creates complete PHR entry
- [ ] PHR correctly placed in history/prompts/ folder
- [ ] Stage-based routing followed (constitution/, robotics-book/, general/)

### Git Discipline Compliance
- [ ] Git commands prompted after every /sp.* command that modifies files
- [ ] Clear commit message provided with exact commands
- [ ] No auto-commit or auto-push without explicit confirmation
- [ ] Next phase waits for human confirmation of push completion

### Versioning & Traceability Compliance
- [ ] All generated files include header comment with constitution version
- [ ] Date and time of generation included
- [ ] Git branch specified (must be opencode-ai)
- [ ] Link to PHR entry provided

### Preservation of Human Oversight Compliance
- [ ] AI generates drafts but final judgment remains with human owner
- [ ] No assumption of approval without explicit confirmation
- [ ] Quality, accuracy, and style decisions reserved for human

### Enhanced AI Integration Compliance
- [ ] opencode CLI used as exclusive AI agent for all /sp.* commands
- [ ] No other AI agents (Claude Code, Claude, Cursor, etc.) used or referenced
- [ ] Bonus point tracking implemented with [BONUS-50] labels where applicable

### RAG Chatbot Embedment Compliance
- [ ] RAG chatbot embedded in Docusaurus site using specified stack
- [ ] OpenAI Agents/ChatKit SDKs integrated with FastAPI backend
- [ ] Neon Serverless Postgres with pgvector configured for embeddings
- [ ] Qdrant Cloud Free Tier used for vector storage
- [ ] Chatbot answers questions from book content including text highlights
- [ ] Integration via sidebar widget or dedicated /chat page

### Authentication and Personalization Compliance
- [ ] Better Auth implemented for signup/signin functionality
- [ ] Custom signup form collects software/hardware background
- [ ] User profiles used to personalize content (advanced modules for experts)
- [ ] Per-chapter buttons added for personalization toggle
- [ ] Bonus point tracking for personalization features

### Multilingual Support Compliance
- [ ] Per-chapter buttons added for Urdu translation
- [ ] OpenAI API used for translation functionality
- [ ] Original English content preserved
- [ ] Translations provided as overlays or toggles
- [ ] Bonus point tracking for multilingual features

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
