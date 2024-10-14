#!/bin/bash

# Navigate to the app directory
cd data  # Adjust if your Dockerfile WORKDIR is different

# Execute Alembic command
alembic upgrade head

cd ..
