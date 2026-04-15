# Arkive — Enterprise Intelligence Platform

**Author:** Abduttayyeb  
**Stack:** SvelteKit 5 + FastAPI + SQLAlchemy + Socket.IO  
**Purpose:** A self-hosted, multi-model AI workspace for teams — covering chat, retrieval, collaboration, knowledge management, agents/tools, and admin governance.

---

## 1. Project Identity

Arkive is a full-stack enterprise AI platform. It is **not** a thin wrapper around a single model API. It is a first-class product with:

- A persistent database of users, chats, notes, knowledge bases, tools, and settings
- A pluggable model routing layer that speaks to Ollama, OpenAI-compatible endpoints, Anthropic, and pipelines
- A retrieval-augmented generation (RAG) pipeline with multiple vector database backends
- Team collaboration features: channels, folders, shared chats, webhooks
- Admin governance: RBAC groups, audit logs, analytics, evaluations, and fine-grained feature flags
- Browser-side Python execution via Pyodide and backend-side tool/terminal execution

The codebase was forked from Open WebUI and has been comprehensively rebranded and extended. There must be **zero references** to "Open WebUI" anywhere — the product name is always **Arkive**.

---

## 2. Technology Stack

### Frontend

| Layer | Technology |
|-------|-----------|
| Framework | SvelteKit 5 (with `@sveltejs/adapter-node` for SSR/static) |
| Language | TypeScript throughout (`lang="ts"` in all script blocks) |
| Styling | Tailwind CSS |
| Rich text editor | Tiptap (with custom extensions: image, file-handler, drag-handle, bubble menu, YouTube, tables, code blocks) |
| Code editor | CodeMirror 6 (Python, JavaScript, language data) |
| Charts | Chart.js (auto import, lazy loaded) |
| Browser AI | `@huggingface/transformers` (in-browser embedding), `@mediapipe/tasks-vision` (vision models) |
| Python in browser | Pyodide + PyScript (`@pyscript/core`) |
| Realtime | Socket.IO client |
| Auth | Azure MSAL (`@azure/msal-browser`) for Microsoft OAuth flows |
| I18n | i18next |
| Notifications | svelte-sonner (toast) |
| Markdown | marked + DOMPurify + highlight.js + KaTeX |
| Drag and drop | SortableJS |

### Backend

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI 0.135 + Uvicorn |
| Language | Python 3.11–3.12 |
| ORM | SQLAlchemy 2 + Alembic (migrations) |
| Default DB | SQLite (WAL optional) |
| Production DB | PostgreSQL + pgvector supported |
| Realtime | python-socketio (Socket.IO) |
| Auth | JWT (python-jose), bcrypt, argon2, PyJWT, Authlib (OAuth), python-ldap |
| Cache/Sync | Redis (optional, for multi-node config sync and Socket.IO pub/sub) |
| HTTP client | httpx + aiohttp |
| Compression | starlette-compress + Brotli |
| Sessions | starsessions (Redis-backed sessions optional) |
| PDF generation | WeasyPrint |

### Data & Infrastructure

| Concern | Options |
|---------|---------|
| Vector DB | Chroma (default), pgvector, Qdrant, Weaviate, Milvus, OpenSearch, Elasticsearch, Pinecone, MariaDB vector, Oracle 23ai, S3Vector, OpenGauss |
| Embeddings | Sentence Transformers (local), OpenAI embeddings, Ollama embeddings, HuggingFace in-browser |
| Reranking | Cross-encoder models (local), external rerank APIs |
| Object storage | Local filesystem (`backend/data/uploads`), pluggable |
| Task queue | Background tasks via FastAPI `BackgroundTasks` |

---

