# Product Philosophy

_This is the soul of the product. It explains why the app exists and what its core beliefs are. Product Visionaries and UI/UX Designers use this to make feature and design decisions. Engineers use it to resolve ambiguity._

## 1. Why This Exists
_What is the core pain point this project solves? Provide a single clear narrative._
- Example: "I forget to keep in touch with people I care about. This tool makes maintaining relationships effortless, not another chore."
- Example: "I have a 10TB media library with no subtitles. Manually generating SRTs is tedious. This tool autonomously processes entire libraries with zero intervention."

## 2. Target User
_Who is this for? Define a single clear persona. Every feature decision should be evaluated against this persona._
- Example: "This is a personal tool, not a SaaS. Optimize for one user: me. I am a power user who values speed, keyboard shortcuts, and information density over onboarding or hand-holding."
- Example: "This is for NAS hoarders and sysadmins who manage petabyte-scale media libraries. They are comfortable with Docker, CLI tools, and cron jobs."
- Example: "This is a public-facing blog for a technical audience. Readers are engineers and product thinkers who value depth, editorial quality, and interactive demonstrations."

## 3. Core Beliefs
_List 3-5 principles that guide all product and design decisions. Treat these as tie-breakers when multiple options exist._
- **Speed over features**: Opening this app should be faster than opening a native alternative. Features that add friction should be rejected.
- **Privacy is non-negotiable**: Data never leaves the device unless explicitly shared.
- **Gentle, not nagging**: Reminders should feel like a helpful nudge, not a strict task manager.

## 4. Design & UX Principles
_High-level experiential principles. These apply whether the project has a visual UI, a CLI, or is headless._
- Example (Web): "Mobile-first design. Everything must work at 375px before expanding to desktop."
- Example (CLI): "Beautiful terminal output via Rich. Progress bars for long operations. Graceful degradation if stdout is piped."
- Example (Editorial): "Magazine-quality typography. Every heading uses `text-balance`, every paragraph uses `text-pretty`."
- Example (All): "Every user action needs acknowledgment. Buttons respond on press, forms confirm on submit, destructive actions require confirmation."

## 5. What This Is NOT
_Explicitly scope out what's out of bounds to prevent feature creep. State the anti-goals._
- Not a B2B SaaS tool. No "leads", "pipelines", or "conversion tracking".
- Not a social media aggregator.
- Not a generic task manager. (e.g., Apple Reminders already exists)
