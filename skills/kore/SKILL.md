---
name: kore
description: Use the Kore CLI to search, browse, save, and synthesize the user's personal memory bank
triggers:
  - kore
  - "check my memory"
  - "do i have anything"
  - "remember this"
  - "save this"
  - "what do i know about"
---

You have access to the user's personal knowledge base through Kore — saved bookmarks, notes,
recommendations, experiences, and synthesized insights accumulated over time, often months or years ago.

The user frequently forgets what they've saved. Your role is to bridge the gap between saved knowledge
and active recall. Use the `kore` CLI to interact with the knowledge base.

## Core Behaviors

**1. PROACTIVE RECALL** — Call `kore search` BEFORE composing responses when the topic could involve
personal context: restaurants, travel, recipes, books, movies, people, places, projects, technical
preferences, health, hobbies, learning resources. If the topic MIGHT have personal context, check.
Weave relevant memories into your answer naturally — don't list them mechanically.

**2. PREFER INSIGHTS** — When search returns many results on the same topic, run `kore insights` for
a synthesized view. Present the synthesis rather than listing individual memories unless the user
wants specifics.

**3. OFFER TO REMEMBER** — When the conversation produces valuable information the user might want
later, offer to save it. Never save silently — always confirm first.

**4. NEVER FABRICATE** — If search returns nothing relevant, say so. "I don't see anything in your
saved memories about that" is a perfectly good response. Don't guess what the user might have saved.

**5. RESPECT CONFIDENCE** — When a memory has low confidence (< 0.5), mention it: "I found a note
about this, though the details might not be fully accurate."

## Commands

### Search memories

```sh
kore search "query" [--type place|media|note|person] [--intent recommendation|reference|personal-experience|aspiration|how-to] [--tags tag1,tag2] [--limit 10] [--min-confidence 0.6] [--created-after 2025-01-01] [--created-before 2025-12-31] [--offset 0] [--json]
```

- Omit `--query` for metadata-only browsing (e.g., "show all my aspirations", "list recent places") —
  results sort by date saved descending. Only pass a query when content relevance matters.
- Use `--intent` to narrow: `recommendation` for suggestions others gave, `aspiration` for things the
  user wants to try, `how-to` for instructions.
- Use `--created-after`/`--created-before` for time-based queries: "restaurants saved last month".
- **If results are empty or sparse:** broaden before concluding nothing exists. A query for
  "tonkotsu ramen tokyo" that returns nothing might still return results for "ramen tokyo" or "ramen".
  Try removing `--intent`/`--tags` filters to widen the match set, then narrow manually.
- **Result fields:** `score` = search relevance; `confidence` = how reliably the memory was extracted
  from its source. Results of type `insight` are synthesized documents — prefer these when the user
  wants a summary.

### Browse without a query

```sh
kore list [--type place|media|note|person|insight] [--limit 20] [--json]
```

### Full memory detail

```sh
kore show <id> [--json]
```

Use after search when you need the full source text, all metadata, or to follow consolidation
references (`insight_refs`, `source_ids`). Content is truncated at 20k characters.

### Save new content

```sh
echo "content" | kore ingest [--source agent] [--url <url>] [--priority low|normal|high] [--suggested-tags tag1,tag2] [--suggested-category travel/food/ramen]
```

- Always confirm with the user before saving unless they've said to save freely.
- Include enough context for good extraction. Don't just save "Mutekiya" — save
  "Mutekiya Ramen in Ikebukuro, Tokyo — recommended by John for solo dining, known for rich
  48-hour pork bone broth." Raw or messy text is fine; the extraction pipeline handles it.
- `--suggested-tags` and `--suggested-category` are hints that improve extraction accuracy.
- Content is queued for LLM extraction — it won't appear in search immediately.

### Synthesized insights

```sh
kore insights ["query"] [--type cluster_summary|evolution|contradiction|connection] [--status active|evolving|degraded] [--limit 5] [--json]
```

Use when the user asks about their "current view", "overall understanding", or "what do I know about"
a topic. Also use when search returns 5+ fragmented results on the same topic — check for a
consolidated version first.

- `--type evolution`: how the user's thinking has changed over time
- `--type connection`: cross-domain connections across different areas of knowledge
- Result fields: `synthesis` = 3–5 sentence summary; `reinforcement_count` = how many times updated
  (higher = more actively confirmed knowledge); `status evolving` = insight is being updated with
  new evidence

### Synthesize related memories

```sh
kore consolidate --dry-run [--json]   # preview first
kore consolidate [--json]             # run on user confirmation
```

Offer consolidation when search returns many fragmented results and no insight exists yet:
"You have 8 separate notes about sourdough. Would you like me to synthesize them into a consolidated
reference?" Always run `--dry-run` first to show the preview.

Result status meanings:
- `consolidated`: synthesis succeeded — the new insight ID is returned
- `no_seed`: nothing ready yet; more memories needed
- `cluster_too_small`: a candidate seed exists but lacks enough related memories
- `retired_reeval` / `synthesis_failed`: transient failure; suggest trying again

Note: consolidation also runs automatically in the background every 30 minutes. This command is
for on-demand synthesis when the user wants it now.

### System health

```sh
kore health
```

Use when the user asks system status ("how many memories do I have?", "is Kore running?") or when
diagnosing unexpected search results — check whether the index is still embedding or the queue has
failed tasks.
