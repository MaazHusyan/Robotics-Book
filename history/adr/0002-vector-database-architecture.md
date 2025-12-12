# ADR-0002: Vector Database Architecture

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-12
- **Feature:** 001-rag-chatbot
- **Context:** The RAG chatbot requires efficient storage and retrieval of text embeddings from robotics book content. The system must handle semantic search across ~1000 content chunks with sub-second response times while maintaining cost efficiency and scalability for future growth.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

Adopt Qdrant Cloud as the vector database solution with optimized configuration for text similarity search:

- **Vector Storage**: Qdrant Cloud free tier with 768-dimensional vectors
- **Distance Metric**: Cosine similarity for optimal text embedding comparison
- **Index Type**: HNSW (Hierarchical Navigable Small World) for fast approximate search
- **Score Threshold**: 0.7 minimum similarity to filter irrelevant results
- **Collection**: Single "content_vectors" collection with comprehensive payload schema
- **Metadata**: Rich payload including source file, chapter, section, and content type
- **Scaling Strategy**: Start with free tier, scale to paid tier as content grows

## Consequences

### Positive

- **Performance**: HNSW index provides sub-100ms search times for typical queries
- **Cost Efficiency**: Free tier sufficient for current scale (~1000 vectors)
- **Developer Experience**: Managed service eliminates operational overhead
- **Semantic Quality**: Cosine similarity optimal for text embeddings
- **Scalability**: Clear upgrade path to paid tier as content grows
- **Filtering**: Score threshold reduces noise and improves relevance
- **Metadata Support**: Rich payload enables advanced filtering and analytics

### Negative

- **Vendor Lock-in**: Migrating away from Qdrant requires re-embedding all content
- **Free Tier Limits**: 1GB storage limit may require future migration
- **Network Dependency**: Cloud service introduces latency vs local deployment
- **Cost Uncertainty**: Paid tier pricing may become expensive at scale
- **Single Point of Failure**: Cloud service dependency for core functionality
- **Approximate Search**: HNSW may miss exact matches in some edge cases

## Alternatives Considered

**Alternative A: Self-Hosted Qdrant**
- Deploy Qdrant on own infrastructure (Docker/VPS)
- Pros: Full control, no storage limits, potentially lower cost at scale
- Cons: Operational overhead, maintenance burden, scaling complexity
- Rejected: Added operational complexity not justified for current scale

**Alternative B: Pinecone Vector Database**
- Managed vector database service optimized for production
- Pros: Excellent performance, auto-scaling, enterprise features
- Cons: Higher costs, proprietary lock-in, less flexible configuration
- Rejected: Cost structure not favorable for educational project budget

**Alternative C: PostgreSQL + pgvector Extension**
- Use existing Postgres with vector extension
- Pros: Single database for all data, transactional consistency, familiar stack
- Cons: Lower performance for high-dimensional vectors, limited indexing options
- Rejected: Performance limitations would impact user experience with >500ms query times

**Alternative D: Weaviate Vector Database**
- Open-source vector database with GraphQL API
- Pros: GraphQL interface, modular architecture, good documentation
- Cons: Steeper learning curve, smaller community, more complex setup
- Rejected: Qdrant provides better performance with simpler configuration for our use case

**Alternative E: In-Memory Vector Search**
- Use FAISS or similar library with in-memory storage
- Pros: Fastest possible performance, no network latency
- Cons: Memory limitations, no persistence, scaling challenges
- Rejected: Not suitable for persistent content storage and scaling requirements

## References

- Feature Spec: specs/001-rag-chatbot/spec.md
- Implementation Plan: specs/001-rag-chatbot/plan.md
- Research Findings: specs/001-rag-chatbot/research.md
- Data Model: specs/001-rag-chatbot/data-model.md
- Constitution: .specify/memory/constitution.md
- Related ADRs: ADR-0001 (AI Integration Stack), ADR-0003 (Real-time Communication)
