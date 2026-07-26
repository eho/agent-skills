#!/bin/bash

set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)

mock_gh() {
  case "${MOCK_GH_MODE:-}" in
    sync-unchanged)
      case "$*" in
        "issue view 7 --json title -q .title") echo "ST-001: Title" ;;
        "issue view 7 --json body -q .body") command cat "$MOCK_BODY" ;;
        "issue view 7 --json labels -q .labels[].name") printf '%s\n' user-story ST ;;
        "issue view 7 --json url -q .url") echo "https://github.test/issues/7" ;;
        "issue edit"*) return 91 ;;
        *) return 92 ;;
      esac
      ;;
    sync-update)
      case "$*" in
        "issue view 7 --json title -q .title"|"issue view 7 --json body -q .body") echo old ;;
        "issue view 7 --json labels -q .labels[].name") echo user-story ;;
        "issue view 7 --json url -q .url") echo "https://github.test/issues/7" ;;
        "issue edit"*) return 0 ;;
        *) return 92 ;;
      esac
      ;;
    sync-create)
      [[ "$1 $2" == "issue create" ]] || return 92
      echo "https://github.test/issues/8"
      ;;
    issue-create)
      [[ "$1 $2" == "issue create" ]] || return 92
      echo "https://github.test/issues/10"
      ;;
    pr-create)
      [[ "$1 $2" == "pr create" ]] || return 92
      echo "https://github.test/pull/11"
      ;;
    dependency-unchanged)
      case "$*" in
        "repo view --json nameWithOwner -q .nameWithOwner") echo owner/repo ;;
        "api user -q .login") echo bot ;;
        "api repos/owner/repo/issues/7/comments?per_page=100 --paginate --jq "*) echo 55 ;;
        "api repos/owner/repo/issues/comments/55 --jq .body") command cat "$MOCK_BODY" ;;
        *) return 92 ;;
      esac
      ;;
    dependency-create)
      case "$*" in
        "repo view --json nameWithOwner -q .nameWithOwner") echo owner/repo ;;
        "api user -q .login") echo bot ;;
        "api repos/owner/repo/issues/7/comments?per_page=100 --paginate --jq "*) return 0 ;;
        "issue comment 7 --body-file "*) return 0 ;;
        *) return 92 ;;
      esac
      ;;
    dependency-update)
      case "$*" in
        "repo view --json nameWithOwner -q .nameWithOwner") echo owner/repo ;;
        "api user -q .login") echo bot ;;
        "api repos/owner/repo/issues/7/comments?per_page=100 --paginate --jq "*) echo 55 ;;
        "api repos/owner/repo/issues/comments/55 --jq .body") echo old ;;
        "api --method PATCH repos/owner/repo/issues/comments/55 -F body=@"*) return 0 ;;
        *) return 92 ;;
      esac
      ;;
    dependency-duplicate)
      case "$*" in
        "repo view --json nameWithOwner -q .nameWithOwner") echo owner/repo ;;
        "api user -q .login") echo bot ;;
        "api repos/owner/repo/issues/7/comments?per_page=100 --paginate --jq "*) printf '%s\n' 55 56 ;;
        *) return 92 ;;
      esac
      ;;
    milestone-existing)
      case "$*" in
        "repo view --json nameWithOwner -q .nameWithOwner") echo owner/repo ;;
        "api repos/owner/repo/milestones?state=all&per_page=100 --paginate --jq .[].title") echo Feature ;;
        *) return 92 ;;
      esac
      ;;
    milestone-create)
      case "$*" in
        "repo view --json nameWithOwner -q .nameWithOwner") echo owner/repo ;;
        "api repos/owner/repo/milestones?state=all&per_page=100 --paginate --jq .[].title") return 0 ;;
        "api repos/owner/repo/milestones -f title=Feature") return 0 ;;
        *) return 92 ;;
      esac
      ;;
    review-merge)
      case "$*" in
        "pr view 9 --json state -q .state") echo OPEN ;;
        "pr view 9 --json isDraft -q .isDraft") echo false ;;
        "pr view 9 --json headRefOid -q .headRefOid") echo abc123 ;;
        "pr view 9 --json mergeable -q .mergeable") echo MERGEABLE ;;
        "pr view 9 --json statusCheckRollup --jq "*) return 0 ;;
        "pr view 9 --json author -q .author.login"|"api user -q .login") echo bot ;;
        "pr review 9 --comment --body-file "*|"pr merge 9 --squash --delete-branch") return 0 ;;
        "pr view 9 --json mergeStateStatus -q .mergeStateStatus") echo CLEAN ;;
        *) return 92 ;;
      esac
      ;;
    review-head-changed)
      case "$*" in
        "pr view 9 --json state -q .state") echo OPEN ;;
        "pr view 9 --json isDraft -q .isDraft") echo false ;;
        "pr view 9 --json headRefOid -q .headRefOid") echo newer456 ;;
        "pr view 9 --json mergeable -q .mergeable") echo MERGEABLE ;;
        *) return 92 ;;
      esac
      ;;
    prepare)
      [[ "$*" == "repo view --json defaultBranchRef -q .defaultBranchRef.name" ]] || return 92
      echo main
      ;;
    *)
      echo "Unknown MOCK_GH_MODE: ${MOCK_GH_MODE:-unset}" >&2
      return 93
      ;;
  esac
}

if [[ "$(basename "$0")" == gh ]]; then
  mock_gh "$@"
  exit
fi

