#!/usr/bin/env bash
set -euo pipefail

TAG="${1:?Usage: rollback-config.sh <git-tag>}"

cd /srv/docker

git restore --source "$TAG" .
echo "Restored tracked files from $TAG"
echo "Now review and restart needed stacks manually."
