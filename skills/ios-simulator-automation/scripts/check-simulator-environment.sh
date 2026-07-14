#!/usr/bin/env bash
set -euo pipefail

min_free_gib=10
device=""

usage() {
  cat <<'EOF'
Usage: check-simulator-environment.sh [--min-free-gib N] [--device NAME_OR_UDID]

Read-only preflight for iOS Simulator automation. Reports tool versions, booted
Simulators, free disk, and common listener ownership. Exits non-zero when a hard
prerequisite is missing, free disk is below the threshold, or --device is not
present in the booted-device list.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --min-free-gib)
      min_free_gib="${2:?missing value for --min-free-gib}"
      shift 2
      ;;
    --device)
      device="${2:?missing value for --device}"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      printf 'ERROR: unknown argument: %s\n' "$1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ ! "$min_free_gib" =~ ^[0-9]+$ ]]; then
  printf 'ERROR: --min-free-gib must be a non-negative integer\n' >&2
  exit 2
fi

if [[ "$(uname -s)" != "Darwin" ]]; then
  printf 'ERROR: iOS Simulator automation requires macOS\n' >&2
  exit 1
fi

for command_name in xcrun agent-device; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    printf 'ERROR: required command not found: %s\n' "$command_name" >&2
    exit 1
  fi
done

printf 'agent-device: %s\n' "$(agent-device --version)"
printf 'xcrun: %s\n' "$(xcrun --version | head -n 1)"

booted_devices="$(xcrun simctl list devices booted)"
printf '%s\n' "$booted_devices"

booted_count="$(grep -c '(Booted)' <<<"$booted_devices" || true)"
if (( booted_count == 0 )); then
  printf 'ERROR: no booted iOS Simulator found\n' >&2
  exit 1
fi

if (( booted_count > 1 )) && [[ -z "$device" ]]; then
  printf 'ERROR: %s Simulators are booted; select one with --device\n' "$booted_count" >&2
  exit 1
fi

if [[ -n "$device" ]] && ! grep -Fq "$device" <<<"$booted_devices"; then
  printf 'ERROR: selected device is not booted: %s\n' "$device" >&2
  exit 1
fi

available_kib="$(df -Pk . | awk 'NR == 2 { print $4 }')"
available_gib="$((available_kib / 1024 / 1024))"
printf 'free disk: %s GiB (minimum %s GiB)\n' "$available_gib" "$min_free_gib"

if (( available_gib < min_free_gib )); then
  printf 'ERROR: insufficient free disk for requested threshold\n' >&2
  exit 1
fi

if command -v lsof >/dev/null 2>&1; then
  for port in 8081 3100 3200; do
    listener="$(lsof -nP -iTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)"
    if [[ -n "$listener" ]]; then
      printf 'listener on port %s:\n%s\n' "$port" "$listener"
    else
      printf 'listener on port %s: none\n' "$port"
    fi
  done
fi
