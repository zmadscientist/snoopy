#!/usr/bin/env bash
set -Eeuo pipefail

# Where the repo lives (has snoopy.py and pythonLicenses.csv)
SNOOPY_HOME="${SNOOPY_HOME:-$HOME/examples/snoopy}"

PY="$SNOOPY_HOME/snoopy.py"
if [[ ! -f "$PY" ]]; then
  printf 'snoopy: cannot find %s\n' "$PY" >&2
  printf 'Set SNOOPY_HOME or fix the path inside %s\n' "$0" >&2
  exit 127
fi

exec /usr/bin/env python3 "$PY" "$@"
