# Architecture

_This document acts as the definitive anchor for understanding system design, data models, API contracts, and technology boundaries. Update this document during the Design and Review phases._

## 1. Tech Stack & Infrastructure
_List the core technologies and briefly explain *why* they were chosen._
- **Frontend**: e.g., Next.js 14 App Router (RSC-first approach)
- **Backend/API**: e.g., Node.js + Express / Next.js Server Actions
- **Database**: e.g., PostgreSQL via Prisma or SQLite via Drizzle
- **Deployment**: e.g., Vercel (Frontend) + Render (Backend)

## 2. System Boundaries & Data Flow
_Explain how the pieces connect. How does a user action traverse the stack? Do you use a strict Request/Response pattern, WebSockets, or Event Queues?_
- Example: All database mutations must happen via Server Actions. Client components should only manage local UI state.
- Example: The frontend utilizes explicit `fetch` calls wrapped via `useQuery` exclusively relying on React Query. Never write native `useEffect` fetch loops.

## 3. Data Models & Database Schema
_Document the core entities and their relationships. Highlight any complex junction tables, cascading deletion rules, or search indexes._
- **`User`**: Primary entity. 
- **`Post`**: Has a many-to-one relationship with `User`.
- _Critical Rules_: e.g., "Never hard-delete a user, always set `deletedAt`."

## 4. API Contracts
_The absolute source of truth for communication between frontend and backend. Both sides build against these contracts. Include endpoint paths, methods, request/response shapes, and error formats._

### Example Contract:
**POST `/api/v1/resource`**
- **Request**: `{ title: string, content?: string }`
- **Response**: `{ data: Resource }`
- **Errors**: `{ error: string, code: "VALIDATION_ERROR" }`
- **Validation**: e.g., title must be non-empty, content max 500 chars.

## 5. External Integrations / AI
_Detail any third-party services, LLMs, or complex libraries. Mention rate limits, caching strategies, or wrapper functions._
- Example: All AI operations live under `src/lib/ai/` using a provider-agnostic adapter pattern.
- Example: Calls to Gemini API happen in Edge Routes via Native Web Streams API.

## 6. Directory Structure
_Outline the purpose of key directories in the repository._
- `src/app/` - Routing and pages
- `src/components/` - Reusable UI components
- `src/server/` - Backend services and adapters
