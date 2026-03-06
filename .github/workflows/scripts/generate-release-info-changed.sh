#!/usr/bin/env bash
set -euo pipefail

# generate-release-info-changed.sh
# Parse conventional commits since the last tag and produce two outputs:
#   1. release_notes.md  — GitHub Release body (flat commit list, unchanged behaviour)
#   2. CHANGELOG.md      — prepend a new categorised section for the release
#
# Usage: generate-release-info-changed.sh <new_version> <last_tag>

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <new_version> <last_tag>" >&2
  exit 1
fi

NEW_VERSION="$1"
LAST_TAG="$2"

# ── Collect raw commits ────────────────────────────────────────────────────
if [ "$LAST_TAG" = "v0.0.0" ]; then
  COMMIT_COUNT=$(git rev-list --count HEAD)
  if [ "$COMMIT_COUNT" -gt 10 ]; then
    RAW_COMMITS=$(git log --pretty=format:"%s" HEAD~10..HEAD)
  else
    RAW_COMMITS=$(git log --pretty=format:"%s" HEAD~"$COMMIT_COUNT"..HEAD 2>/dev/null \
                  || git log --pretty=format:"%s")
  fi
else
  RAW_COMMITS=$(git log --pretty=format:"%s" "$LAST_TAG..HEAD")
fi

export RAW_COMMITS NEW_VERSION

# ── Output 1: release_notes.md (flat list, preserves original behaviour) ──
FLAT_LIST=$(echo "$RAW_COMMITS" | sed 's/^/- /')

cat > release_notes.md << EOF
This is the latest set of releases that you can use with your agent of choice. We recommend using the Specify CLI to scaffold your projects, however you can download these independently and manage them yourself.

## Changelog

$FLAT_LIST

EOF

echo "Generated release_notes.md:"
cat release_notes.md

# ── Output 2: CHANGELOG.md (categorised section) ──────────────────────────
python3 << 'PYEOF'
import os, re
from datetime import date

new_version = os.environ['NEW_VERSION'].lstrip('v')
today = date.today().strftime('%Y-%m-%d')
raw = os.environ.get('RAW_COMMITS', '')

commits = [l.strip() for l in raw.splitlines() if l.strip()]

SKIP_PATTERNS = [
    r'\[skip ci\]',
    r'^chore\(release\)',
    r'^Merge (pull request|branch)',
    r'^Initial ',
]

TYPE_MAP = {
    'feat':     'Added',
    'fix':      'Fixed',
    'refactor': 'Changed',
    'chore':    'Changed',
    'style':    'Changed',
    'perf':     'Changed',
    'ci':       'Changed',
    'docs':     'Documentation',
}

sections = {'Added': [], 'Fixed': [], 'Changed': [], 'Documentation': []}

for msg in commits:
    if any(re.search(p, msg, re.I) for p in SKIP_PATTERNS):
        continue
    m = re.match(r'^(\w+)(?:\([^)]+\))?: (.+)', msg)
    if not m:
        continue
    section = TYPE_MAP.get(m.group(1))
    if section:
        sections[section].append(m.group(2).strip())

lines = [f"## [{new_version}] - {today}\n"]
for name, items in sections.items():
    if items:
        lines.append(f"\n### {name}\n\n")
        for item in items:
            lines.append(f"- {item}\n")

if len(lines) == 1:
    lines += ["\n### Changed\n\n", "- Minor updates and improvements\n"]

new_section = ''.join(lines)

try:
    with open('CHANGELOG.md', 'r') as f:
        content = f.read()
    insert = re.search(r'^## \[', content, re.MULTILINE)
    if insert:
        pos = insert.start()
        new_content = content[:pos] + new_section + "\n" + content[pos:]
    else:
        new_content = content.rstrip('\n') + "\n\n" + new_section
except FileNotFoundError:
    new_content = f"# Changelog\n\n{new_section}"

with open('CHANGELOG.md', 'w') as f:
    f.write(new_content)

print(f"Updated CHANGELOG.md — added section for v{new_version}")
PYEOF
