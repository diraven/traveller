#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset
#set -o xtrace

# Build image.
devops/build.bash

# Test image.
bash devops/utils/echo_info.bash "Test $(pwd)"

docker run crabot:local devops/utils/test_container.bash
