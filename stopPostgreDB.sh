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

# Restore previous service if saved
if [ -f ~/.pg_previous_service ] && [ -f ~/.pg_previous_pgdata ]; then
    PREV_SERVICE=$(cat ~/.pg_previous_service)
    PREV_PGDATA=$(cat ~/.pg_previous_pgdata)

    echo "Restoring previous PostgreSQL service..."

    if [ "$PREV_SERVICE" == "brew" ]; then
        brew services start postgresql@16
        echo "✅ Homebrew PostgreSQL restored."
    elif [ "$PREV_SERVICE" == "pgctl" ]; then
        pg_ctl -D "$PREV_PGDATA" start
        echo "✅ pg_ctl PostgreSQL restored at: $PREV_PGDATA"
    fi

    # Clean up saved state
    rm ~/.pg_previous_service
    rm ~/.pg_previous_pgdata
else
    echo "No previous service to restore."
fi

echo ""
echo "✅ your PostgreSQL server stopped."