#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

./scripts/build.sh
./scripts/init-db.sh
./scripts/run-all.sh
./scripts/check-output.sh
