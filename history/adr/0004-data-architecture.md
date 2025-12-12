# ADR-0004: Data Architecture

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-12
- **Feature:** 001-rag-chatbot
- **Context:** The RAG chatbot requires a multi-database architecture to handle different data types efficiently. The system must store content metadata, manage chat sessions, cache performance-critical data, and maintain vector embeddings while ensuring privacy, scalability, and cost efficiency for an educational platform.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

Adopt a hybrid multi-database architecture optimized for different data patterns and performance requirements:

- **Primary Database**: Neon Serverless Postgres for structured data and metadata
- **Vector Storage**: Qdrant Cloud for semantic search and embeddings
- **Caching Layer**: Redis for performance optimization and session management
- **Schema Design**: Separate tables for content chunks, chat sessions, and analytics
- **Privacy-First**: Anonymous access with hashed IP addresses and no PII storage
- **Data Relationships**: Foreign key relationships between content and session data
- **Indexing Strategy**: Optimized indexes for frequent query patterns
- **Backup Strategy**: Automated backups for critical metadata and analytics

## Consequences

### Positive

- **Performance Optimization**: Each database optimized for its specific data type and access patterns
- **Scalability**: Serverless architecture scales independently for each data store
- **Cost Efficiency**: Free tiers sufficient for current scale with clear upgrade paths
- **Privacy Compliance**: Anonymous access design with no PII storage requirements
- **Developer Experience**: Managed services reduce operational complexity
- **Query Performance**: Specialized indexes and caching ensure <2s response times
- **Analytics Ready**: Structured query logs enable performance monitoring and usage analysis

### Negative

- **Operational Complexity**: Multiple databases to monitor, maintain, and secure
- **Data Consistency**: Cross-database transactions not possible, requires application-level consistency
- **Vendor Lock-in**: Multiple vendor dependencies (Neon, Qdrant, Redis providers)
- **Cost Scaling**: Multiple services may become expensive at scale compared to monolithic approach
- **Backup Complexity**: Need separate backup strategies for each data store
- **Network Latency**: Cross-service communication adds latency vs single database
- **Debugging Difficulty**: Issues may span multiple services, making troubleshooting complex

## Alternatives Considered

**Alternative A: Single PostgreSQL Database**
- Use Postgres with pgvector for all data types including vectors
- Pros: Single service to manage, transactional consistency, simpler backup
- Cons: Poor vector search performance, limited scalability, complex queries
- Rejected: Performance limitations would violate <2s response time requirements

**Alternative B: MongoDB with Vector Search**
- Use MongoDB Atlas with built-in vector search capabilities
- Pros: Single database, unified API, good document flexibility
- Cons: Less mature vector search, higher costs, limited free tier
- Rejected: Higher costs and less performant vector search than dedicated solution

**Alternative C: Self-Hosted Stack**
- Self-hosted Postgres, Qdrant, and Redis on own infrastructure
- Pros: Full control, potentially lower costs at scale, no vendor limits
- Cons: Significant operational overhead, maintenance burden, scaling complexity
- Rejected: Operational complexity not justified for educational project scope

**Alternative D: Firebase/Supabase**
- Use Firebase or Supabase as integrated backend solution
- Pros: All-in-one solution, real-time capabilities, managed service
- Cons: Limited vector search, vendor lock-in, less control over performance
- Rejected: Inadequate vector search capabilities and performance for RAG use case

**Alternative E: In-Memory Only**
- Store all data in memory with periodic persistence
- Pros: Fastest possible performance, simple architecture
- Cons: Data loss on restart, memory limitations, no analytics persistence
- Rejected: Not suitable for persistent content storage and analytics requirements

## References

- Feature Spec: specs/001-rag-chatbot/spec.md
- Implementation Plan: specs/001-rag-chatbot/plan.md
- Research Findings: specs/001-rag-chatbot/research.md
- Data Model: specs/001-rag-chatbot/data-model.md
- Database Schema: specs/001-rag-chatbot/data-model.md#database-schema-neon-postgres
- Constitution: .specify/memory/constitution.md
- Related ADRs: ADR-0001 (AI Integration Stack), ADR-0002 (Vector Database Architecture), ADR-0003 (Real-time Communication)
