# AGENTS.md - Development Guidelines

## Build Commands
- `npm start` - Start development server (http://localhost:3000)
- `npm run build` - Build production bundle
- `npm run serve` - Serve built files locally
- `npm run clear` - Clear Docusaurus cache
- `npm run swizzle` - Customize Docusaurus components

## Code Style Guidelines

### JavaScript/React Components
- Use ES6+ imports/exports (no CommonJS)
- Functional components with hooks preferred over class components
- Use `@ts-check` JSDoc for type checking in JS files
- Import order: React/Docusaurus imports → external libraries → local imports
- Use clsx for conditional CSS classes
- Component files: PascalCase naming (e.g., HomepageFeatures.js)

### MDX Content Files
- Frontmatter required: title, sidebar_label, description
- Use kebab-case for file names (e.g., history-and-evolution.mdx)
- Hide table of contents with `hide_table_of_contents: false` when needed
- Use learning objectives with checkbox format for educational content

### Configuration
- Docusaurus config uses TypeScript JSDoc annotations
- Dark mode as default (`defaultMode: 'dark'`)
- Custom theme colors: primary '#0066cc', secondary '#00d4ff'
- Base URL: '/Robotics-Book/' for GitHub Pages deployment

### File Structure
- Docs organized in numbered directories (01-introduction/, 02-physical-fundamentals/, etc.)
- Components in src/components/ with accompanying CSS modules
- Static assets in static/img/
- Sidebar structure defined in sidebars.js with category hierarchy

## MCP Integration

### Context7 MCP Server
This project includes Context7 MCP server integration for up-to-date code documentation:

**Configuration Files:**
- `mcp.json` - Local MCP server configuration
- `opencode.json` - Opencode-specific MCP configuration

**Setup:**
1. Get API key from [context7.com/dashboard](https://context7.com/dashboard)
2. Replace `YOUR_API_KEY` in configuration files
3. Use `use context7` in prompts or set up auto-invoke rules

**Available Tools:**
- `resolve-library-id` - Find library IDs
- `get-library-docs` - Fetch documentation with optional topic filtering

## Active Technologies
- Python 3.11 + FastAPI, OpenAI Agents SDK, Qdrant Client, Neon Postgres, WebSockets (001-rag-chatbot)
- Neon Serverless Postgres (metadata), Qdrant Cloud (vectors) (001-rag-chatbot)
- Python 3.11 + FastAPI 0.104.1, OpenAI Agents SDK 0.7.0, Qdrant Client 1.7.0, psycopg2-binary 2.9.9, uvicorn 0.24.0, python-multipart 0.0.6, python-dotenv 1.0.0, langchain 0.1.0, redis 5.0.1 (001-rag-chatbot)
- Neon Serverless Postgres (metadata), Qdrant Cloud (vectors), Redis (caching) (001-rag-chatbot)

## Recent Changes
- 001-rag-chatbot: Added Python 3.11 + FastAPI, OpenAI Agents SDK, Qdrant Client, Neon Postgres, WebSockets
