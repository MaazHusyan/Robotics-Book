<!--
Sync Impact Report:
- Version change: 2.0.0 → 2.1.0 (MINOR - Added RAG Chatbot feature principles and technical requirements)
- Modified principles: Template placeholders replaced with RAG Chatbot specific principles
- Added sections: RAG Chatbot technical stack, AI usage policy, performance metrics
- Removed sections: Reset context section (replaced with active feature context)
- Templates requiring updates: ✅ updated - plan-template.md, spec-template.md, tasks-template.md aligned with RAG principles
- Follow-up TODOs: None
-->

# RAG Chatbot Integration Constitution

## Core Principles

### User-Centric RAG Design
Chatbot responses MUST be accurate, relevant to robotics book content, and enhanced by user-selected text context. The system MUST prioritize user intent and provide contextualized answers that directly address queries about the Physical and Humanoid Robotics book content.

### Content Integrity
Chatbot responses MUST only reference actual book content with clear source attribution. All answers MUST include citations to specific book sections, chapters, or page references. The system MUST NOT hallucinate information or generate content beyond the documented book material.

### Performance & Scalability
Chatbot MUST deliver fast retrieval and response times using serverless architecture. Response time for typical queries MUST be under 5 seconds (3-5 seconds target). The system MUST scale efficiently using Neon serverless Postgres and Qdrant Cloud Free Tier without performance degradation.

## Content Standards

### Technical Stack Requirements
- Platform: Docusaurus 3.9.2 + React 19.0.0 (frontend), FastAPI (backend)
- Vector DB: Qdrant Cloud Free Tier
- Database: Neon Serverless Postgres
- LLM Integration: OpenAI Agents SDK with Gemini model and API
- API Communication: REST API (FastAPI)
- Deployment: GitHub Pages (frontend), Serverless (backend)
- Version Control: Git with semantic versioning
- Code Examples: Python (FastAPI backend), TypeScript/JSX (React components)
- Additional Tools: OpenAPI/Swagger for API documentation

### Writing Style Guidelines
- Tone: Technical and precise for API documentation, user-friendly for chatbot responses
- Content Length: Concise API endpoints, comprehensive chatbot responses
- Code Integration: Well-documented React components with prop types, FastAPI with Pydantic models
- Citation Format: IEEE style with links to online sources for book content
- Language: English with clear technical terminology definitions

### Quality Assurance Requirements
- RAG answer accuracy testing with sample robotics book questions
- Response time benchmarks under 5 seconds for typical queries (3-5 second target)
- Vector search relevance scoring above 0.8 threshold
- Text selection feature reliability testing with 99% success rate
- API error handling and resilience testing with graceful degradation

## Development Guidelines

### AI Usage Policy
All code generation, prompts, and documentation creation MUST be done via AI tools. AI-generated code MUST be reviewed for accuracy, security, and performance before integration. Human oversight is required for final approval of all AI-generated content.

### Review Process
- Code review before merging to ensure quality and security standards
- Test execution for QA validation of all features
- Performance testing to meet response time requirements
- Content accuracy validation against robotics book source material

### Success Metrics
- Chatbot successfully embedded in Docusaurus site
- Can answer book-related questions with 95% accuracy
- Text selection feature works reliably with 99% success rate
- Response time consistently under 5 seconds for typical queries (3-5 second target)
- User satisfaction score above 4.5/5.0 for chatbot interactions

## Governance

### Authority Structure
Feature owner (user) makes final decisions on all aspects of RAG Chatbot integration. Technical decisions require alignment with project's opencode.md spec-driven development rules. Architecture changes must be approved by feature owner.

### Amendment Process
Update constitution via `/sp. constitution rag-chatbot` command. All amendments MUST follow semantic versioning principles and include detailed justification for changes. Amendments require feature owner approval before implementation.

### Compliance Requirements
All development MUST follow project's opencode.md principles and spec-driven development workflow. Code MUST adhere to security best practices, accessibility standards, and performance requirements. Integration MUST not disrupt existing Docusaurus functionality.

### Versioning Policy
Constitution follows semantic versioning: MAJOR for backward-incompatible changes, MINOR for new features or principles, PATCH for clarifications and corrections. All changes MUST be documented in git commit history with clear rationale and impact assessment.

**Version**: 2.1.0 | **Ratified**: 2025-12-14 | **Last Amended**: 2025-12-14