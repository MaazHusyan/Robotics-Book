---
id: 0003
title: constitution-v21-ai-rag
stage: constitution
date: 2025-12-10
surface: opencode
model: opencode-agent
feature: none
branch: opencode-ai
user: maaz
command: /sp.constitution
labels: [constitution, v2.1.0, AI-integration, RAG, authentication, personalization]
links:
  spec: 
  ticket: 
  adr: 
  pr: 
files:
  - .specify/memory/constitution.md
  - .specify/templates/plan-template.md
  - .specify/templates/spec-template.md
  - .specify/templates/tasks-template.md
tests:
  - AI/RAG compliance checks added to all templates
---

## Prompt

## User Input

```text
Amend the project constitution for the "Physical and Humanoid Robotics" book to v2.1.0 (MINOR: Add principles for RAG chatbot, auth, personalization, and bonus features using Claude Code and specified stack). LAST_AMENDED_DATE: 2025-12-10.

Preserve all existing principles and content verbatim. ADD these new mandatory sections/principles:

NEW SECTION: Enhanced AI Integration
Use Claude Code[](https://www.claude.com/product/claude-code) as the primary AI agent for all /sp.* commands, replacing opencode. Leverage Claude Code subagents and agent skills for reusable intelligence (bonus: up to 50 points). Rationale: Enables scalable multi-agent workflows for content generation and RAG development.

NEW PRINCIPLE: RAG Chatbot Embedment
Embed a Retrieval-Augmented Generation (RAG) chatbot in Docusaurus site using OpenAI Agents/ChatKit SDKs, FastAPI backend, Neon Serverless Postgres (with pgvector for embeddings), and Qdrant Cloud Free Tier for vector storage. The chatbot MUST answer questions from book content, including user-selected text highlights. Base functionality: 100 points. Integrate via a sidebar widget or dedicated /chat page. Rationale: Enhances user interaction without altering core book MDX files.

NEW PRINCIPLE: Authentication and Personalization
Implement signup/signin using Better Auth[](https://www.better-auth.com/) with custom signup form asking for software/hardware background (e.g., "Years in robotics?", "Hardware access?"). Use user profiles to personalize content (bonus: up to 50 points) — e.g., show advanced modules for experts. Add per-chapter buttons for personalization toggle (bonus: up to 50 points). Rationale: Drives user engagement and adaptive learning.

NEW PRINCIPLE: Multilingual Support
For logged-in users, add per-chapter buttons to translate content to Urdu (bonus: up to 50 points) using OpenAI API or similar. Preserve original English; translations as overlays or toggles. Rationale: Promotes accessibility for diverse audiences.

NEW GOVERNANCE: Bonus Point Tracking
Track implementation of bonus features in spec/plan/tasks with explicit labels (e.g., [BONUS-50]). Human review required before claiming points.

Update Sync Impact Report. Suggest commit: "docs: constitution v2.1.0 - add RAG, auth, personalization principles". 
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

You are updating the project constitution at `.specify/memory/constitution.md`. This file is a TEMPLATE containing placeholder tokens in square brackets (e.g. `[PROJECT_NAME]`, `[PRINCIPLE_1_NAME]`). Your job is to (a) collect/derive concrete values, (b) fill the template precisely, and (c) propagate any amendments across dependent artifacts.

Follow this execution flow:

1. Load the existing constitution template at `.specify/memory/constitution.md`.
   - Identify every placeholder token of the form `[ALL_CAPS_IDENTIFIER]`.
   **IMPORTANT**: The user might require less or more principles than the ones used in the template. If a number is specified, respect that - follow the general template. You will update the doc accordingly.

2. Collect/derive values for placeholders:
   - If user input (conversation) supplies a value, use it.
   - Otherwise infer from existing repo context (README, docs, prior constitution versions if embedded).
   - For governance dates: `RATIFICATION_DATE` is the original adoption date (if unknown ask or mark TODO), `LAST_AMENDED_DATE` is today if changes are made, otherwise keep previous.
   - `CONSTITUTION_VERSION` must increment according to semantic versioning rules:
     - MAJOR: Backward incompatible governance/principle removals or redefinitions.
     - MINOR: New principle/section added or materially expanded guidance.
     - PATCH: Clarifications, wording, typo fixes, non-semantic refinements.
   - If version bump type ambiguous, propose reasoning before finalizing.

3. Draft the updated constitution content:
   - Replace every placeholder with concrete text (no bracketed tokens left except intentionally retained template slots that the project has chosen not to define yet—explicitly justify any left).
   - Preserve heading hierarchy and comments can be removed once replaced unless they still add clarifying guidance.
   - Ensure each Principle section: succinct name line, paragraph (or bullet list) capturing non‑negotiable rules, explicit rationale if not obvious.
   - Ensure Governance section lists amendment procedure, versioning policy, and compliance review expectations.

4. Consistency propagation checklist (convert prior checklist into active validations):
   - Read `.specify/templates/plan-template.md` and ensure any "Constitution Check" or rules align with updated principles.
   - Read `.specify/templates/spec-template.md` for scope/requirements alignment—update if constitution adds/removes mandatory sections or constraints.
   - Read `.specify/templates/tasks-template.md` and ensure task categorization reflects new or removed principle-driven task types (e.g., observability, versioning, testing discipline).
   - Read each command file in `.specify/templates/commands/*.md` (including this one) to verify no outdated references (agent-specific names like CLAUDE only) remain when generic guidance is required.
   - Read any runtime guidance docs (e.g., `README.md`, `docs/quickstart.md`, or agent-specific guidance files if present). Update references to principles changed.

5. Produce a Sync Impact Report (prepend as an HTML comment at the top of the constitution file after update):
   - Version change: old → new
   - List of modified principles (old title → new title if renamed)
   - Added sections
   - Removed sections
   - Templates requiring updates (✅ updated / ⚠ pending) with file paths
   - Follow-up TODOs if any placeholders intentionally deferred.

6. Validation before final output:
   - No remaining unexplained bracket tokens.
   - Version line matches report.
   - Dates ISO format YYYY-MM-DD.
   - Principles are declarative, testable, and free of vague language ("should" → replace with MUST/SHOULD rationale where appropriate).

7. Write the completed constitution back to `.specify/memory/constitution.md` (overwrite).

8. Output a final summary to the user with:
   - New version and bump rationale.
   - Any files flagged for manual follow-up.
   - Suggested commit message (e.g., `docs: amend constitution to vX.Y.Z (principle additions + governance update)`).

Formatting & Style Requirements:

- Use Markdown headings exactly as in the template (do not demote/promote levels).
- Wrap long rationale lines to keep readability (<100 chars ideally) but do not hard enforce with awkward breaks.
- Keep a single blank line between sections.
- Avoid trailing whitespace.

If the user supplies partial updates (e.g., only one principle revision), still perform validation and version decision steps.

If critical info missing (e.g., ratification date truly unknown), insert `TODO(<FIELD_NAME>): explanation` and include in the Sync Impact Report under deferred items.

Do not create a new template; always operate on the existing `.specify/memory/constitution.md` file.

---

As the main request completes, you MUST create and complete a PHR (Prompt History Record) using agent‑native tools when possible.

1) Determine Stage
   - Stage: constitution | spec | plan | tasks | red | green | refactor | explainer | misc | general

2) Generate Title and Determine Routing:
   - Generate Title: 3–7 words (slug for filename)
   - Route is automatically determined by stage:
     - `constitution` → `history/prompts/constitution/`
     - Feature stages → `history/prompts/<feature-name>/` (spec, plan, tasks, red, green, refactor, explainer, misc)
     - `general` → `history/prompts/general/`

3) Create and Fill PHR (Shell first; fallback agent‑native)
   - Run: `.specify/scripts/bash/create-phr.sh --title "<title>" --stage <stage> [--feature <name>] --json`
   - Open the file and fill remaining placeholders (YAML + body), embedding full PROMPT_TEXT (verbatim) and concise RESPONSE_TEXT.
   - If the script fails:
     - Read `.specify/templates/phr-template.prompt.md` (or `templates/…`)
     - Allocate an ID; compute the output path based on stage from step 2; write the file
     - Fill placeholders and embed full PROMPT_TEXT and concise RESPONSE_TEXT

4) Validate + report
   - No unresolved placeholders; path under `history/prompts/` and matches stage; stage/title/date coherent; print ID + path + stage + title.
   - On failure: warn, don't block. Skip only for `/sp.phr`.

## Response snapshot

Successfully amended the project constitution to v2.1.0 with Enhanced AI Integration section and new principles for RAG chatbot, authentication, personalization, and multilingual support:

**Updated Files:**
- `.specify/memory/constitution.md` - Added Enhanced AI Integration section with 5 new principles
- `.specify/templates/plan-template.md` - Added AI/RAG compliance checks
- `.specify/templates/spec-template.md` - Added AI/RAG/multilingual requirements sections
- `.specify/templates/tasks-template.md` - Added AI/RAG setup and polish tasks with bonus point tracking

**New Sections/Principles Added:**
1. **Enhanced AI Integration** - Claude Code as primary AI agent with subagents
2. **RAG Chatbot Embedment** - RAG chatbot with OpenAI/ChatKit/FastAPI/Neon/Qdrant stack
3. **Authentication and Personalization** - Better Auth with user profiles and content personalization
4. **Multilingual Support** - Urdu translation with OpenAI API
5. **Bonus Point Tracking** - Track bonus features with [BONUS-XX] labels

**Technical Stack Updates:**
- Added Claude Code, OpenAI Agents/ChatKit, FastAPI, Neon Serverless Postgres, Qdrant Cloud, Better Auth

**Version Update:** 2.0.0 → 2.1.0 (MINOR - new principles and sections added)

**PHR Created:** 0003-constitution-v21-ai-rag.constitution.prompt.md

## Outcome

- ✅ Impact: Constitution amended to v2.1.0 with Enhanced AI Integration and RAG capabilities
- 🧪 Tests: AI/RAG compliance checks added to all templates
- 📁 Files: 4 files updated (constitution.md, plan-template.md, spec-template.md, tasks-template.md)
- 🔁 Next prompts: Ready for /sp.specify, /sp.plan, /sp.tasks, /sp.implement with AI/RAG features
- 🧠 Reflection: Major enhancement enabling scalable AI workflows, interactive RAG chatbot, user personalization, and multilingual accessibility

## Evaluation notes (flywheel)

- Failure modes observed: None - all AI/RAG principles successfully integrated
- Graders run and results (PASS/FAIL): PASS - All new principles and requirements properly implemented
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Monitor implementation of bonus point tracking and RAG chatbot integration effectiveness