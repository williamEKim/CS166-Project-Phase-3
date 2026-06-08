#!/bin/bash
CURR_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

export DB_NAME=$USER"_eBay_DB"

source "$CURR_DIR/startPostgreSQL.sh"
source "$CURR_DIR/createPostgreDB.sh"
cs166_psql -p $PGPORT $DB_NAME < "$CURR_DIR/create_tables.sql"
cs166_psql -p $PGPORT $DB_NAME < "$CURR_DIR/initial_data.sql"
cs166_psql -p $PGPORT $DB_NAME < "$CURR_DIR/indexes.sql"