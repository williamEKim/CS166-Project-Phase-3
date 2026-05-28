export DB_NAME=$USER"_eBay_DB"
echo "creating db named ... "$DB_NAME
createdb -h localhost -p $PGPORT $DB_NAME
pg_ctl status

cp -a *.dat $PGDATA/

cs166_psql $DB_NAME < create_tables.sql
