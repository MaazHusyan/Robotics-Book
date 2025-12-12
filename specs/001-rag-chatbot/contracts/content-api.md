# API Contract: Content Management

**Version**: 1.0.0  
**Created**: 2025-12-10  
**Purpose**: REST API for content ingestion and management

## Authentication

API Key required for content management endpoints
```
Authorization: Bearer [management-api-key]
```

## Endpoints

### POST /api/ingest

Trigger content reindexing and vector embedding generation

**Request**:
```json
{
  "force": false,
  "files": ["docs/01-introduction/history.mdx", "docs/02-fundamentals/kinematics.mdx"]
}
```

**Response**:
```json
{
  "task_id": "ingest-task-uuid",
  "status": "started",
  "files_count": 15,
  "estimated_time_minutes": 3
}
```

### GET /api/ingest/{task_id}

Check ingestion status

**Response**:
```json
{
  "task_id": "ingest-task-uuid",
  "status": "in_progress",
  "progress": {
    "files_processed": 8,
    "total_files": 15,
    "chunks_created": 142,
    "vectors_generated": 142
  },
  "started_at": "2025-12-10T10:30:00Z",
  "estimated_completion": "2025-12-10T10:33:00Z"
}
```

### GET /api/content/stats

Content statistics and system health

**Response**:
```json
{
  "total_chunks": 1247,
  "total_files": 23,
  "last_updated": "2025-12-10T09:15:00Z",
  "vector_db_size": "2.3MB",
  "search_index_status": "healthy"
}
```

### DELETE /api/content/cache

Clear search cache and force reindex

**Response**:
```json
{
  "message": "Cache cleared successfully",
  "files_reindexed": 1247,
  "task_id": "reindex-task-uuid"
}
```

## Error Handling

| Status Code | Description |
|-------------|-------------|
| 401 | Invalid or missing API key |
| 403 | Insufficient permissions |
| 409 | Ingestion already in progress |
| 422 | Invalid request format |
| 429 | Rate limit exceeded |
| 500 | Internal server error |

## Rate Limiting

- **Ingestion**: 1 per 5 minutes per API key
- **Status checks**: 10 per minute per API key
- **Cache clear**: 1 per hour per API key

## Webhook Configuration

### GitHub Webhook

**Endpoint**: `/api/webhook/github`
**Events**: `push` to main branch
**Secret**: GitHub webhook secret verification

**Payload**:
```json
{
  "ref": "refs/heads/main",
  "repository": {
    "name": "Robotics-Book"
  },
  "commits": [
    {
      "id": "commit-sha",
      "added": ["docs/new-chapter.mdx"],
      "modified": ["docs/updated-chapter.mdx"],
      "removed": []
    }
  ]
}
```

**Response**:
```json
{
  "webhook_received": true,
  "triggered_ingestion": true,
  "task_id": "webhook-ingest-uuid"
}
```