# Style Guide & Code Conventions

_This document enforces the visual identity and coding patterns of the project. It prevents context drift as multiple agents work on the codebase. Agents MUST follow these rules strictly._

## 1. Visual Language & Tokens
_Define the core color palette, spacing, and typography rules._
- **Primary Color**: `#XXXXXX` (Used for main CTAs)
- **Backgrounds**: e.g., Use `bg-surface` for base layers, `bg-surface-container` for elevated cards.
- **Borders**: e.g., "Lines are a failure of hierarchy. In this system, 1px solid borders are strictly prohibited for sectioning. Boundaries must be defined solely through background color shifts."

## 2. Component Patterns
_Specify how common UI elements should be built._
- **Buttons**: e.g., `bg-primary text-on-primary font-bold rounded-xl px-5 py-2.5`
- **Cards**: e.g., `bg-surface-container shadow-sm rounded-2xl p-6`
- **Inputs**: e.g., Focus states must use `focus:ring-2 focus:ring-primary/30`.

## 3. Code Conventions & State Management
_Define how logic should be structured._
- **Server-First Execution**: Maximize the use of React Server Components (RSC) to ship zero JavaScript for content delivery.
- **Quarantine Client State**: The `'use client'` directive should only be used in isolated interactive components (e.g., form inputs or interactive tables).
- **Data Fetching**: e.g., "Always use React Query for client-side fetching. Never write raw `useEffect` fetch loops."
- **Strict Typing**: The codebase maintains 0 TypeScript errors and 0 ESLint warnings. No `any` types. Use Zod for runtime validation.

## 4. Anti-Patterns (FORBIDDEN)
_Explicitly list approaches that agents should NEVER use._
- ❌ NEVER use `overflow-hidden` on flex containers that have children with focus rings. (Use `ring-inset` instead)
- ❌ NEVER inline SVG icons directly in components; use the designated Icon component.
- ❌ NEVER hallucinate styles or invent generic Tailwind utility classes unless permitted by the visual system.
- ❌ NEVER disable ESLint or TypeScript checks.
