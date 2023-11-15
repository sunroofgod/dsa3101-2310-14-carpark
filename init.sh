#!/bin/bash

echo "DATABASE_NAME=NUS-carpark-data" > .env
echo "MYSQL_ROOT_PASSWORD=root_password" >> .env
echo "MYSQL_USERNAME=root" >> .env

echo ".env file created successfully."

python3 backend/database/__init__.py