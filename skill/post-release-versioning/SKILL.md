---
name: post-release-versioning
description: Perform post-release version metadata maintenance only on explicit invocation. Use only when the user invokes $post-release-versioning.
---

# Post Release Versioning

## Inspect the repository

Identify the released commit, its release version, all release-version sources, and the current branch's push remote before proposing changes. Inspect `git status --short`, the target commit, existing tags, version metadata, the current branch, and its upstream. Preserve unrelated working-tree changes. Stop and ask if the branch, remote, or upstream is ambiguous.

Discover package and Expo configuration with `rg --files -g 'package.json' -g 'app.json' -g 'app.config.*' -g 'eas.json'`.

- Update a release-bearing `package.json` `version` field. In a monorepo, inspect the root manifest and workspace manifests; update the root and application manifests that represent the same release. Do not blindly bump independent packages. If the appropriate manifests are ambiguous, list them and ask the user to choose.
- If an Expo `app.json` exists, update `expo.version`. If `app.config.*` is the active Expo configuration, locate the version source and edit it only when the change is unambiguous; otherwise ask the user.
- Inspect EAS configuration when present. Do not change platform build numbers if EAS manages them remotely with automatic incrementing.

## Confirm the proposed version

Determine the next version only from the user's instruction. If they have not specified it, ask what version to use; do not infer a major, minor, or patch bump.

Before creating a tag or editing files, present the released version, release commit, proposed next version, tag name, every manifest that will change, the planned version-bump commit message, and the remote/branch that will receive the commit and tag. Ask for explicit confirmation of the proposed version and changes. Do not proceed without an affirmative response.

If the proposed release tag already exists, report the commit it resolves to and do not move or replace it without explicit instruction.

## Tag the release, update versions, and commit

After confirmation, create an annotated local tag for the released commit before modifying version metadata:

```bash
git tag -a "v<released-version>" -m "Release v<released-version>" <release-commit>
```

Update only the confirmed version sources. Validate the changes before committing. Stage only those explicit paths, never use a blanket staging command such as `git add -A`, then create a version-bump commit such as `chore: prepare v<next-version>`.

Push the current branch and annotated tag to the confirmed remote after the commit succeeds:

```bash
git push <remote> <branch> "refs/tags/v<released-version>"
```

Never force-push. Stop and report any remote rejection rather than replacing remote history. Do not publish an app update or deploy unless the user explicitly asks.

## Validate and report

Verify that the tag dereferences to the intended commit with `git rev-parse --verify "v<released-version>^{}"`. Parse edited JSON files and assert that their version values equal the confirmed next version. For dynamic Expo configuration, use the repository's Expo config validation command when available. Run `git diff --check`.

Report the release tag and its target commit, the version-bump commit, updated files, validation outcome, and the remote branch and tag push results.
