#! /bin/bash
echo "creating db named ... "$USER"_eBay_DB"
cs166_createdb $USER'_eBay_DB'
cs166_db_status
