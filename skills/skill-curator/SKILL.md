---
name: skill-curator
description: Curate and catalog agent skills from GitHub repositories or URLs. You MUST use this skill whenever the user asks you to add a skill, curate skills, catalog an agent tool, or update a central catalog/README with a list of skills.
metadata:
  author: eho
  version: '1.0.1'
---

# Skill Curator

## Overview

This skill automates the process of discovering, extracting, and cataloging agent skills into a central `README.md` file. It ensures consistency in descriptions, categories, and installation commands.

## Workflow

### 1. Research & Discovery
Use the most appropriate tool to explore the target repository. If you are equipped with the "Public Repo Explorer" skill, perform a local shallow clone. Otherwise, use tools like the GitHub MCP server to browse the remote files.
- You MUST explicitly locate the actual `SKILL.md` files to identify valid skills. Use comprehensive search tools (e.g., `find_by_name` or `grep_search` if local, or MCP search) across the entire codebase.
- **Why?** Do not guess the directory structure based on folder names, because skills can be deeply nested (e.g., `plugins/expo-app-design/skills/layout/SKILL.md`). A folder is only a valid skill if it contains a `SKILL.md` file directly inside it.

### 2. Metadata Extraction
For each identified `SKILL.md` file, extract:
- **Name**: The display name of the skill (from `SKILL.md` frontmatter).
- **Description**: A concise summary of what the skill does (from `SKILL.md` frontmatter).
- **Source Link**: The direct GitHub URL to the `SKILL.md` file itself (must end in `/SKILL.md`).

### 3. Categorization
Group skills into logical categories. If a clear category isn't obvious, use these defaults or suggest new ones:
- **React Native**: Mobile development, optimization, and upgrades.
- **Web & React**: Frontend best practices, design guidelines, and composition patterns.
- **Workflows & Tools**: CI/CD, GitHub automation, deployment, and general utility skills.

### 4. Catalog Update
Update the workspace `README.md` using the established table format. The Source Link MUST point directly to the `SKILL.md` file (e.g., end in `/SKILL.md`). Do not include an "Install Command" column; instead, ensure the `README.md` has a general Installation section at the bottom.

| Skill Name | Source | Description |
| :--- | :--- | :--- |
| [**Skill Name**](Source Link to SKILL.md) | [Source Name](Source Repo URL) | Description |

## Examples

**Example 1:**
*Input:* "Add the skills from https://github.com/example/agent-skills to my catalog."
*Action:*
1. Discover `SKILL.md` files recursively in the repository.
2. Find skills like `image-optimizer` at `packages/ui/skills/image-optimizer/SKILL.md`.
3. Extract name and description from the frontmatter.
4. Update `README.md` with the new entries, ensuring the Source Link points directly to `packages/ui/skills/image-optimizer/SKILL.md`.
