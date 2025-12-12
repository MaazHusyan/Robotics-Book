---
id: 0003
title: rag-chatbot-task-generation
stage: tasks
date: 2025-12-10
surface: agent
model: opencode
feature: 001-rag-chatbot
branch: 001-rag-chatbot
user: maaz
command: /sp.tasks
labels: [tasks, rag-chatbot, implementation-plan]
links:
  spec: /specs/001-rag-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
- /specs/001-rag-chatbot/tasks.md
tests:
- Task completeness validation
- Constitution compliance check
- Implementation feasibility review
---

## Prompt

Create the official execution plan for feature 001-rag-chatbot.

Use exactly this technology stack (no alternatives, no discussion):
- LLM & Embeddings → Gemini via OpenAI-compatible endpoint (generativelanguage.googleapis.com/v1beta/openai/)
- Agent framework → OpenAI Agents Python SDK (pip install openai-agents)
- Vector store → Qdrant Cloud free tier
- Metadata DB → Neon Serverless Postgres (with pgvector extension optional)
- Backend → FastAPI + WebSocket (uvicorn)
- Frontend widget → React component in Docusaurus (src/components/RAGChat.tsx)
- Ingestion → LangChain + RecursiveCharacterTextSplitter + OpenAIEmbeddings (pointed at Gemini)
- Deployment → Render.com or Railway (free tier) for backend, GitHub Pages for Docusaurus

Deliver exactly these 12 tasks in this exact order (numbered T001–T012):

T001 – Create backend skeleton (folders, .env, requirements.txt, agents_config.py with Gemini redirect)
T002 – Neon connection + create metadata table (chunk_id, source_file, timestamp)
T003 – Qdrant collection creation script (768-dim for Gemini embeddings)
T004 – Ingestion script that loads all ../docs/**/*.mdx, chunks, embeds with Gemini, stores in Qdrant + Neon
T005 – Retrieval tool decorated with @tool for the OpenAI Agents SDK
T006 – Create a RAG agent (Robotics Book Tutor) with perfect system prompt and single retrieval tool
T007 – FastAPI main.py with /ws/chat WebSocket endpoint that streams Agent runs
T008 – Add CORS and health-check endpoint
T009 – Docusaurus RAGChat.tsx component with:
   • WebSocket connection
   • Real-time streaming
   • Text-selection detection (window.getSelection)
   • Auto-send selected text as context
T010 – Embed <RAGChat /> globally or on every page
T011 – Update README with one-click ingest command and deployment steps
T012 – Final end-to-end test case (highlight text → ask follow-up → correct streamed answer)

Mark every other possible task as "out of scope".  
Estimated total time: ≤3 hours.

Generate plan.md with these 12 tasks, clear acceptance criteria per task, and exact commands to run for each one.

## Response snapshot

Successfully generated comprehensive task breakdown with exactly 12 implementation tasks for Live Gemini RAG Tutor. Each task includes detailed acceptance criteria, complete code implementations, and specific commands to run.

Key deliverables created:
- tasks.md: 12 sequential tasks (T001-T012) covering backend skeleton, database setup, vector store, ingestion pipeline, agent creation, WebSocket API, frontend component, integration, documentation, and testing
- Each task includes complete code snippets and commands for immediate execution
- Technology stack strictly follows requirements: FastAPI, OpenAI Agents SDK, Gemini, Qdrant, Neon Postgres, React/Docusaurus
- Out-of-scope items clearly marked per constitution v3.0.0
- Estimated completion time: ≤3 hours

Task structure ensures systematic implementation:
1. Foundation (T001-T003): Backend skeleton, database, vector store
2. Core Logic (T004-T007): Content ingestion, retrieval tool, RAG agent, WebSocket API
3. Frontend (T008-T010): CORS, React component, Docusaurus integration
4. Completion (T011-T012): Documentation, end-to-end testing

All tasks are executable with clear acceptance criteria and ready for /sp.implement phase.

## Outcome

- ✅ Impact: Complete implementation roadmap with 12 executable tasks for RAG chatbot
- 🧪 Tests: Task completeness validated, constitution compliance verified, implementation feasibility confirmed
- 📁 Files: tasks.md created with detailed code snippets and commands for each task
- 🔁 Next prompts: Ready for /sp.implement to begin task execution
- 🧠 Reflection: Successfully balanced detailed implementation guidance with strict technology requirements and 3-hour time constraint

## Evaluation notes (flywheel)

- Failure modes observed: Multiple spec directories caused initial script errors, resolved by using correct feature path
- Graders run and results (PASS/FAIL): PASS - All 12 tasks generated with complete code, constitution compliance maintained, technology stack correctly implemented
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Monitor implementation phase for task execution time and code quality

---

## Prompt

{{PROMPT_TEXT}}

## Response snapshot

{{RESPONSE_TEXT}}

## Outcome

- ✅ Impact: {{OUTCOME_IMPACT}}
- 🧪 Tests: {{TESTS_SUMMARY}}
- 📁 Files: {{FILES_SUMMARY}}
- 🔁 Next prompts: {{NEXT_PROMPTS}}
- 🧠 Reflection: {{REFLECTION_NOTE}}

## Evaluation notes (flywheel)

- Failure modes observed: {{FAILURE_MODES}}
- Graders run and results (PASS/FAIL): {{GRADER_RESULTS}}
- Prompt variant (if applicable): {{PROMPT_VARIANT_ID}}
- Next experiment (smallest change to try): {{NEXT_EXPERIMENT}}
