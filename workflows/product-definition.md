---
name: product-definition
description: Run the product definition workflow
---
# Workflow: Product Definition

**Goal:** Go from a raw idea to a concrete feature proposal and UX specification.

## Composition
This workflow composes:
- **Roles:** `Product Visionary`, `UI/UX Designer`
- **Phases:** `Ideate`, `Design (UX)`

## Process

1. **Step 1: Ideate (Product Visionary)**
   - Act as the **Product Visionary**. Survey the landscape, identify user pain points, and select a feature to build.
   - Write the exploration document to `docs/explorations/YYYY-MM-DD-product-visionary-{feature}.md`.
   - Update `.agent/STATUS.md` with your progress.

2. **Step 2: Design (UI/UX Designer)**
   - Act as the **UI/UX Designer**. Take the approved exploration and design the user journey, screen layouts, and interaction states.
   - Write the UX specification document to `docs/designs/YYYY-MM-DD-ui-ux-designer-{feature}.md`.
   - Update `.agent/STATUS.md` with your progress.

## Code Writing Policy
**STRICTLY PROHIBITED.** You are operating in a purely conceptual capacity. You only write Markdown (`.md`) files. You never write, modify, or suggest concrete implementation code.