TEST_TMP=$(mktemp -d)
cleanup() {
  rm -rf "$TEST_TMP"
}
trap cleanup EXIT
mkdir "$TEST_TMP/bin"
ln -s "$ROOT/tests/feature-delivery-scripts.sh" "$TEST_TMP/bin/gh"
export PATH="$TEST_TMP/bin:$PATH"

MOCK_BODY="$ROOT/README.md"
export MOCK_BODY

MOCK_GH_MODE=sync-unchanged
export MOCK_GH_MODE
OUTPUT=$("$ROOT/skills/design-to-issues/scripts/sync_issue.sh" \
  7 "ST-001: Title" "user-story,ST" "$MOCK_BODY")
grep -Fq "Sync Result: Unchanged" <<<"$OUTPUT"

MOCK_GH_MODE=sync-update
OUTPUT=$("$ROOT/skills/design-to-issues/scripts/sync_issue.sh" \
  7 "ST-001: Title" "user-story,ST" "$MOCK_BODY")
grep -Fq "Sync Result: Updated" <<<"$OUTPUT"

MOCK_GH_MODE=sync-create
OUTPUT=$("$ROOT/skills/design-to-issues/scripts/sync_issue.sh" \
  new "ST-002: New" "user-story,ST" "$MOCK_BODY")
grep -Fq "Issue Number: 8" <<<"$OUTPUT"

MOCK_GH_MODE=issue-create
OUTPUT=$("$ROOT/skills/design-to-issues/scripts/create_issue.sh" \
  "ST-003: Script" "user-story,ST" "$MOCK_BODY")
grep -Fq "Issue Number: 10" <<<"$OUTPUT"

MOCK_GH_MODE=pr-create
OUTPUT=$("$ROOT/skills/user-story-implementer/scripts/create_pr.sh" \
  10 "feat: story" "Implemented story")
grep -Fq "https://github.test/pull/11" <<<"$OUTPUT"

MOCK_BODY="$ROOT/skills/design-to-issues/SKILL.md"
export MOCK_BODY
MOCK_GH_MODE=dependency-unchanged
OUTPUT=$("$ROOT/skills/design-to-issues/scripts/upsert_dependency_comment.sh" 7 "$MOCK_BODY")
grep -Fq "Dependency Comment: Unchanged" <<<"$OUTPUT"

MOCK_GH_MODE=dependency-create
OUTPUT=$("$ROOT/skills/design-to-issues/scripts/upsert_dependency_comment.sh" 7 "$MOCK_BODY")
grep -Fq "Dependency Comment: Created" <<<"$OUTPUT"

MOCK_GH_MODE=dependency-update
OUTPUT=$("$ROOT/skills/design-to-issues/scripts/upsert_dependency_comment.sh" 7 "$MOCK_BODY")
grep -Fq "Dependency Comment: Updated" <<<"$OUTPUT"

MOCK_GH_MODE=dependency-duplicate
if "$ROOT/skills/design-to-issues/scripts/upsert_dependency_comment.sh" \
  7 "$MOCK_BODY" >/dev/null 2>&1; then
  echo "Dependency helper accepted duplicate marker comments." >&2
  exit 1
fi

MOCK_GH_MODE=milestone-existing
OUTPUT=$("$ROOT/skills/design-to-issues/scripts/create_milestone.sh" Feature)
grep -Fq "Milestone ready" <<<"$OUTPUT"

MOCK_GH_MODE=milestone-create
OUTPUT=$("$ROOT/skills/design-to-issues/scripts/create_milestone.sh" Feature)
grep -Fq "Milestone created" <<<"$OUTPUT"

MOCK_GH_MODE=review-merge
"$ROOT/skills/user-story-reviewer/scripts/approve_or_merge_pr.sh" \
  9 "$ROOT/README.md" abc123

MOCK_GH_MODE=review-head-changed
if "$ROOT/skills/user-story-reviewer/scripts/approve_or_merge_pr.sh" \
  9 "$ROOT/README.md" abc123 >/dev/null 2>&1; then
  echo "Reviewer helper accepted a changed PR head." >&2
  exit 1
fi

REMOTE="$TEST_TMP/remote.git"
SEED="$TEST_TMP/seed"
WORK="$TEST_TMP/work"
git init --bare --initial-branch=main "$REMOTE" >/dev/null
git clone "$REMOTE" "$SEED" >/dev/null 2>&1
git -C "$SEED" config user.email test@example.com
git -C "$SEED" config user.name Test
git -C "$SEED" commit --allow-empty -m initial >/dev/null
git -C "$SEED" push origin main >/dev/null 2>&1
DEPENDENCY_OID=$(git -C "$SEED" rev-parse HEAD)
git clone "$REMOTE" "$WORK" >/dev/null 2>&1
MOCK_GH_MODE=prepare
(
  cd "$WORK"
  "$ROOT/skills/user-story-implementer/scripts/prepare_story_branch.sh" \
    feature/story-1 "$DEPENDENCY_OID" >/dev/null
  [[ "$(git branch --show-current)" == "feature/story-1" ]]
)

touch "$WORK/untracked"
if (
  cd "$WORK"
  "$ROOT/skills/user-story-implementer/scripts/prepare_story_branch.sh" \
    feature/story-2 "$DEPENDENCY_OID" >/dev/null 2>&1
); then
  echo "Branch helper accepted a dirty worktree." >&2
  exit 1
fi

echo "feature-delivery script behavior tests passed"
