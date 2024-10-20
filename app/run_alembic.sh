#!/bin/bash

# Load environment variables from the .env file
set -o allexport
source .env
set -o allexport

# Navigate to the app directory
cd data  # Adjust if your Dockerfile WORKDIR is different

# Set up variables from the .env file
DB_NAME=${POSTGRES_DB}    # Assuming POSTGRES_DB is in your .env
DB_USER=${POSTGRES_USER}  # Assuming POSTGRES_USER is in your .env
DB_PASSWORD=${POSTGRES_PASSWORD}  # Assuming POSTGRES_PASSWORD is in your .env
DB_HOST="db"              # This should match the service name in your docker-compose
DB_PORT="5432"            # Default PostgreSQL port
BACKUP_DIR="backups"
BACKUP_FILE="${BACKUP_DIR}/backup_$(date +'%Y%m%d_%H%M%S').sql"

# Ensure the backup directory exists
mkdir -p $BACKUP_DIR

# Step 1: Create a database backup inside the container
echo "Creating database backup..."
PGPASSWORD=$DB_PASSWORD pg_dump -U $DB_USER -h $DB_HOST -p $DB_PORT -d $DB_NAME > $BACKUP_FILE

# Check if the backup was successful
if [ $? -eq 0 ]; then
    echo "Backup created successfully: $BACKUP_FILE"
else
    echo "Backup failed! Aborting Alembic upgrade." >&2
    exit 1
fi

# Step 2: Execute Alembic migrations
echo "Running Alembic migrations..."
alembic upgrade head

# Navigate back
cd ..
