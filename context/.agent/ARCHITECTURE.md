# Architecture

_This document acts as the definitive anchor for understanding system design, data models, API contracts, and technology boundaries. Update this document during the Design and Review phases._

## 0. Project Topology

**Topology:** [e.g., `backend`, `frontend`, `ml-ai`, `infrastructure`, `library-sdk`]

_Declare one or more topology attributes that describe this project. Agents MUST read the corresponding topology profile(s) from the Gemstack `topologies/` directory (available at `~/.gemini/antigravity/global_workflows/`) before proceeding with any workflow step. Multiple topologies can be combined (e.g., a full-stack app with AI features declares `[frontend, backend, ml-ai]`)._

_For projects that don't fit any topology (e.g., documentation repos), write `[none]` and rely on the standard role/phase guardrails._

## 1. Tech Stack & Infrastructure
_List the core technologies and briefly explain *why* they were chosen. Pin exact major versions._
- **Language / Runtime**: e.g., TypeScript 5 / Node.js 22 — or Python 3.11+ — or Go 1.25
- **Frontend**: e.g., React 19 via Vite 6 — or Next.js 16 (App Router) — or N/A (CLI tool, no frontend)
- **Backend / API**: e.g., Express.js with `tsx` — or FastAPI / Typer CLI — or go-chi HTTP router — or Bash script (single-file utility)
- **Database**: e.g., SQLite (WAL mode) via Drizzle ORM — or PostgreSQL + TimescaleDB via sqlc — or N/A
- **Deployment**: e.g., Self-hosted / Docker Compose — or Vercel — or single binary via `go build`
- **Package Management**: e.g., npm / pnpm — or Poetry / pip — or Go modules (`go.mod`) + Makefile
- **Build System**: e.g., Vite — or `go build -ldflags` via Makefile — or N/A (interpreted script)

_For infrastructure repos (Docker Compose stacks, Proxmox configs): list the services, images, and their versions instead of a traditional tech stack._

## 2. System Boundaries & Data Flow
_Explain how the pieces connect. How does a user action traverse the stack? Specify the execution model (request/response, event-driven, producer-consumer pipeline, etc.)._

### Request / Data Flow
- Example (Web): Client Components → React Query `useQuery`/`useMutation` → Express API routes → Drizzle ORM → SQLite. Never write raw `useEffect` fetch loops.
- Example (Pipeline): CLI entrypoint → `asyncio.TaskGroup` producer-consumer → bounded `asyncio.Queue(maxsize=3)` → GPU inference worker in `ThreadPoolExecutor(max_workers=1)` → atomic file writer.
- Example (Go API): HTTP request → go-chi middleware (auth, rate limit, request ID) → handler → service layer → sqlc DAL → PostgreSQL. Server Actions call Go API and `revalidatePath("/")`.
- Example (Bash): Argument parsing → engine auto-detection → self-piping Docker re-invocation (or native) → phased processing (SRT cleanup → junk removal → MKV stream scrubbing) → telemetry dashboard.
- Example (Docker Compose): External traffic → Nginx Proxy Manager (SSL termination) → individual service containers. Inter-service communication via Docker bridge networks.

### Concurrency / Threading Model
_How does the system handle parallelism? Document queue bounds, worker pools, and any GIL or event-loop constraints._
- Example (Web): Single Node.js process, async I/O. React Query deduplicates concurrent requests. Background AI calls run through a `ParallelQueue` (max 5 concurrent per model).
- Example (Pipeline): Strictly bounded asyncio queues (extraction=3, inference=2). GPU inference offloaded to `loop.run_in_executor()` to avoid event-loop starvation.
- Example (Go): Goroutines for concurrent polling/webhook workers. `sync.Mutex` for ad-hoc sync locking. `context.Context` for cancellation propagation. Advisory DB locks (`pg_advisory_xact_lock`) prevent concurrent syncs per user.
- Example (Bash): Sequential processing — one MKV at a time. `flock`/`mkdir` lockfile prevents concurrent runs on the same directory.

