#!/bin/bash
set -euo pipefail

SKILLS_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
export PYTHONDONTWRITEBYTECODE=1

bash -n \
  "$SKILLS_ROOT"/design-to-issues/scripts/*.sh \
  "$SKILLS_ROOT"/design-to-issues/tests/*.sh \
  "$SKILLS_ROOT"/user-story-implementer/scripts/*.sh \
  "$SKILLS_ROOT"/user-story-implementer/tests/*.sh \
  "$SKILLS_ROOT"/user-story-reviewer/scripts/*.sh \
  "$SKILLS_ROOT"/user-story-reviewer/tests/*.sh

python3 -m json.tool "$SKILLS_ROOT/feature-delivery/evals/evals.json" > /dev/null
python3 "$SKILLS_ROOT/design-to-issues/tests/story_contract_test.py"
python3 "$SKILLS_ROOT/design-to-issues/tests/render_issue_body_test.py"
python3 "$SKILLS_ROOT/user-story-implementer/tests/next_delivery_id_test.py"
python3 "$SKILLS_ROOT/feature-delivery/tests/audit_gap_contract_test.py"
python3 "$SKILLS_ROOT/feature-delivery/tests/fingerprint_findings_test.py"
python3 "$SKILLS_ROOT/feature-delivery/tests/handoff_contracts_test.py"
bash "$SKILLS_ROOT/design-to-issues/tests/create_milestone_test.sh"
bash "$SKILLS_ROOT/user-story-implementer/tests/create_pr_test.sh"
bash "$SKILLS_ROOT/user-story-implementer/tests/prepare_story_branch_test.sh"
bash "$SKILLS_ROOT/user-story-reviewer/tests/approve_or_merge_pr_test.sh"

echo "feature-delivery chain tests passed"
