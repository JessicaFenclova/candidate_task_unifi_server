#!/bin/bash
set -euo pipefail

cd /home/runner/actions-runner

# Registration token is only needed the first time; the config persists in the volume.
if [ ! -f .runner ]; then
  ./config.sh --unattended --replace \
    --url "${REPO_URL}" \
    --token "${RUNNER_TOKEN}" \
    --name "${RUNNER_NAME:-unifi-runner}" \
    --labels unifi
fi

exec ./run.sh
