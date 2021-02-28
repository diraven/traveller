#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset
#set -o xtrace

# Build image.
bash devops/utils/echo_info.bash "Build $(pwd)"

docker build --tag crabot:local .
