---
name: blog-writer
description: "Transform technical documents, outlines, or raw notes into engaging, human-sounding blog posts. Use when asked to write a blog post, draft a post, turn this into a blog, or write up some content."
triggers:
  - write a blog post
  - draft a blog post
  - turn this into a blog post
  - blog this
  - write a post about
metadata:
  author: eho
  version: '1.0.0'
---

# Blog Writer

Turn technical content, outlines, or raw notes into polished, conversational blog posts that sound human — not AI-generated.

---

## The Job

1. Receive raw content or a topic from the user
2. Ask 2–3 quick clarifying questions if the input doesn't already answer them
3. Write the blog post following the style guide below
4. Save as `docs/blogs/[slug].md`

---

## Step 1: Clarify Before Writing

If the input doesn't already specify these, ask before writing. Users can respond quickly with lettered answers (e.g., "1A, 2B, 3C").

```
1. Who's the target reader?
   A. Technical practitioners (developers, engineers)
   B. Technical leaders / managers
   C. General business audience
   D. General public / beginners

2. Desired length?
   A. Short-form (~500 words) — quick take or opinion piece
   B. Standard (~900 words) — typical blog post
   C. Long-form (~1500 words) — deep dive or tutorial

3. What's the main angle?
   A. Derive from the content
   B. How-to / tutorial
   C. Opinion / take
   D. News / announcement
   E. Story / case study
```

**Skip any question you can already answer from the input.** If the input is a full document with a clear angle, proceed directly to writing.

---

## Step 2: Write the Post

### Tone and Voice

- Be conversational, empathetic, and slightly opinionated.
- Use contractions naturally (I'm, you're, don't, won't, it's).
- Write like you're talking to a smart peer over coffee — not presenting at a conference.
- Inject mild humor, metaphors, or relatable anecdotes where they fit naturally.
- Zero corporate jargon, academic phrasing, or dry technical-manual speak.
- **Technical depth:** For technical practitioners, preserve accuracy and use correct terminology. For general audiences, simplify concepts with analogies but don't sacrifice accuracy.

### Pacing and Rhythm

Humans don't write in perfectly uniform sentences. Mix it up:

- Short, punchy sentences hit hard.
- Then follow with a longer sentence that unpacks the idea and gives it room to breathe.
- Keep paragraphs to 1–3 sentences max for mobile readability.

### The Anti-AI Rulebook

Never use these phrases or patterns:

**Banned phrases:** "In the ever-evolving landscape of," "delve into," "a tapestry of," "a testament to," "unlocking," "crucial," "paramount," "fosters," "Furthermore," "Moreover," "In conclusion," "it's worth noting," "at the end of the day," "game-changer," "leveraging," "seamlessly," "robust," "cutting-edge," "innovative solution," "comprehensive," "streamline," "dive deep," "holistic"

**Banned patterns:**
- Throat-clearing intros: "In this article, we will explore..." or "Today, we're going to discuss..."
- End-of-post summaries: "In summary, we've covered..." or "To recap..."
- Passive voice overuse
- Symmetrical three-part lists that sound like a press release
- Starting consecutive paragraphs with the same word

### Structure

**The Hook** — Start with one of:
- A relatable frustration ("You've probably spent an afternoon debugging X only to realize...")
- A surprising or counterintuitive fact
- A short scene or story (2–4 sentences max)
- A blunt opinion ("Hot take: most teams are solving this problem backwards.")

**Headings** — Use H2s and H3s that sound like things a person would actually say:
- Good: "Why This Keeps Biting Teams"
- Good: "The Part Nobody Talks About"
- Bad: "Common Challenges and Considerations"
- Bad: "Key Benefits and Features"

**Body** — Follow the structure implied by the content. For how-tos, numbered steps work. For opinion pieces, use narrative flow with H2 breaks where the topic genuinely shifts.

**Ending** — End with a final thought, a question for the reader, or a subtle call to action. Do NOT summarize the whole post. Just land the plane.

---

## Step 3: Self-Check Before Outputting

- [ ] Hook grabs attention in the first sentence — no throat-clearing
- [ ] No banned phrases or AI-sounding patterns appear anywhere
- [ ] Paragraphs are 1–3 sentences throughout
- [ ] Sentence length varies — not all short, not all long
- [ ] Headings sound conversational, not like textbook chapters
- [ ] Post ends naturally — no summary paragraph
- [ ] Length matches the requested target (within ~10%)

---

## Output

Output ONLY the finalized Markdown blog post. No preamble, no "Here's your post!", no trailing notes or meta-commentary.

Save as `docs/blogs/[slug].md` (kebab-case title derived from the post title).
