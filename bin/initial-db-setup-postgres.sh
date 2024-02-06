#!/usr/bin/env sh

set -eu

SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd )"
DATABASEMIGRATIONPATH="$SCRIPTPATH/../database-migrations"
cd "$DATABASEMIGRATIONPATH"

./gradlew -Dflyway.configFiles="$DATABASEMIGRATIONPATH/postgresql/flyway/local.conf" flywayMigrate -i