## 3. High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        Browser (SvelteKit SPA)                    │
│                                                                    │
│  ┌───────────┐  ┌──────────┐  ┌──────────┐  ┌────────────────┐  │
│  │   Chat    │  │ Workspace│  │  Admin   │  │    Channels    │  │
│  │ (Svelte)  │  │ (Svelte) │  │ (Svelte) │  │   (Svelte)     │  │
│  └─────┬─────┘  └────┬─────┘  └────┬─────┘  └───────┬────────┘  │
│        │              │              │                 │           │
│        └──────────────┴──────────────┴─────────────────┘          │
│                             │                                      │
│                    src/lib/apis/*  (fetch wrappers)               │
│                             │                                      │
│              Socket.IO client (/ws)  ←────────────────────────┐  │
└─────────────────────────────┼──────────────────────────────────┼──┘
                              │ HTTP/REST                         │ WS
┌─────────────────────────────▼──────────────────────────────────┼──┐
│                        FastAPI Application                       │  │
│                       (backend/arkive/main.py)                  │  │
│                                                                  │  │
│  ┌───────────────────────────────────────────────────────────┐  │  │
│  │                     API Routers (/api/v1/*)               │  │  │
│  │  auths  users  chats  channels  notes  models  knowledge  │  │  │
│  │  prompts  tools  skills  functions  files  folders  groups│  │  │
│  │  evaluations  analytics  memories  terminals  retrieval   │  │  │
│  │  configs  tasks  images  audio  utils  pipelines  scim    │  │  │
│  └───────────────────────────────────────────────────────────┘  │  │
│                                                                  │  │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────────────────┐│  │
│  │  /ollama   │  │   /openai    │  │  Socket.IO (/ws)  ────────┼┘  │
│  │  (proxy +  │  │   (proxy +   │  │  (socket/main.py)         │   │
│  │  internal) │  │   internal)  │  └──────────────────────────┘│   │
│  └─────┬──────┘  └──────┬───────┘                              │   │
│        │                 │                                       │   │
│  ┌─────▼─────────────────▼─────────────────────────────────┐   │   │
│  │             SQLAlchemy Models + Alembic                  │   │   │
│  │  (users, chats, messages, channels, notes, files, …)    │   │   │
│  └─────────────────────────────────────────────────────────┘   │   │
│                                                                  │   │
│  ┌─────────────────────────────────────────────────────────┐   │   │
│  │              Retrieval Pipeline                          │   │   │
│  │  loaders → chunking → embedding → vector DB → search    │   │   │
│  └─────────────────────────────────────────────────────────┘   │   │
└──────────────────────────────────────────────────────────────────┘
```

---

## 4. Repository Layout

```
ArkiveV2IA/
├── src/                              # SvelteKit frontend
│   ├── app.html                      # HTML shell
│   ├── app.css                       # Global styles (Tailwind)
│   ├── app.d.ts                      # SvelteKit ambient types
│   ├── routes/
│   │   ├── +layout.svelte            # Root layout (i18n init, theme)
│   │   ├── (app)/                    # Authenticated shell
│   │   │   ├── +layout.svelte        # Auth gate, config/store hydration
│   │   │   ├── +page.svelte          # Home → redirects to /c/new
│   │   │   ├── c/[id]/               # Chat thread pages
│   │   │   ├── admin/                # Admin panel routes
│   │   │   │   ├── functions/        # Function create/edit
│   │   │   │   └── ...
│   │   │   ├── workspace/            # Models, prompts, tools, skills, knowledge
│   │   │   ├── channel/              # Channel view pages
│   │   │   └── notes/                # Notes pages
│   │   ├── auth/                     # Login / signup page
│   │   ├── s/[id]/                   # Shared (public) chat viewer
│   │   └── watch/                    # Media watch page
│   └── lib/
│       ├── stores/index.ts           # ALL global Svelte stores + TypeScript types
│       ├── constants.ts              # API base URLs and compile-time constants
│       ├── i18n/                     # i18next setup, locale files
│       ├── utils/                    # Frontend utility functions (index.ts is large)
│       ├── workers/
│       │   └── pyodide.worker.ts     # Pyodide (browser Python) worker
│       ├── apis/                     # Typed fetch wrappers for every backend route
│       │   ├── index.ts              # Generic model/config fetchers
│       │   ├── auths/
│       │   ├── chats/
│       │   ├── ollama/
│       │   ├── openai/
│       │   ├── knowledge/
│       │   ├── audio/
│       │   ├── retrieval/
│       │   ├── streaming/            # SSE/streaming fetch utilities
│       │   └── ...
│       └── components/
│           ├── chat/                 # Core chat experience (see §6)
│           ├── workspace/            # Models, knowledge, prompts, tools, skills editors
│           ├── admin/                # Admin settings, analytics, evaluations, functions
│           ├── layout/               # Sidebar, Navbar, SearchModal, channel list
│           ├── notes/                # Note editor (Tiptap-based)
│           ├── playground/           # Standalone chat/completion playground
│           ├── common/               # Shared UI primitives (Button, Modal, Tooltip, …)
│           └── icons/                # SVG icon components
├── backend/
│   ├── arkive/
│   │   ├── main.py                   # FastAPI app, middleware stack, router mounting
│   │   ├── env.py                    # ALL environment variable declarations
│   │   ├── config.py                 # Runtime config model (DB-backed, Redis-synced)
│   │   ├── constants.py              # Shared constant strings and error messages
│   │   ├── functions.py              # Dynamic function loading and execution
│   │   ├── tasks.py                  # Background task definitions
│   │   ├── routers/                  # FastAPI routers (one file per domain)
│   │   ├── models/                   # SQLAlchemy ORM models + Pydantic schemas
│   │   ├── migrations/               # Alembic migration scripts
│   │   ├── retrieval/
│   │   │   ├── loaders/              # Document loaders: PDF, DOCX, YouTube, web, OCR
│   │   │   ├── vector/
│   │   │   │   ├── dbs/              # Connector for each vector DB
│   │   │   │   └── factory.py        # Vector DB factory (selects from env)
│   │   │   ├── web/                  # Web search providers (20+ integrations)
│   │   │   └── models/               # Embedding + reranker model wrappers
│   │   ├── socket/
│   │   │   └── main.py               # Socket.IO server, event routing, model tracking
│   │   ├── utils/
│   │   │   ├── auth.py               # JWT creation/validation, user extraction
│   │   │   ├── oauth.py              # OAuth provider helpers
│   │   │   ├── middleware.py         # Request middleware (auth, CORS, rate limit)
│   │   │   ├── audit.py              # Audit logging middleware
│   │   │   ├── embeddings.py         # Embedding model utilities
│   │   │   ├── tools.py              # Tool execution engine
│   │   │   ├── plugin.py             # Plugin/function loader
│   │   │   ├── mcp/                  # MCP (Model Context Protocol) support
│   │   │   └── ...
│   │   ├── internal/
│   │   │   └── db.py                 # SQLAlchemy engine, session factory, Base
│   │   ├── data/                     # Runtime data (gitignored)
│   │   │   ├── arkive.db             # Default SQLite database
│   │   │   ├── uploads/              # Uploaded files
│   │   │   ├── cache/                # Model/artifact cache
│   │   │   └── vector_db/            # Local Chroma vector store
│   │   └── static/                   # Brand assets (favicon, logos, manifests)
│   ├── requirements.txt
│   ├── start.sh                      # Uvicorn launcher (Linux/macOS/WSL)
│   └── start_windows.bat             # Uvicorn launcher (Windows native)
├── static/                           # Frontend public assets + Pyodide bundles
├── scripts/
│   └── prepare-pyodide.js            # Copies Pyodide assets into static/pyodide/
├── Dockerfile
├── docker-compose.yaml
├── docker-compose.gpu.yaml
├── package.json
└── pyproject.toml
```

---

## 5. Backend: API Surface

All routes are mounted in `backend/arkive/main.py`. The full prefix map:

| Mount prefix | Router file | Domain |
|---|---|---|
| `/ollama` | `routers/ollama.py` | Proxy + internal Ollama model management |
| `/openai` | `routers/openai.py` | OpenAI-compatible proxy + internal routing |
| `/api/v1/auths` | `routers/auths.py` | Sign in, sign up, OAuth, LDAP, token management |
| `/api/v1/users` | `routers/users.py` | User CRUD, roles, permissions, profile |
| `/api/v1/chats` | `routers/chats.py` | Chat CRUD, messages, sharing, archiving, tags |
| `/api/v1/channels` | `routers/channels.py` | Group channels, DMs, webhooks, messages |
| `/api/v1/models` | `routers/models.py` | Model definitions, visibility, ordering |
| `/api/v1/knowledge` | `routers/knowledge.py` | Knowledge bases, ingestion, search |
| `/api/v1/prompts` | `routers/prompts.py` | Saved prompts |
| `/api/v1/tools` | `routers/tools.py` | Tool definitions, execution |
| `/api/v1/skills` | `routers/skills.py` | Skill definitions |
| `/api/v1/functions` | `routers/functions.py` | Admin-authored server-side functions |
| `/api/v1/memories` | `routers/memories.py` | User memory entries |
| `/api/v1/files` | `routers/files.py` | File upload, retrieval, deletion |
| `/api/v1/folders` | `routers/folders.py` | Chat folder management |
| `/api/v1/groups` | `routers/groups.py` | User groups and RBAC |
| `/api/v1/evaluations` | `routers/evaluations.py` | Feedback, ratings, leaderboard data |
| `/api/v1/analytics` | `routers/analytics.py` | Usage dashboards, token stats |
| `/api/v1/retrieval` | `routers/retrieval.py` | RAG config, file ingestion, search |
| `/api/v1/configs` | `routers/configs.py` | Runtime app configuration |
| `/api/v1/tasks` | `routers/tasks.py` | Title gen, autocomplete, tag generation |
| `/api/v1/images` | `routers/images.py` | Image generation, editing (DALL-E, ComfyUI, A1111) |
| `/api/v1/audio` | `routers/audio.py` | STT (Whisper) |
| `/api/v1/pipelines` | `routers/pipelines.py` | Pipeline execution |
| `/api/v1/terminals` | `routers/terminals.py` | Terminal server connections |
| `/api/v1/utils` | `routers/utils.py` | PDF export, gravatar, code formatting |
| `/api/v1/scim/v2` | `routers/scim.py` | SCIM 2.0 provisioning (admin-only) |
| `/ws` | `socket/main.py` | Socket.IO realtime endpoint |
| `/static` | Static files | Brand assets |
| `/*` (fallback) | SPA fallback | Serves `build/index.html` |

---

## 6. Frontend: Component Architecture

### Route → Component Map

```
src/routes/(app)/
  +layout.svelte              ← Auth check, config fetch, store hydration, Socket.IO connect
  c/[id]/+page.svelte         ← Chat thread (wraps <Chat />)
  admin/+page.svelte          ← Admin panel shell (tabs into Settings/Users/etc.)
  workspace/models/           ← Model authoring (ModelEditor.svelte)
  workspace/knowledge/        ← Knowledge base management
  workspace/prompts/          ← Prompt authoring
  workspace/tools/            ← Toolkit editor
  workspace/skills/           ← Skill editor
  channel/[id]/+page.svelte   ← Channel view
  s/[id]/+page.svelte         ← Public shared chat (read-only)
```

### Core Chat Component Tree

```
src/lib/components/chat/
  Chat.svelte                 ← Top-level chat orchestrator
    Navbar.svelte             ← Chat header: model selector, actions
    MessageInput.svelte       ← Prompt input, file attachment, voice, tools
    Messages.svelte           ← Message list renderer
      ContentRenderer/        ← Markdown, code, citations, tool outputs
      Artifacts.svelte        ← Side-panel for rendered HTML/code artifacts
    ChatControls.svelte       ← Context-sensitive controls panel
    ModelSelector.svelte      ← Multi-model selection UI
    Settings/                 ← Per-chat and global chat settings
      Connections/            ← Connection management per-chat
      Integrations/           ← Tool server connections
    FileNav.svelte            ← File attachment navigator
    XTerminal.svelte          ← In-chat terminal (xterm.js)
```

### Key Stores (`src/lib/stores/index.ts`)

All global state lives in Svelte stores in this single file. Critical ones:

| Store | Type | Purpose |
|-------|------|---------|
| `user` | `Writable<SessionUser>` | Authenticated user profile |
| `config` | `Writable<Config>` | Backend runtime config (features, auth options) |
| `settings` | `Writable<Settings>` | User preferences (theme, language, model params) |
| `models` | `Writable<Model[]>` | Available models (Ollama + OpenAI + Arena) |
| `chatId` | `Writable<string>` | Active chat ID |
| `showSidebar` | `Writable<boolean>` | Sidebar visibility |
| `ARKIVE_NAME` | `Writable<string>` | Branding name (never "Open WebUI") |
| `_tools`, `_functions`, `_skills` | `Writable<...[]>` | Workspace assets |
| `socket` | `Writable<Socket>` | Socket.IO instance |

### `Model` Type Union

Models in the store are typed as:
```typescript
type Model = OpenAIModel | OllamaModel | ArenaModel;
```
- `OpenAIModel`: external OpenAI-compatible endpoint
- `OllamaModel`: locally-run Ollama model
- `ArenaModel`: `owned_by: 'arena'` — used for model comparison/evaluation arena

---

## 7. Retrieval Pipeline (RAG)

```
File upload / URL / web content
         │
         ▼
   backend/arkive/retrieval/loaders/
     ├── main.py          — dispatcher: detects file type, picks loader
     ├── external_web.py  — generic URL/web scraping
     ├── youtube.py       — YouTube transcript extraction
     ├── datalab_marker.py — Marker-based document parsing
     ├── mistral.py       — Mistral OCR
     └── mineru.py        — MinerU document parser
         │
         ▼
   Chunking (configurable chunk size + overlap)
         │
         ▼
   Embedding model (sentence-transformers / OpenAI / Ollama)
     backend/arkive/retrieval/models/
     backend/arkive/utils/embeddings.py
         │
         ▼
   Vector DB (selected via VECTOR_DB env var)
     backend/arkive/retrieval/vector/factory.py
     → Chroma | pgvector | Qdrant | Weaviate | Milvus | OpenSearch | Pinecone | ...
         │
         ▼
   Search (similarity + optional reranking)
     backend/arkive/retrieval/vector/main.py
         │
         ▼
   Context injection into chat message
```

### Web Search Providers (20+)

`backend/arkive/retrieval/web/` supports: Tavily, Brave, Bing, Azure, Google PSE, SearXNG, DuckDuckGo, Exa, Jina, Kagi, Perplexity, Serper, SerpAPI, SerpStack, Serply, Mojeek, YDC, Yandex, SearchAPI, Sougou, Bocha, Firecrawl, external (custom endpoint).

---

## 8. Model Routing

The backend does not call models directly from routers. The flow is:

```
Chat request (POST /api/v1/chats or streaming)
      │
      ▼
backend/arkive/utils/models.py    — resolves model ID → upstream config
      │
      ├── Ollama upstream   → /ollama proxy → Ollama instance(s)
      ├── OpenAI-compatible → /openai proxy → any OpenAI-format API
      ├── Anthropic         → utils/anthropic.py → Anthropic API directly
      └── Pipeline          → /api/v1/pipelines  → pipeline execution
```

The `MODELS` dict in `socket/main.py` tracks which models are currently active/in-use for display in the UI.

---

## 9. Realtime (Socket.IO)

`backend/arkive/socket/main.py` is the Socket.IO server mounted at `/ws`.

Key responsibilities:
- Tracks active user sessions and model usage (`MODELS`, session pools)
- Delivers streaming token events to the correct browser tab
- Broadcasts channel message events to connected clients
- Runs periodic cleanup: `periodic_usage_pool_cleanup`, `periodic_session_pool_cleanup`
- Redis pub/sub integration for multi-node deployments

---

## 10. Authentication & Authorization

### Auth Methods (all configured via env / admin UI)

| Method | Implementation |
|--------|---------------|
| Local (email + password) | bcrypt or argon2, JWT issued on sign-in |
| Trusted header | Proxied SSO via `X-Arkive-User-*` headers |
| OAuth 2.0 | Google, Microsoft (MSAL), GitHub, OIDC — via Authlib |
| LDAP | `python-ldap` integration |
| SCIM 2.0 | `/api/v1/scim/v2` — user provisioning from IdP |
| API keys | Long-lived tokens for programmatic access |

### Roles

- `admin` — full access, including all admin routes
- `user` — standard authenticated user
- `pending` — registered but not approved

### Groups & Permissions

Groups are DB-backed (`models/groups.py`). They gate access to models, knowledge bases, tools, and functions via `access_grants`. The `utils/access_control/` module handles policy evaluation.

---

## 11. Configuration System

Configuration is two-layered:

1. **Environment variables** (`backend/arkive/env.py`) — set at startup, controls infrastructure-level behavior (DB URL, Redis, feature flags, provider keys)
2. **Database-backed config** (`backend/arkive/config.py`) — stored in the `config` table, managed through the admin UI at `/admin/settings/*`

When Redis is available, config changes are pub/sub-synced across all nodes.

### Critical Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `ARKIVE_SECRET_KEY` | — | JWT signing key (required in production) |
| `DATABASE_URL` | `sqlite:///backend/data/arkive.db` | Primary database |
| `REDIS_URL` | — | Redis (optional, enables multi-node) |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server |
| `OPENAI_API_BASE_URL` | `https://api.openai.com/v1` | OpenAI-compatible upstream |
| `OPENAI_API_KEY` | — | Key for OpenAI/compatible |
| `VECTOR_DB` | `chroma` | Vector database backend |
| `RAG_EMBEDDING_MODEL` | sentence-transformers default | Embedding model |
| `FRONTEND_BUILD_DIR` | `../build` | Path to compiled SvelteKit output |
| `DATA_DIR` | `backend/data` | Uploads, cache, vector DB root |
| `ENV` | `dev` | `dev` or `prod` (affects error verbosity) |

---

## 12. Admin Surfaces

### Admin Settings Tabs

The admin settings panel (`src/lib/components/admin/Settings/`) is organized into:

| Tab | File | Scope |
|-----|------|-------|
| General | `General.svelte` | Auth, trusted header, LDAP, signup, onboarding |
| Connections | `Connections.svelte` | Ollama/OpenAI endpoints, direct connections |
| Models | `Models.svelte` | Default model, system prompt, model ordering |
| Evaluations | `Evaluations.svelte` | Feedback/evaluation settings |
| Integrations | `Integrations.svelte` | Google Drive, OneDrive, MCP, terminal servers |
| Documents | `Documents.svelte` | RAG chunking, embedding model, vector DB |
| Web Search | `WebSearch.svelte` | Web search provider + API key config |
| Code Execution | `CodeExecution.svelte` | Jupyter/Pyodide settings |
| Interface | `Interface/` | Banners, UI defaults, autocomplete, suggestions |
| Audio | `Audio.svelte` | STT provider selection and config |
| Images | `Images.svelte` | Image generation config (DALL-E, ComfyUI, A1111) |
| Pipelines | `Pipelines.svelte` | Pipeline server connections |
| Database | `Database.svelte` | Import/export, backup/restore |

### Additional Admin Pages

- **Users**: `admin/Settings/Users.svelte` — list, create, edit, ban, delete users
- **Groups**: group creation and membership management
- **Analytics**: `admin/Analytics/` — per-model usage, per-user usage, dashboard charts
- **Evaluations**: `admin/Evaluations/` — feedback list, leaderboard, model activity chart
- **Functions**: `admin/Functions/` — create and manage server-side executable functions

---

## 13. Workspace (User-Facing Asset Authoring)

Each workspace area has a list view and a full editor:

| Area | List | Editor | Backend model |
|------|------|--------|---------------|
| Models | `workspace/Models.svelte` | `Models/ModelEditor.svelte` | `routers/models.py` |
| Knowledge | `workspace/Knowledge/` | `Knowledge/KnowledgeBase.svelte` | `routers/knowledge.py` |
| Prompts | `workspace/Prompts.svelte` | `Prompts/PromptEditor.svelte` | `routers/prompts.py` |
| Tools | `workspace/Tools.svelte` | `Tools/ToolkitEditor.svelte` | `routers/tools.py` |
| Skills | `workspace/Skills.svelte` | `Skills/SkillEditor.svelte` | `routers/skills.py` |
| Functions | `admin/Functions.svelte` | `Functions/FunctionEditor.svelte` | `routers/functions.py` |

---

## 14. Browser Python Execution (Pyodide)

```
src/lib/workers/pyodide.worker.ts   ← Web Worker running Pyodide
scripts/prepare-pyodide.js          ← Copies WASM + packages into static/pyodide/
static/pyodide/                     ← Pyodide WASM and stdlib (gitignored, generated)
```

- The chat UI can send Python code to the worker
- Results stream back through `postMessage`
- Package loading is handled inside the worker at runtime
- Used for code interpreter features and in-browser data analysis

---

## 15. Dev Setup

### Prerequisites

- Node.js `>=18.13.0 <=22.x.x`
- npm `>=6`
- Python `>=3.11, <3.13`

### Steps

```bash
# 1. Copy env file and configure
cp .env.example .env
# Edit .env: set ARKIVE_SECRET_KEY, database URL, model URLs

# 2. Frontend dependencies
npm install

# 3. Backend virtual environment
python -m venv .venv
source .venv/bin/activate          # macOS/Linux/WSL
# OR: .\.venv\Scripts\Activate.ps1  # PowerShell
pip install -r backend/requirements.txt

# 4. Start backend (port 8080)
cd backend && bash start.sh
# Windows: .\start_windows.bat

# 5. Start frontend dev server (port 5173)
npm run dev
```

`npm run dev` and `npm run build` both execute `scripts/prepare-pyodide.js` first, which populates `static/pyodide/`.

### Useful Scripts

| Command | Purpose |
|---------|---------|
| `npm run dev` | Vite dev server on :5173 |
| `npm run build` | Build SvelteKit SPA to `build/` |
| `npm run preview` | Preview built SPA |
| `npm run check` | `svelte-check` (TypeScript + Svelte errors) |
| `npm run lint` | ESLint + svelte-check + pylint |
| `npm run test:frontend` | Vitest unit tests |
| `npm run pyodide:fetch` | Refresh Pyodide WASM assets |

---

## 16. Production Deployment

### Docker (recommended)

```bash
docker compose up -d
```

- `Dockerfile` — builds the full app (frontend + backend)
- `docker-compose.yaml` — `arkive` + `ollama` services, persistent volumes
- `docker-compose.gpu.yaml` — same with GPU passthrough for Ollama

Ports: Arkive exposed on `${ARKIVE_PORT:-3000}`.

### Manual (no Docker)

```bash
# Build frontend
npm run build

# Start backend (serves SPA from build/)
cd backend && bash start.sh
```

FastAPI mounts `build/` as a StaticFiles SPA fallback for all non-API routes.

---

## 17. Data Layout at Runtime

```
backend/data/
├── arkive.db          ← SQLite (default; swap for Postgres via DATABASE_URL)
├── uploads/           ← User-uploaded files (knowledge, chat attachments)
├── cache/             ← Embedding cache, model artifacts
└── vector_db/         ← Chroma persistent storage (default vector DB)
```

Optional external infrastructure:
- **Redis** — session store, config pub/sub, Socket.IO adapter for multi-node
- **PostgreSQL + pgvector** — production-grade DB + vector search in one
- **Dedicated vector DB** — Qdrant, Weaviate, Milvus, Pinecone, OpenSearch, etc.

---

## 18. Branding Rules

- Product name: **Arkive**
- Variable name in code: `ARKIVE_NAME` (store), `ARKIVE_*` (env vars)
- Every UI title, `<title>` tag, toast, and label must use `$ARKIVE_NAME` from the store
- Zero references to "Open WebUI" anywhere in frontend or backend
- Favicons, logos, and manifests live in `backend/arkive/static/`

---

## 19. Key Engineering Patterns

### Frontend Conventions

- All Svelte components use `<script lang="ts">` — no `// @ts-nocheck`
- `export let` for bindable/external props; `export const` for non-mutated exports
- `onMount` must be synchronous and return a cleanup function directly — async logic goes inside `.then()`
- FileReader `.result` is typed `string | ArrayBuffer` — always cast with `as string` before `JSON.parse`
- `getElementsByClassName` returns `Element[]` — cast to `HTMLElement` before calling `.click()`
- The `Model` type is a union — check `model.owned_by === 'arena'` or `model.arena === true` to exclude arena models from real model lists

### Backend Conventions

- All config keys are environment variables declared in `env.py` with their defaults
- DB-backed settings in `config.py` override env defaults at runtime
- Routers depend-inject `user = Depends(get_current_user)` for authentication
- The Ollama and OpenAI routers both proxy AND expose internal endpoints — they are not pure proxies
- Background tasks for title generation, tagging, and autocomplete run via FastAPI `BackgroundTasks` + `tasks.py`

---

## 20. Where to Start (Reading Order for a New AI Agent)

To understand the full system in minimum reads:

1. `pyproject.toml` + `package.json` — versions and dependency map
2. `backend/arkive/env.py` — every configuration knob that exists
3. `backend/arkive/main.py` — middleware stack, router mounts, startup lifecycle
4. `src/lib/stores/index.ts` — all global state and TypeScript types
5. `src/routes/(app)/+layout.svelte` — auth gate, store hydration, socket setup
6. `src/lib/components/chat/Chat.svelte` — core product loop
7. `src/lib/components/layout/Sidebar.svelte` — full product information architecture
8. `backend/arkive/routers/chats.py` — primary data flow (create, stream, save)
9. `backend/arkive/retrieval/` — RAG pipeline
10. `backend/arkive/socket/main.py` — realtime event model
