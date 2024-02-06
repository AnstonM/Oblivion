#!/usr/bin/env sh

set -eu

SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd )"
DEVDOCKERPATH="$SCRIPTPATH/../database-migrations/dev-docker"

docker-compose -f "$DEVDOCKERPATH/docker-compose.yml" down