## 3. Data Models & Database Schema
_Document the core entities and their relationships. Highlight complex junction tables, cascading deletion rules, virtual tables, or search indexes._
- **`User`**: Primary entity.
- **`Post`**: Has a many-to-one relationship with `User`.
- _Critical Rules_: e.g., "Never hard-delete a user, always set `deletedAt`."
- _Virtual Tables_: e.g., "FTS5 for full-text search, vec0 for vector embeddings. These do NOT support FK cascading — manual cleanup required on delete."
- _Time-Series_: e.g., "TimescaleDB hypertables for `cycles`, `sleeps`, `workouts`. Continuous aggregates (`daily_strain`, `daily_recovery`) for pre-computed dashboards."

_For projects without databases, write "N/A — No database utilized" (or "SQLite state DB for tracking processed files" etc.)._

### Schema Change Process
_How are migrations managed?_
- Example (Drizzle): Run `npm run db:generate` after modifying `src/db/schema.ts`. Server applies pending migrations on startup.
- Example (Alembic): Run `alembic revision --autogenerate -m "description"`, then `alembic upgrade head`.
- Example (sqlc): Write raw SQL migrations in `migrations/`. Run `sqlc generate` to regenerate type-safe Go code from `queries/query.sql`.
- Example (No ORM): Hand-written `CREATE TABLE` in Go `db.Init()` with `IF NOT EXISTS` guards.

## 4. API Contracts
_The absolute source of truth for communication between frontend and backend. Both sides build against these contracts. Include endpoint paths, methods, request/response shapes, and error formats._

### Example Contract (HTTP API):
**POST `/api/v1/resource`**
- **Request**: `{ title: string, content?: string }`
- **Response**: `{ data: Resource }`
- **Errors**: `{ error: string, code: "VALIDATION_ERROR" }`
- **Validation**: e.g., title must be non-empty, content max 500 chars.

_For CLI tools: document the command-line interface (flags, args, env vars)._
_For SDK libraries: document the exported public types and functions as the API contract. Include versioning and backward compatibility guarantees._
_For Go APIs with Swagger: reference the auto-generated `docs/swagger.json` as the canonical spec, and list key endpoints here for agent context._

## 5. External Integrations / AI
_Detail any third-party services, LLMs, or complex libraries. Mention rate limits, caching strategies, or wrapper functions._
- Example (Web): All AI operations live under `server/ai/` using a provider-agnostic adapter pattern. Calls routed through a SmartRouter with per-model quota tracking (RPM/RPD).
- Example (Pipeline): `faster-whisper` (CTranslate2 backend) loaded via hardware-aware routing matrix. Model selection based on VRAM/RAM auto-detection.
- Example (Edge AI): All LLM calls happen in Edge API routes. Client uses native Web Streams (`fetch` + `TextDecoder`) — never unstable SDK hooks.
- Example (Go SDK): Wraps the official WHOOP/eero REST API with typed Go structs. OAuth2 token refresh handled internally. Rate limiting via `golang.org/x/time/rate`.
- Example (Bash): Shells out to `ffmpeg`/`ffprobe` for media analysis. Docker self-piping pattern for containerized execution.

### Caching Strategy
_How is data cached? At which layers?_
- Example: React Query with stale-while-revalidate. Server-side LRU cache for search results (60s TTL).
- Example: Upstash Redis at the edge for rate limiting and telemetry aggregation.
- Example: Go in-memory cache with TTL for API responses. TimescaleDB continuous aggregates for pre-computed analytics.

### 5.1 Model Ledger (ML/AI Topology Only)

_If this project uses LLM APIs or ML models, document every model in use. This ledger drives the Circuit Breaker cost calculations defined in the `ml-ai` topology profile._

| Model | Role | Cost (1M in / 1M out) | Context Window | Structured Output | Rate Limit | Circuit Breaker Cost Cap |
|-------|------|----------------------|----------------|-------------------|------------|--------------------------|
| _(e.g., gemini-2.5-pro)_ | _(e.g., primary reasoning)_ | _($1.25 / $10.00)_ | _(1M tokens)_ | _(Yes/No)_ | _(5 RPM)_ | _($5.00/session)_ |

