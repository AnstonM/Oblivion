#!/usr/bin/env sh

set -eu

SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd )"
DEVDOCKERPATH="$SCRIPTPATH/../database-migrations/dev-docker"

docker-compose -f "$DEVDOCKERPATH/docker-compose.yml" up --build -d

# Make sure pg is ready to accept connections
until docker container exec -it postgres_db pg_isready;
do
  echo "Waiting for postgres to get ready to accept connections"
  sleep 1
done

# POST CONTAINER CREATION ACTIONS
# -------------------------------

# Run flyway migration
$SCRIPTPATH/../bin/initial-db-setup-postgres.sh
