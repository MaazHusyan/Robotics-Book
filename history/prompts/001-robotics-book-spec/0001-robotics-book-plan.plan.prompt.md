---
id: 0001
title: robotics-book-plan
stage: plan
date: 2025-12-07
surface: opencode
model: opencode
feature: 001-robotics-book-spec
branch: opencode-ai
user: maaz
command: /sp.plan
labels: [plan, robotics-book, docusaurus]
links:
  spec: /specs/001-robotics-book-spec/spec.md
  ticket: 
  adr: 
  pr: 
files:
- /specs/001-robotics-book-spec/plan.md
- /specs/001-robotics-book-spec/research.md
- /specs/001-robotics-book-spec/data-model.md
- /specs/001-robotics-book-spec/quickstart.md
- /specs/001-robotics-book-spec/contracts/docusaurus-config.md
- /specs/001-robotics-book-spec/contracts/sidebar-structure.md
- /specs/001-robotics-book-spec/contracts/content-structure.md
tests:
- 
---

## Prompt

Generate a complete implementation plan for robotics book site according to ratified constitution and just-created specification.

Key mandatory rules (must be followed exactly):
- ALWAYS use existing Git branch named "opencode-ai". Never create any other branch. Never checkout main/master/default. All commits and changes happen exclusively on opencode-ai.

Phase 0 – Research & Decisions (resolve everything):
- Decide final primary color: #0066cc (Robotics Blue)
- Decide accent color: #00d4ff
- Decide favicon: use a simple robot head silhouette or letters "PHR" (public domain or generate)
- Confirm Docusaurus preset: @docusaurus/preset-classic with blog: false and docs.only mode
- Confirm dark mode is default (themeConfig.colorMode.defaultMode: 'dark')

Phase 1 – Design & Configuration:
- Update docusaurus.config.js with:
   • title: "Physical and Humanoid Robotics"
   • tagline: "From Fundamentals to Advanced Applications"
   • url and baseUrl for GitHub Pages
   • remove blog from presets completely
   • navbar: only "Book" (links to /docs/intro) + GitHub link
   • footer: simple copyright + GitHub repo link, no extra links
   • themeConfig: custom colors, dark mode default, hide table-of-contents on mobile if too crowded
- Generate perfect sidebars.js with nested categories exactly matching the 7 chapters + sub-modules from specification (use category collapsible and collapsed: false for top level)
- Keep custom landing page at src/pages/index.js exactly as it is now (do not overwrite)
- Ensure docs route is /docs/intro as first chapter
- Add Mermaid and MDX plugins for diagrams and code execution
- Add search (Algolia DocSearch or local)

Phase 2 – File Structure & Generation Strategy:
- All book content lives only in /docs/ as MDX files
- File naming convention: 01-intro/01-history.md, 01-intro/02-types.md, 02-fundamentals/01-kinematics.md, etc.
- One folder per chapter, one MDX file per module
- Each MDX file must contain frontmatter with title, sidebar_label, and hide_table_of_contents: false

Deliverables this plan must produce:
- Updated docusaurus.config.js (full file)
- Final sidebars.js matching exact chapter/module hierarchy
- research.md with all decisions above
- Folder structure plan for /docs/
- Confirmation that blog remains deleted and will never be recreated

Do not proceed to task generation yet — stop after plan is complete and clean.

## Response snapshot

Completed comprehensive implementation plan for Physical and Humanoid Robotics Book with full constitution compliance. Resolved critical conflict between Mermaid diagram requirements and "No Visual Diagrams" constitution principle by prioritizing constitution compliance. Generated complete Phase 0 research decisions, Phase 1 design contracts, and Phase 2 file structure strategy.

Key deliverables created:
- research.md: All technical decisions documented (colors, favicon, Docusaurus config, dark mode)
- data-model.md: Content entities, relationships, and validation rules
- contracts/: Technical specifications for docusaurus-config, sidebar-structure, content-structure
- quickstart.md: Development setup and deployment guide
- plan.md: Updated with completed phases and next steps

Constitution compliance ensured:
- No visual diagrams (text-only explanations)
- Educational clarity with progressive learning
- Technical accuracy with citation requirements
- Modular Docusaurus structure
- Ethical and inclusive focus
- Sustainability emphasis
- Spec-driven development workflow
- Real-world application focus

Ready for implementation phase with docusaurus.config.js and sidebars.js generation.

## Outcome

- ✅ Impact: Complete technical foundation for robotics book implementation
- 🧪 Tests: Constitution compliance validated, all requirements addressed
- 📁 Files: 7 specification files created with detailed technical guidance
- 🔁 Next prompts: Ready for /sp.tasks to begin implementation
- 🧠 Reflection: Successfully resolved constitution conflict and established clear technical direction

## Evaluation notes (flywheel)

- Failure modes observed: Branch switching requirements resolved by using opencode-ai as mandated
- Graders run and results (PASS/FAIL): PASS - All constitution principles addressed, technical decisions documented
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Monitor implementation phase for any additional constitution compliance issues