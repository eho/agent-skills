# Image-generation prompts

Use this reference only when generating or revising app-icon artwork with an image model.

## Build the prompt in layers

A reliable prompt separates five concerns:

1. **Context** — what the image is for and what it must not imitate.
2. **Concept** — the product promise, metaphor, and chosen archetype.
3. **Art direction** — palette, material, rendering, lighting, and mood.
4. **Composition and constraints** — square framing, silhouette, exclusions, and small-size behavior.
5. **Quality filters** — conditions that should cause the model to reject or revise its own result.

This is more reliable than a long comma-separated style description because it distinguishes the visual idea from rendering and technical constraints.

## Assign roles to references

When using multiple input images, state what each controls:

- **Concept/geometry reference** — the selected metaphor, silhouette, proportions, or arrangement.
- **Visual-language reference** — palette, material, rendering depth, lighting, or texture.
- **Product-context reference** — recurring brand motifs or UI character; do not reproduce the screen as an icon.

Tell the model which traits to preserve and which may change. Preserve the intended visual language without copying or blending the reference compositions.

## Choose one archetype

Choose internally; do not label it in the generated image:

- **Object** — one recognizable physical or symbolic object. Useful for utilities, productivity, finance, and dashboards.
- **Abstract form** — a distinctive geometric metaphor. Useful for creative, analytical, AI, or experimental products.
- **Hybrid** — a recognizable object with restrained personality but no face. Useful for friendly lifestyle, health, and household products.
- **Character** — an expressive figure with a face. Reserve for products where a mascot genuinely fits, such as games or children’s learning.

Do not default to a mascot merely to make the icon feel friendly.

## Base prompt

```text
Use case: logo-brand
Asset type: square symbol illustration for [product]

Product promise:
[One sentence describing what the product helps people accomplish or feel.]

Audience and tone:
[Audience]; [three or four tone words].

Primary concept:
[One clear metaphor, silhouette, and arrangement.]

Input references, if any:
- [Reference 1]: controls [concept/geometry traits]
- [Reference 2]: controls [palette/material/rendering traits]
- Preserve [specific traits]; do not duplicate either composition

Archetype:
[object / abstract form / hybrid / character]

Art direction:
- Palette: [named colors and hex values]
- Material/rendering: [flat vector, paper, ceramic, matte 2.5D, etc.]
- Lighting: [controlled direction and softness]
- Mood: [desired emotional effect]

Composition:
- 1024×1024, square 1:1 canvas
- one focal point and a strong centered or intentionally balanced silhouette
- readable at 48–64 px
- background reaches all four sharp canvas corners

Constraints:
- no text, letters, numbers, watermark, or recognizable brand marks
- no device or UI mockup
- no rounded-square tile, card, border, sticker, or baked launcher mask
- no outer drop shadow, long cast shadow, halo, or global glow
- no [product-specific misleading symbols or categories]

Quality check:
Reject and simplify if the result becomes a full scene, generic logo,
unrequested mascot, multi-object collage, or loses its subject at small size.
```

The base template targets a full-color master. To generate its transparent foreground companion, keep the concept, geometry, palette, material, and view fixed, then replace the background instruction with:

```text
Output only the foreground mark on a transparent 1024×1024 canvas.
Preserve the selected symbol exactly. No background, frame, mask, outer shadow,
glow, or new objects. Keep antialiased edges clean.
```

## Defaults that prevent common failures

- Describe the output as a **square symbol illustration**, not merely “an app icon.” Image models often respond to “app icon” by drawing a rounded-square tile inside the canvas.
- Ask for one intentional visual element rather than a collection of app features.
- Prefer a slightly unexpected but understandable metaphor over the most literal category symbol.
- Default to clean 2D or restrained matte 2.5D rendering with subtle internal shading. Avoid inflated glass, chrome, neon, bloom, sparkles, lens flare, and exaggerated shine unless the user requests them.
- Keep lighting soft and controlled so it defines form without becoming the concept.
- Avoid realistic portraits, full scenes, device chrome, and UI elements.
- Treat clean geometry, recognizable silhouette, and wallpaper contrast as higher priorities than surface detail.

A 92–98% subject-fill instruction can counter excessive image-model padding. Treat it as a corrective heuristic, not a platform requirement: use it when artwork arrives too small inside its canvas, but preserve intentional breathing room. Adaptive foreground sizing is handled later during packaging.

## Generate useful variants

For early concept exploration, vary the underlying metaphor or silhouette. Palette-only variants do not test the idea.

For iterations within one selected direction, keep the archetype, palette, and dominant material stable. Change one structural variable at a time—for example:

- compact versus open geometry;
- centered versus intentionally offset balance;
- one-piece versus cutout silhouette;
- flat versus shallow dimensional treatment.

State what remains fixed and what changes in each prompt so the model produces a coherent family instead of unrelated icons.

## Review loop

Before accepting a candidate:

- View it at full size, 64 px, and 48 px.
- Apply a slight blur or squint test; the focal shape should remain obvious.
- Check that it reads on both light and dark surroundings.
- Check for unintended text, faces, extra objects, padding, masks, shadows, or category confusion.
- Confirm that the central metaphor can become a clean single-color Android themed mark.

When a candidate fails, revise the concept or silhouette first. More texture and lighting rarely repair a weak icon idea.
