#!/bin/bash
# PostgreSQL Database Dump Script for moao_db
# Usage: ./dump_db.sh [output_file]

OUTPUT_FILE=${1:-"moao_db_dump_$(date +%Y%m%d_%H%M%S).sql"}

echo "Dumping database moao_db..."
pg_dump -h localhost -U postgres -d moao_db -F c -f "$OUTPUT_FILE"

if [ $? -eq 0 ]; then
    echo "Dump completed successfully: $OUTPUT_FILE"
    ls -lh "$OUTPUT_FILE"
else
    echo "Dump failed!"
    exit 1
fi
