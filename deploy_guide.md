# Deployment Guide - Django Web Analytics

This guide explains how to deploy this Django application to another server with full database reconstruction (schema + data).

## Prerequisites

- Python 3.9+
- PostgreSQL 12+
- pip (Python package manager)
- pg_dump and pg_restore (PostgreSQL tools)

## Step 1: Export Data from Source Server

### 1.1 Export Database Schema (Django Migrations)

Migrations have been created and committed to this repository:
```bash
finance/migrations/0001_initial.py
```

This file contains the complete schema definition for all tables in `moao_db`.

### 1.2 Export Database Data (PostgreSQL Dump)

Run the dump script to export all data:
```bash
./dump_db.sh [optional_output_file.sql]
```

Example:
```bash
./dump_db.sh moao_db_full_dump.sql
```

This creates a custom-format dump file containing all data from `moao_db`.

### 1.3 Transfer Files to Target Server

Copy these files to the target server:
- The entire Django project (including `finance/migrations/0001_initial.py`)
- The database dump file (e.g., `moao_db_full_dump.sql`)

---

## Step 2: Setup on Target Server

### 2.1 Install Dependencies

```bash
pip3 install django psycopg2-binary bcrypt
```

### 2.2 Configure Database

Edit `sales_dashboard/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'moao_db',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 2.3 Create Database

```bash
sudo -u postgres createdb moao_db
```

### 2.4 Restore Database Data

Using the dump file created in Step 1.2:

```bash
pg_restore -h localhost -U postgres -d moao_db moao_db_full_dump.sql
```

Or if using plain SQL dump:
```bash
psql -h localhost -U postgres -d moao_db < moao_db_full_dump.sql
```

### 2.5 Apply Django Migrations (Schema Only)

Since the database is already restored with data, we need to tell Django that migrations are applied:

```bash
python3 manage.py migrate --fake-initial
```

Or if starting fresh with migrations only (no data dump):
```bash
python3 manage.py migrate
```

---

## Step 3: Verify Deployment

### 3.1 Create Superuser (Optional)

```bash
python3 manage.py createsuperuser
```

### 3.2 Run Server

```bash
./run.sh
```

Or manually:
```bash
python3 manage.py runserver 0.0.0.0:8000
```

### 3.3 Access Dashboard

Open browser and navigate to:
```
http://<server_ip>:8000/
```

---

## Alternative: Schema-Only Deployment

If you only need the schema (without data), follow these steps:

### 1. On target server, create the database:

```bash
sudo -u postgres createdb moao_db
```

### 2. Apply migrations:

```bash
python3 manage.py migrate
```

This will create all tables defined in `finance/migrations/0001_initial.py`.

### 3. Load data separately (if needed):

```bash
python3 manage.py loaddata data.json
```

---

## Files for Deployment

| File | Purpose |
|------|---------|
| `finance/migrations/0001_initial.py` | Database schema (Django migrations) |
| `moao_db_full_dump.sql` | Full database dump (schema + data) |
| `dump_db.sh` | Script to create database dump |
| `restore_db.sh` | Script to restore database (see below) |
| `deploy_guide.md` | This file |

---

## Quick Deploy Script

Create a `restore_db.sh` script on the target server:

```bash
#!/bin/bash
# restore_db.sh - Restore moao_db from dump

DUMP_FILE=${1:-"moao_db_full_dump.sql"}
DB_NAME="moao_db"
DB_USER="postgres"

echo "Dropping database if exists..."
sudo -u postgres dropdb --if-exists $DB_NAME

echo "Creating database..."
sudo -u postgres createdb $DB_NAME

echo "Restoring from dump: $DUMP_FILE"
pg_restore -h localhost -U $DB_USER -d $DB_NAME "$DUMP_FILE"

if [ $? -eq 0 ]; then
    echo "Restore completed successfully!"
else
    echo "Restore failed!"
    exit 1
fi
```

Make it executable:
```bash
chmod +x restore_db.sh
```

Usage:
```bash
./restore_db.sh moao_db_full_dump.sql
```

---

## Notes

- The `managed = False` setting in models means Django won't modify existing tables
- Migrations are used only for initial schema creation on new servers
- For existing databases, use `--fake-initial` to skip table creation
- Make sure the PostgreSQL user has proper permissions
- Update `ALLOWED_HOSTS` in `settings.py` for production deployment
