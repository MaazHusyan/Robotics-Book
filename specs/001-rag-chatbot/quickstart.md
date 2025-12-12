# Quickstart Guide: Live Gemini RAG Tutor

**Date**: 2025-12-11  
**Purpose**: Setup and deployment guide for RAG chatbot system

## Prerequisites

### Required Services

1. **Neon Serverless Postgres**
   - Free tier account
   - Database connection string
   - Enable pgvector extension

2. **Qdrant Cloud**
   - Free tier account
   - API key and cluster URL
   - Create collection: `content_vectors`

3. **Google AI Studio**
   - Gemini API access
   - OpenAI-compatible endpoint URL
   - API key with sufficient quota

4. **GitHub Repository**
   - Main branch deployment
   - GitHub Pages enabled
   - Webhook configuration

### Local Development

```bash
# Python 3.11+ required
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn websockets openai qdrant-client psycopg2-binary python-multipart

# Environment variables
export DATABASE_URL="postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/db?sslmode=require"
export QDRANT_URL="https://xxx.aws.qdrant.cloud"
export QDRANT_API_KEY="your-qdrant-key"
export GEMINI_API_KEY="your-gemini-key"
export GITHUB_WEBHOOK_SECRET="your-webhook-secret"
```

## Installation

### Backend Setup

```bash
# Clone repository
git clone https://github.com/username/Robotics-Book.git
cd Robotics-Book

# Switch to feature branch
git checkout 001-rag-chatbot

# Create backend directory
mkdir -p backend/src
cd backend

# Create main application
touch src/main.py src/models.py src/services.py src/database.py
```

### Environment Configuration

Create `.env` file:
```bash
# Database
DATABASE_URL=postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/db?sslmode=require

# Vector Database
QDRANT_URL=https://xxx.aws.qdrant.cloud:6333
QDRANT_API_KEY=your-qdrant-key

# AI Service
GEMINI_API_KEY=your-gemini-key
OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/

# Security
GITHUB_WEBHOOK_SECRET=your-webhook-secret
CORS_ORIGIN=https://username.github.io

# Performance
MAX_CONCURRENT_USERS=50
RATE_LIMIT_PER_MINUTE=10
```

## Content Ingestion

### Initial Setup

```bash
# Run ingestion pipeline
python backend/scripts/ingest.py --source ../docs --force

# Monitor progress
python backend/scripts/ingest.py --status
```

### Automated Updates

1. **GitHub Webhook Setup**
   - Repository Settings → Webhooks → Add webhook
   - Payload URL: `https://your-backend.com/api/webhook/github`
   - Content type: `application/json`
   - Secret: Same as `GITHUB_WEBHOOK_SECRET`
   - Events: `Push` to main branch

2. **Debounced Reindexing**
   - Webhook triggers 30-second delay
   - Multiple pushes within window = single reindex
   - Automatic content update detection

## Local Development

### Backend Server

```bash
cd backend
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Test WebSocket connection
wscat -c ws://localhost:8000/api/chat
```

### Frontend Integration

```bash
# Install Docusaurus dependencies
npm install

# Swizzle chat component
npm run swizzle @docusaurus/theme-classic Footer -- --eject --typescript

# Create chat component
mkdir -p src/theme/RAGChat
touch src/theme/RAGChat/index.tsx src/theme/RAGChat/styles.css
```

### Testing

```bash
# Backend tests
cd backend && python -m pytest tests/

# Frontend tests
npm run test

# Integration tests
npm run test:integration
```

## Deployment

### Backend Deployment

```bash
# Option 1: Railway
railway login
railway link
railway up

# Option 2: Vercel (serverless)
vercel --prod

# Option 3: DigitalOcean App Platform
doctl apps create --spec spec.yaml
```

### Frontend Deployment

```bash
# Build Docusaurus site
npm run build

# Deploy to GitHub Pages
npm run deploy

# Or custom domain
npm run build -- --deploy-url https://your-domain.com
```

### Environment Variables in Production

Set in deployment platform:
- `DATABASE_URL`
- `QDRANT_URL` 
- `QDRANT_API_KEY`
- `GEMINI_API_KEY`
- `GITHUB_WEBHOOK_SECRET`
- `CORS_ORIGIN`

## Monitoring

### Health Checks

```bash
# Backend health
curl https://your-backend.com/api/health

# Content statistics
curl https://your-backend.com/api/content/stats

# WebSocket test
wscat -c wss://your-backend.com/api/chat
```

### Log Monitoring

```bash
# Application logs
railway logs

# Database queries
psql $DATABASE_URL -c "SELECT * FROM query_logs ORDER BY timestamp DESC LIMIT 10;"

# Vector database stats
curl -H "api-key: $QDRANT_API_KEY" $QDRANT_URL/collections/content_vectors
```

## Troubleshooting

### Common Issues

1. **CORS Errors**
   ```bash
   # Check CORS_ORIGIN matches deployment domain
   echo $CORS_ORIGIN
   ```

2. **Vector Database Connection**
   ```bash
   # Test Qdrant connection
   curl -H "api-key: $QDRANT_API_KEY" $QDRANT_URL/collections
   ```

3. **Slow Responses**
   ```bash
   # Check embedding model
   curl -H "Authorization: Bearer $GEMINI_API_KEY" \
        -H "Content-Type: application/json" \
        -d '{"model":"text-embedding-3-small","input":"test"}' \
        https://generativelanguage.googleapis.com/v1beta/openai/embeddings
   ```

4. **Content Not Found**
   ```bash
   # Re-run ingestion
   python backend/scripts/ingest.py --force --source ../docs
   ```

### Performance Tuning

```bash
# Optimize chunk size
python backend/scripts/ingest.py --chunk-size 800

# Adjust rate limits
export RATE_LIMIT_PER_MINUTE=20

# Monitor memory usage
python backend/scripts/monitor.py --metrics
```

## Security Considerations

### API Key Management

- Use environment variables, never commit keys
- Rotate keys quarterly
- Monitor usage quotas
- Implement key revocation process

### Rate Limiting

- IP-based limiting prevents abuse
- Burst capacity accommodates legitimate use
- Daily limits prevent excessive automated queries
- Anonymous access per constitution requirements

### Data Privacy

- No PII stored in database
- Query hashing for analytics
- Session data expires after 30 minutes
- Content-only responses prevent hallucinations

## Support

### Documentation

- API documentation: `/api/docs` (Swagger UI)
- Data model: `specs/001-rag-chatbot/data-model.md`
- Contracts: `specs/001-rag-chatbot/contracts/`

### Community

- Issues: GitHub repository issues
- Discussions: GitHub repository discussions
- Updates: Follow repository releases

### Backup and Recovery

```bash
# Database backup
pg_dump $DATABASE_URL > backup.sql

# Vector backup
curl -H "api-key: $QDRANT_API_KEY" \
     $QDRANT_URL/snapshots/create

# Content backup
tar -czf content-backup.tar.gz docs/
```