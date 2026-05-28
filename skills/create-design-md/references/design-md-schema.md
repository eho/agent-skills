# DESIGN.md Schema Reference

Use this reference when the user has not provided a stricter schema. If the user provides a schema, follow the user's schema exactly.

## Official References

Use these when the user asks for Google Stitch compatibility, the current Design.md specification, or official citations:

- Google Stitch Design.md overview: `https://stitch.withgoogle.com/docs/design-md/overview/`
- Google Stitch Design.md specification: `https://stitch.withgoogle.com/docs/design-md/specification/`

If the official docs are unavailable through non-browser fetch because the pages are JavaScript-rendered, state that limitation and follow the user-provided schema plus this reference.

## Original Meta-Spec

The following meta-spec is the baseline this skill was created from. Treat it as required unless the user gives a different schema.

### Mission

You are an expert Frontend Architect and UX/UI Engineer. Analyze the provided design inputs, including images, descriptions, screenshots, mockups, brand notes, raw data, or existing UI, and generate a comprehensive `DESIGN.md` file. This file serves as the single source of truth for the design system.

### Formatting Rules

- Use standard Markdown formatting.
- Use Markdown tables for design tokens such as colors, typography, and spacing.
- Specify exact values: hex codes for colors, `rem` or `px` for sizing, concrete radii, shadows, and timings.
- Provide the intended CSS variable name or utility class, such as Tailwind, for every token.

### Required Schema

The generated `DESIGN.md` must include these sections exactly:

- `[Section 1] System Overview`
- `[Section 2] Design Tokens`
- `[Section 3] Core Components`
- `[Section 4] Implementation Guidelines`

### Section Requirements

`[Section 1] System Overview` must briefly summarize the design system aesthetic.

`[Section 2] Design Tokens` must group foundational values into tables:

- Colors: include role, hex value, CSS variable or utility class, and states such as hover, active, disabled.
- Typography: include font family, weights, and a scale for H1-H6 and body text with size and line-height.
- Spacing & Layout: define grid system, standard gaps, padding, and margin scale.
- Shadows & Radii: define standard border radii and box shadows.
- Breakpoints: define responsive thresholds and layout behavior.
- Motion: define durations, easings, reduced-motion behavior, and what may animate.
- Z-index: define layering tokens for sticky elements, overlays, modals, and toasts.
- Data visualization: define chart, heatmap, map, and progress tokens when dashboards or metrics are part of the product.

`[Section 3] Core Components` must cover Buttons, Inputs, Cards, Badges, and Modals. For each component provide:

- Structure.
- Variants.
- States.
- Interaction rules.

`[Section 4] Implementation Guidelines` must specify:

- Primary styling framework.
- Strict accessibility rules, including WCAG AA contrast expectations.

## Required Structure

```markdown
---
design_system:
  name: "<Design system name>"
  version: "0.1.0"
  status: "draft"
  description: "<Short summary>"
  tokens:
    colors:
      <name>: "<hex>"
    typography:
      <role>: "<font family>"
    spacing_base_px: 4
---

# DESIGN.md

## [Section 1] System Overview

## [Section 2] Design Tokens

## [Section 3] Core Components

## [Section 4] Implementation Guidelines
```

## Section 1: System Overview

Include:

- One concise paragraph describing the aesthetic and product context.
- 4-8 principles that future implementation must preserve.
- Explicit anti-goals when drift risk is high.

## Section 2: Design Tokens

Use Markdown tables.

### Colors

Required columns:

| Role | Hex | CSS Variable | Utility Class | Usage |
|---|---:|---|---|---|
| Background | `#FFFFFF` | `--color-background` | `bg-background` | Main page background. |

Include:

- Backgrounds and surfaces.
- Primary text, secondary text, muted text.
- Borders/dividers.
- Primary, secondary, and accent colors.
- Hover, active, disabled, focus, success, warning, danger states.
- Chart/data colors when dashboards or metrics are part of the product.

### Typography

Required columns for font families:

| Role | Font Family | CSS Variable | Utility Class | Weights | Usage |
|---|---|---|---|---|---|

Required columns for scale:

| Text Style | Size | Line Height | Weight | CSS Variable | Utility Class | Usage |
|---|---:|---:|---:|---|---|---|

Include:

- Font family roles.
- H1-H6.
- Body large, body, body small, caption.
- Metric or mono styles when data is part of the UI.

### Spacing & Layout

Required columns:

| Token | Value | CSS Variable | Utility Class | Usage |
|---|---:|---|---|---|

Include:

- A spacing scale.
- Page max widths.
- Gutters.
- Grid columns.
- Section spacing.
- Responsive stacking rules.

### Shadows & Radii

Required columns:

| Token | Value | CSS Variable | Utility Class | Usage |
|---|---:|---|---|---|

Include:

- Border radii.
- Shadow/elevation levels.
- Rules for when to use shadows vs borders.

## Section 3: Core Components

For each required core component, include:

- Structure.
- Variants.
- States.
- Interaction rules.

Required components:

- Buttons.
- Inputs.
- Cards.
- Badges.
- Modals.

Add domain-specific components when the product needs them, such as:

- Navigation.
- Stat tiles.
- Charts.
- Activity feeds.
- Project cards.
- Media blocks.
- Empty states.
- Error states.

## Section 4: Implementation Guidelines

Include:

- Primary styling framework.
- Implementation token contract mapping tokens to code artifacts.
- Tailwind theme mapping or equivalent framework mapping when relevant.
- Font loading instructions.
- Component naming and folder conventions.
- Token implementation strategy.
- Accessibility rules.
- Responsive rules.
- Motion rules.
- Content/tone rules.
- Data/privacy rules when personal, health, financial, or user-sensitive data appears.
- Quality bar and validation expectations.

## Writing Rules

- Use exact values, not placeholders like `primary blue`.
- Use design tokens in component examples.
- Keep the design contract and code contract together in `DESIGN.md`; actual executable CSS, Tailwind config, React components, schemas, and tests belong in app files.
- Explain why a rule exists only when it prevents likely drift.
- Avoid long theoretical design-system education.
- Do not include a changelog, README, or install instructions inside the skill output unless the user asks.

## Implementation Contract Checklist

Add this level of implementation detail by default:

- CSS variable baseline for every token family.
- Framework mapping such as Tailwind `theme.extend` or Tailwind v4 theme CSS.
- Font loading guidance, including exact font families, weights, and CSS variable assignment.
- Breakpoint tokens and responsive stacking rules.
- Motion tokens and `prefers-reduced-motion` expectations.
- Z-index tokens and layering rules.
- Component naming conventions and folder placement.
- Domain-specific data visualization tokens when the product includes metrics, charts, maps, progress, or activity feeds.
