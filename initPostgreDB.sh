# Check and install PostgreSQL if not installed
if ! command -v pg_ctl &> /dev/null; then
    echo "PostgreSQL not found. Installing..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt-get update && sudo apt-get install -y postgresql
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install postgresql
    else
        echo "Unsupported OS. Please install PostgreSQL manually."
        exit 1
    fi
else
    echo "PostgreSQL is already installed."
fi

export PGDATA=~/myDB/data

# Only init if data dir doesn't exist yet
if [ ! -d "$PGDATA" ]; then
    initdb -D $PGDATA
else
    echo "Database already initialized, skipping initdb."
fi

# Find a free port starting from 5432
find_free_port() {
    local port=5432
    while lsof -i :$port &> /dev/null; do
        echo "Port $port is in use, trying next..." >&2
        port=$((port + 1))
    done
    echo $port
}

export PGPORT=$(find_free_port)
echo "Using port $PGPORT"

# Start our server on the free port
echo "Starting PostgreSQL server at $PGDATA on port $PGPORT..."
pg_ctl -D $PGDATA -o "-p $PGPORT" start

pg_ctl -D $PGDATA status

echo ""
echo "To connect, run:"
echo "  psql -p $PGPORT -U $USER postgres"
echo ""
echo "To stop the server later, run:"
echo "  pg_ctl -D $PGDATA stop"