_If not an ML/AI project, write "N/A — No ML models utilized."_

## 6. Invariants & Safety Rules
_Critical constraints that MUST NEVER be violated. These are the "load-bearing walls" of the architecture. Agents should treat violations as blocking issues._
- Example (Web): `vec0` virtual tables do NOT support FK cascading. When deleting contacts, you MUST manually `DELETE FROM search_embeddings WHERE contactId = ?`.
- Example (Pipeline): NEVER write `.wav` or `.mp4` temp files to disk (zero-disk extraction). NEVER uncap `asyncio.Queue` bounds.
- Example (Security): NEVER inject `process.env.API_KEY` into a Client Component. All LLM calls must reside in server-side routes.
- Example (Go): OAuth tokens MUST be AES-256-GCM encrypted at rest. NEVER store plaintext tokens in the database. Idempotent upserts via `INSERT ... ON CONFLICT` — never risk duplicate records.
- Example (Bash): NEVER process hardlinked files by default (preserve linked source files). ALWAYS verify FFmpeg output duration matches input (±5s threshold) before committing rewrites. ALWAYS use `flock`/lockfile to prevent concurrent runs.
- Example (Docker): NEVER expose database ports to the host network. All inter-service communication goes through Docker bridge networks.

## 7. Error Handling Patterns
_How does the system handle and report errors?_
- Example (Web): Centralized `AppError` class + `asyncHandler` HOF for all Express routes. Consistent `{ error: string, code: string }` response shape.
- Example (Pipeline): `asyncio.wait_for(timeout=1800)` on long ffmpeg processes. Graceful shutdown via `SIGINT`/`SIGTERM` signal handler.
- Example (Frontend): React error boundaries for component-level failures. Toast notifications for API errors.
- Example (Go): Explicit `if err != nil` error propagation. Custom error types with HTTP status codes. Middleware-level panic recovery with structured logging.
- Example (Bash): `set -uo pipefail` at script top. `trap` for cleanup on `INT`/`TERM`. Duration mismatch = abort and preserve original file.

## 8. Directory Structure
_Outline the purpose of key directories in the repository._
- `src/app/` — Routing and pages (Next.js/Vite)
- `src/components/` — Reusable UI components
- `server/` — Backend services, routes, and adapters (Node.js)
- `cmd/` — Go application entrypoints (one per binary)
- `internal/` — Go private packages (not importable externally)
- `tests/` — Test suites (unit, integration)
- `migrations/` — Database migration files (SQL, Drizzle, Alembic)
- `docs/` — Feature lifecycle documents (explorations, designs, plans, archive)

## 9. Local Development
_Exact commands to get a working development environment. Agents should be able to copy-paste these._
- **Install**: `npm install` / `pip install -e ".[dev]"` / `go mod download`
- **Build**: `npm run build` / `go build ./cmd/app` / `make build`
- **Start Dev Server**: `npm run dev` / `python -m src.app` / `go run ./cmd/server` / `make docker-up`
- **Seed Data**: `npm run seed` / `python scripts/seed.py` (if applicable)
- **Database Setup**: e.g., "SQLite file auto-created on first run" / "Run `docker compose up db` for PostgreSQL+TimescaleDB"
- **Code Generation**: `sqlc generate` / `go generate ./...` / `swag init` (if applicable)
- **Required Environment**: List critical env vars from `.env.example` (e.g., `GEMINI_API_KEY`, `DATABASE_URL`, `ENCRYPTION_KEY`)

## 10. Environment Variables
_Inventory of all environment variables. Keep in sync with `.env.example`._

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | Database connection string |
| `GEMINI_API_KEY` | Yes | Google Gemini API key for AI features |
| `AI_TIER` | No | Model tier override (free/paid). Default: free |
| _(add as features require them)_ | | |
