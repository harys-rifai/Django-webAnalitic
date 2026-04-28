#!/bin/bash
# restore_db.sh - Restore moao_db from dump
# Usage: ./restore_db.sh [dump_file]

DUMP_FILE=${1:-"moao_db_dump.sql"}
DB_NAME="moao_db"
DB_USER="postgres"

echo "========================================="
echo "Database Restore Script"
echo "========================================="

# Check if dump file exists
if [ ! -f "$DUMP_FILE" ]; then
    echo "Error: Dump file '$DUMP_FILE' not found!"
    echo "Usage: ./restore_db.sh [dump_file]"
    exit 1
fi

echo "Dropping database if exists..."
sudo -u postgres dropdb --if-exists $DB_NAME

echo "Creating database..."
sudo -u postgres createdb $DB_NAME

echo "Restoring from dump: $DUMP_FILE"
pg_restore -h localhost -U $DB_USER -d $DB_NAME "$DUMP_FILE" 2>&1

if [ $? -eq 0 ]; then
    echo "========================================="
    echo "Restore completed successfully!"
    echo "Database: $DB_NAME"
    echo "Dump file: $DUMP_FILE"
    echo "========================================="
else
    echo "Restore failed! Trying alternative method..."
    # Try with psql for plain SQL dumps
    sudo -u postgres psql -d $DB_NAME -f "$DUMP_FILE"
fi

# Mark migrations as applied (since we restored from dump)
echo ""
echo "Marking Django migrations as applied..."
python3 manage.py migrate --fake-initial

echo ""
echo "Done! You can now run the server with: python3 manage.py runserver"
