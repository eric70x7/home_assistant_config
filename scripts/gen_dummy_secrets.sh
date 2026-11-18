#!/usr/bin/env bash
# Generates a dummy secrets.yaml for CI validation only.
# Scans all YAML files for !secret references and emits
# placeholder values keyed by the names actually used.
# Never touches or exposes the real secrets.yaml (which is
# gitignored anyway).

set -euo pipefail

keys=$(grep -rhoP '!secret\s+\K[\w-]+' \
  --include='*.yaml' \
  . | sort -u)

echo "# Auto-generated dummy secrets for CI check_config only."
for key in ${keys}; do
  echo "${key}: dummy"
done
