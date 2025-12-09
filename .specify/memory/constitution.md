<!--
Sync Impact Report:
- Version change: 2.1.0 → 2.2.0 (MINOR - authorize Integrated RAG Chatbot)
- Modified principles: None (all existing preserved)
- Added sections: Integrated RAG Chatbot (Requirement 2)
- Removed sections: None
- Templates requiring updates: ⚠ pending - plan-template.md, spec-template.md, tasks-template.md need RAG authorization
- Follow-up TODOs: None
-->

# Physical and Humanoid Robotics Book Constitution

## Core Principles

### Educational Clarity
Content MUST prioritize accessible explanations for beginners to intermediate readers using simple language, practical analogies, code examples, and real-world robotics case studies. Concepts build progressively with clear learning objectives and practical applications that readers can immediately relate to and implement.

### No Visual Diagrams
All content MUST be text-based only. No diagrams, flowcharts, or visual representations are permitted in any file. Complex concepts MUST be explained through descriptive text, code examples, and structured lists that readers can follow without visual aids.

### Technical Accuracy
All robotics content covering mechanics, kinematics, sensors, AI integration, humanoid design, and ethics MUST be factually correct, current as of 2025, and cited from reliable sources including IEEE publications, ROS documentation, peer-reviewed academic papers, and established industry standards. All technical claims MUST have verifiable sources.

### Modular Docusaurus Structure
Content MUST be organized as modular chapters with sub-modules in MDX format for Docusaurus, enabling easy navigation, interactive elements (embedded code, mathematical expressions), and extensibility. Each chapter MUST be independently consumable while maintaining logical progression through the book.

### Ethical and Inclusive Focus
Content MUST incorporate comprehensive discussions on robotics ethics including safety considerations, societal impact, AI bias, and responsible development. Language MUST be inclusive with diverse global examples that represent different cultural perspectives and applications of robotics technology.

### Sustainability in Robotics
Examples and case studies MUST promote energy-efficient designs, open-source tools (Gazebo, Arduino, ROS), and sustainable development practices. Content SHOULD highlight environmental considerations in robotics design, manufacturing, and deployment while advocating for responsible resource usage.

### Iterative Spec-Driven Development
All content changes MUST use specifications as first-class artifacts, with AI-generated drafts requiring minimum 20% human review and refinement. Each modification MUST follow the spec-driven workflow ensuring traceability, quality control, and systematic content evolution.

### Real-World Application Focus
Every technical concept MUST be accompanied by practical examples, case studies, or implementation scenarios that demonstrate real-world applicability. Theory MUST be immediately connected to practice through working code examples, industry case studies, or hands-on projects.

## Governance Principles

### Single Branch Discipline
All development, specification, planning, task generation and implementation MUST occur exclusively on the Git branch named "opencode-ai". No other branch may ever be created, checked out, or referenced by any /sp.* command or generated script.

### Content Protection
No existing file containing book content (any file under /docs/, /src/pages/, or any MDX/MDX file) may be modified, overwritten, or deleted without explicit written permission from the human owner in the same command. Placeholder or dummy content may be replaced only when explicitly authorised.

### Prompt History Record (PHR) Enforcement
Every single /sp.* command (constitution, specify, plan, tasks, implement, etc.) MUST automatically create a complete, correctly placed Prompt History Record in the history/prompts/ folder using the official stage-based routing:
- /sp.constitution → history/prompts/constitution/
- /sp.specify, /sp.plan, /sp.tasks, /sp.implement → history/prompts/robotics-book/
- All others → history/prompts/general/
Failure to create a valid PHR is a constitutional violation.

### Git Discipline After Every /sp Command
After completion of ANY /sp.* command that modifies files, the system MUST:
1. Prompt the human with the exact git commands to run
2. Clearly state: "Please run: git add . && git commit -m '<suggested message>' && git push origin opencode-ai"
3. Never auto-commit or auto-push without explicit confirmation
4. Never proceed to the next phase until the human confirms the push is done

### Versioning & Traceability
All generated tasks.md, plan.md, spec.md and constitution.md MUST include a header comment with:
- Constitution version applied
- Date and time of generation
- Git branch used (must be opencode-ai)
- Link to the PHR entry

### Preservation of Human Oversight
AI may generate drafts and execute tasks, but final judgement on quality, accuracy, and style remains with the human owner. The AI must never assume approval.

### Single Branch Forever
All work — past, present, and future — MUST occur exclusively on Git branch "opencode-ai". No other branch may ever be created, checked out, or mentioned.

### Content Protection Lock
No existing book content (any file under /docs/, any MDX file, sidebars.js, or src/pages/) may be modified, overwritten, or deleted without explicit written permission in the same command.

### PHR Enforcement
Every single /sp.* command MUST automatically create a complete Prompt History Record in the correct history/prompts/ subfolder (constitution → /constitution/, all others → /robotics-book/).

### Git Discipline
After any /sp.* command that modifies files, the system MUST stop and display:
"Please run: git add . && git commit -m '<suggested message>' && git push origin opencode-ai"
Auto-commit or auto-push is forbidden.

### Human Final Say
The human owner has absolute veto power over any generated content or change.

## Enhanced AI Integration

### opencode CLI Primary Agent
Use opencode CLI as exclusive AI agent for all /sp.* commands and implementation tasks. No other AI agent (including Claude Code, Claude, Cursor, etc.) may be used or referenced. Rationale: Ensures consistent tooling and governance compliance across all development activities.

