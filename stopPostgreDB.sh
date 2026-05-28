export PGDATA=~/myDB/data

# Find the port our server is running on
PGPORT=$(ps aux | grep "postgres -D $PGDATA" | grep -v grep | grep -oE '\-p [0-9]+' | awk '{print $2}')

if [ -z "$PGPORT" ]; then
    PGPORT=5432  # fallback to default
fi

# Check if our server is actually running
if ! pg_ctl -D $PGDATA status &> /dev/null; then
    echo "No PostgreSQL server is running at $PGDATA."
    exit 0
fi

# Stop our server
echo "Stopping PostgreSQL server on port $PGPORT..."
pg_ctl -D $PGDATA stop

echo ""
echo "your PostgreSQL server stopped."