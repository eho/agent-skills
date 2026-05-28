---
name: create-design-md
description: Create or update a DESIGN.md design system specification for websites, apps, prototypes, or product designs. Use when the user asks to generate a DESIGN.md, design system spec, UI specification, frontend design source of truth, Stitch/Google Design.md-style document, or agent-ready design tokens and component guidelines from images, descriptions, screenshots, mockups, brand notes, or raw product requirements.
---

# Create DESIGN.md

Use this skill to produce a `DESIGN.md` file that can guide future implementation agents without visual drift.

## Workflow

1. Gather design inputs from the current conversation, attached images, existing code, screenshots, mockups, brand notes, product requirements, and any existing `DESIGN.md`.
2. If official or user-provided Design.md requirements are referenced but not included, browse or read them when available. User-provided schema always takes precedence. For Google Stitch Design.md guidance, use the official docs:
   - `https://stitch.withgoogle.com/docs/design-md/overview/`
   - `https://stitch.withgoogle.com/docs/design-md/specification/`
3. Inspect the project before writing so the output matches the intended framework and file conventions.
4. Write or update `DESIGN.md` at the location requested by the user. If no location is specified, use the project root.
5. Use exact values for every token: hex colors, font families, font weights, `px` or `rem` sizing, spacing, radii, shadows, breakpoints, and motion timings.
6. Include CSS variable names or utility class names for every token.
7. Include an implementation token contract that maps design tokens to expected code artifacts such as global CSS variables, Tailwind theme entries, font loading, component folders, chart primitives, and content schemas when relevant.
8. Add implementation rules that prevent drift: layout rules, component states, accessibility rules, content tone, data/privacy rules when relevant, and quality checks.
9. Validate the Markdown structure and required headings after writing.

## Required Document Shape

If the user gives a schema, follow it exactly. Otherwise, use the schema in `references/design-md-schema.md`. That reference includes the original meta-spec this skill was created from.

For Google Stitch-style or agent-ready `DESIGN.md` files:

- Use standard Markdown.
- Prefer Markdown tables for token groups.
- Include optional YAML front matter only when it helps tools parse tokens.
- Keep the file human-readable and implementation-specific.
- Avoid vague design adjectives without concrete rules.
- Include examples of CSS variables and Tailwind utilities when the project is likely to use Tailwind.
- Include breakpoint, motion, z-index, and implementation mapping guidance unless the user explicitly wants a lighter brand-only spec.
- Include chart/data visualization tokens when the design contains dashboards, metrics, analytics, maps, activity feeds, or progress tracking.

## Design Extraction Rules

When source material is visual:

- Identify the design language: layout, density, typography, color behavior, component shape, elevation, motion, imagery, and content tone.
- Convert visible choices into tokens and rules rather than describing the screenshot.
- If text in a mockup is approximate, preserve intent rather than pretending exact copy is known.
- Define what to avoid, especially patterns that would cause drift from the intended direction.

When source material is only descriptive:

- Make conservative, coherent token choices that fit the product domain.
- State assumptions directly inside the design system where future agents need them.
- Do not invent excessive components. Cover the core primitives plus domain-specific modules implied by the product.

## Output Quality Bar

A good `DESIGN.md` must let another agent implement the first screen without asking what colors, fonts, spacing, card radii, component variants, or accessibility rules to use.

Before finishing, check:

- Required section headings are present.
- Color, typography, spacing, shadows, and radii are specified with exact values.
- Breakpoints, motion, z-index, and implementation mapping are covered.
- Buttons, inputs, cards, badges, and modals have structure, variants, states, and interaction rules.
- Framework and accessibility expectations are explicit.
- Domain-specific modules are included when needed.
- The document avoids generic SaaS, marketing, or decorative defaults unless those are actually part of the design.
