---
name: public-repo-explorer
description: Instructs the agent on how to efficiently browse public GitHub repositories using a local shallow clone. Use this skill when the user asks you to scan, examine, or extract information from a public Git repository.
license: MIT
metadata:
  author: eho
  version: '1.0.0'

---

# Public Repo Explorer

## Overview

Use this skill when the user asks you to scan, examine, or extract information from a public Git repository.

## Workflow

1. **Create a Temporary Workspace:**
   - Create a temporary directory on the user's machine to hold the repository safely without cluttering their main workspace. 
   - Command: `mkdir -p /tmp/agent-repo-scan && cd /tmp/agent-repo-scan`

2. **Perform a Shallow Clone:**
   - Do NOT use the GitHub API or `gh` CLI to avoid authentication blocks or rate limits.
   - Use standard git over HTTPS with the `--depth 1` flag to download only the latest commit. This saves massive amounts of time and bandwidth.
   - Command: `git clone --depth 1 <REPOSITORY_URL> temp_repo`

3. **Analyze the Architecture:**
   - Navigate into the cloned directory: `cd temp_repo`
   - List the root directory contents to understand the project structure using whatever tools you have available.
   - Look for standard entry points and configuration files: `README.md`, `package.json`, `requirements.txt`, `pyproject.toml`, `docker-compose.yml`, or `Makefile`.

4. **Examine Requested Content:**
   - If the user asked for a general summary, read the `README.md` and the main dependency file to determine the tech stack.
   - If the user asked for specific code (e.g., "Find how they handle database connections"), use your available search or find tools to locate relevant files, then read those specific files.

5. **Report and Clean Up:**
   - Present your findings to the user clearly and concisely based on their original request.
   - Once the user is satisfied, clean up the temporary directory to free up disk space.
   - Command: `rm -rf /tmp/agent-repo-scan/temp_repo`

## Constraints & Rules:
- **Never** attempt to push commits or open PRs using this skill. It is strictly for read-only browsing.
- **Never** download large binary files, datasets, or LFS assets unless explicitly instructed.
- Always prefer reading files using your internal file-reading tools over standard terminal commands like `cat`, `head`, or `tail` when possible.
