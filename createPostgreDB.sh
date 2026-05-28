export DB_NAME=$USER"_eBay_DB"
echo "Creating database: $DB_NAME"

# Use PGPORT if set, fallback to 5432
export PGPORT=${PGPORT:-5432}

# Create the database
createdb -h localhost -p $PGPORT $DB_NAME

pg_ctl -D $PGDATA status

# Copy .dat files if any exist
if ls *.dat &> /dev/null; then
    echo "Copying .dat files to $PGDATA..."
    cp -a *.dat $PGDATA/
else
    echo "No .dat files found, skipping copy."
fi

# Replace cs166_psql with generic psql
if [ -f create_tables.sql ]; then
    echo "Running create_tables.sql on $DB_NAME..."
    psql -h localhost -p $PGPORT -U $USER -d $DB_NAME -f create_tables.sql
else
    echo "create_tables.sql not found, skipping."
fi

echo ""
echo "✅ Done! To connect to your database:"
echo "   psql -h localhost -p $PGPORT -U $USER -d $DB_NAME"