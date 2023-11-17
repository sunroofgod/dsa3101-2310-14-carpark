#!/bin/bash

echo "DATABASE_NAME=NUS-carpark-data" > .env
echo "MYSQL_ROOT_PASSWORD=root_password" >> .env
echo "MYSQL_USERNAME=root" >> .env

echo ".env file created successfully."

sleep 60
python3 backend/database/__init__.py
python3 frontend/app.py