### RAG Chatbot Embedment
Embed a Retrieval-Augmented Generation (RAG) chatbot in Docusaurus site using OpenAI Agents/ChatKit SDKs, FastAPI backend, Neon Serverless Postgres (with pgvector for embeddings), and Qdrant Cloud Free Tier for vector storage. The chatbot MUST answer questions from book content, including user-selected text highlights. Base functionality: 100 points. Integrate via a sidebar widget or dedicated /chat page. Rationale: Enhances user interaction without altering core book MDX files.

### Integrated RAG Chatbot (Requirement 2 – 100 points)
The project MUST embed a fully functional Retrieval-Augmented Generation chatbot using:
- OpenAI Agents / ChatKit SDKs
- FastAPI backend
- Neon Serverless Postgres (with pgvector extension)
- Qdrant Cloud Free Tier as vector store
The chatbot MUST be reachable from the published Docusaurus book and answer:
  • Any question about the entire book content
  • Questions based ONLY on text the user explicitly selects/highlights
The chatbot UI will be embedded as a floating widget or /chat page without modifying existing /docs/*.mdx content.
All ingestion pipelines and backend services are permitted under this constitution.
Rationale: This is the official second requirement of the challenge.

### Authentication and Personalization
Implement signup/signin using Better Auth with custom signup form asking for software/hardware background (e.g., "Years in robotics?", "Hardware access?"). Use user profiles to personalize content (bonus: up to 50 points) — e.g., show advanced modules for experts. Add per-chapter buttons for personalization toggle (bonus: up to 50 points). Rationale: Drives user engagement and adaptive learning.

### Multilingual Support
For logged-in users, add per-chapter buttons to translate content to Urdu (bonus: up to 50 points) using OpenAI API or similar. Preserve original English; translations as overlays or toggles. Rationale: Promotes accessibility for diverse audiences.

### Bonus Point Tracking
Track implementation of bonus features in spec/plan/tasks with explicit labels (e.g., [BONUS-50]). Human review required before claiming points.

## Content Standards

### Technical Stack Requirements
- Platform: Docusaurus v2+ with MDX support
- Deployment: GitHub Pages with automated CI/CD
- Version Control: Git with semantic versioning for content releases
- Code Examples: Python, C++, and JavaScript for robotics simulations
- Simulation Tools: Gazebo, ROS 2, and Web-based simulators
- AI Agent: opencode CLI as exclusive AI agent for all /sp.* commands
- RAG Backend: FastAPI with OpenAI Agents/ChatKit SDKs
- Database: Neon Serverless Postgres with pgvector for embeddings
- Vector Storage: Qdrant Cloud Free Tier for vector storage
- Authentication: Better Auth with custom signup forms
- Translation: OpenAI API for multilingual support (Urdu)

### Writing Style Guidelines
- Tone: Engaging mentor voice that guides readers through complex topics
- Chapter Length: 2000-5000 words per chapter with clear subsections
- Code Integration: Executable code blocks with syntax highlighting and explanations
- Citation Format: IEEE style with links to online sources
- Language: Simple, direct sentences with technical terms defined on first use

### Quality Assurance Requirements
- All content MUST pass manual technical review by subject matter experts
- Code examples MUST be tested and verified to work with specified versions
- Citations MUST be current (within 3 years for rapidly evolving topics)
- Each chapter MUST include learning objectives, summary, and practical exercises
- Content MUST be accessible to readers with visual impairments (alt text, screen reader compatibility)

## Development Guidelines

### AI Usage Policy
AI tools MAY be used for initial drafts, research assistance, and code generation but MUST NOT replace human expertise. All AI-generated content requires minimum 20% human modification, fact-checking, and enhancement. Final responsibility for accuracy and quality rests with human authors.

### Review Process
- Draft Phase: AI-assisted initial content creation
- Technical Review: Subject matter expert validation
- Editorial Review: Clarity, accessibility, and style consistency
- Ethics Review: Bias assessment and inclusive language verification
- Final Approval: Human owner sign-off before publication

### Success Metrics
- 100% spec coverage for all content changes
- Zero deployment errors on GitHub Pages
- Reader comprehension scores above 85% through feedback mechanisms
- Code example execution success rate above 95%
- Citation accuracy and currency compliance rate of 100%

## Governance

### Authority Structure
The human project owner maintains final authority on all content decisions, including principle interpretation, amendment approval, and conflict resolution. Technical experts provide advisory input but do not have veto power over final decisions.

### Amendment Process
Constitution amendments MUST be proposed via new specification using the `/sp.constitution` command with detailed justification, impact analysis, and implementation plan. Amendments require majority approval from maintainers and MUST follow semantic versioning principles.

### Compliance Requirements
All content MUST comply with ethical standards, legal requirements, and accessibility guidelines. This includes adherence to copyright laws, privacy regulations, data protection standards, and web accessibility guidelines (WCAG 2.1 AA or higher).

### Versioning Policy
Constitution follows semantic versioning: MAJOR for backward-incompatible changes, MINOR for new principles or sections, PATCH for clarifications and corrections. All changes MUST be documented in git commit history with clear rationale and impact assessment.

**Version**: 2.2.0 | **Ratified**: 2025-12-07 | **Last Amended**: 2025-12-10