#!/usr/bin/env bash
set -euo pipefail

SKILL_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
TEST_ROOT=$(mktemp -d)
trap 'rm -rf "$TEST_ROOT"' EXIT

MOCK_BIN="$TEST_ROOT/bin"
mkdir -p "$MOCK_BIN"

cat > "$MOCK_BIN/uname" <<'EOF'
#!/usr/bin/env bash
printf 'Darwin\n'
EOF

cat > "$MOCK_BIN/agent-device" <<'EOF'
#!/usr/bin/env bash
printf 'agent-device 1.2.3\n'
EOF

cat > "$MOCK_BIN/xcrun" <<'EOF'
#!/usr/bin/env bash
if [[ "$1" == "--version" ]]; then
  printf 'xcrun version 1\n'
elif [[ "$1 $2 $3 $4" == "simctl list devices --json" ]]; then
  printf '{"devices":{}}\n'
elif [[ "$1 $2 $3" == "simctl list devices" && "$4" == "booted" ]]; then
  printf '== Devices ==\n-- iOS 26.5 --\n    iPhone Test (SIM-UDID) (Booted)\n'
else
  printf 'unexpected xcrun arguments: %s\n' "$*" >&2
  exit 9
fi
EOF

cat > "$MOCK_BIN/df" <<'EOF'
#!/usr/bin/env bash
printf 'Filesystem 1024-blocks Used Available Capacity Mounted on\n'
printf '/dev/test 100000000 1000 52428800 1%% /tmp\n'
EOF

cat > "$MOCK_BIN/lsof" <<'EOF'
#!/usr/bin/env bash
if [[ "$*" == *":9090"* ]]; then
  printf 'COMMAND PID USER FD TYPE DEVICE SIZE/OFF NODE NAME\n'
  printf 'node 123 test 1u IPv4 0 0t0 TCP 127.0.0.1:9090 (LISTEN)\n'
fi
EOF

chmod +x "$MOCK_BIN"/*

OUTPUT=$(PATH="$MOCK_BIN:$PATH" \
  "$SKILL_ROOT/scripts/check-simulator-environment.sh" \
  --device SIM-UDID --min-free-gib 10 --port 9090)

grep -Fq 'CoreSimulator service: healthy' <<<"$OUTPUT"
grep -Fq 'free disk: 50 GiB' <<<"$OUTPUT"
grep -Fq 'listener on port 9090' <<<"$OUTPUT"

set +e
INVALID_OUTPUT=$(
  "$SKILL_ROOT/scripts/check-simulator-environment.sh" --port 70000 2>&1
)
INVALID_STATUS=$?
set -e

if [[ "$INVALID_STATUS" -ne 2 ]]; then
  printf 'expected invalid port status 2, got %s\n' "$INVALID_STATUS" >&2
  exit 1
fi
grep -Fq -- '--port must be an integer' <<<"$INVALID_OUTPUT"

printf 'check-simulator-environment tests passed\n'
