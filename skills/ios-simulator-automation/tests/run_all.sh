#!/usr/bin/env bash
set -euo pipefail

SKILL_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
export PYTHONDONTWRITEBYTECODE=1

bash -n "$SKILL_ROOT/scripts/check-simulator-environment.sh"
bash -n "$SKILL_ROOT/tests/check_simulator_environment_test.sh"
python3 -m json.tool "$SKILL_ROOT/evals/evals.json" > /dev/null
python3 "$SKILL_ROOT/tests/runtime_manifest_test.py"
python3 "$SKILL_ROOT/tests/skill_contract_test.py"
bash "$SKILL_ROOT/tests/check_simulator_environment_test.sh"

printf 'ios-simulator-automation tests passed\n'
