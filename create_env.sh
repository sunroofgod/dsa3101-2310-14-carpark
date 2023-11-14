#!/bin/bash

echo "DATABASE_NAME=NUS-carpark-data" > .env
echo "MYSQL_PASSWORD=root_password" >> .env
echo "MYSQL_USERNAME=root" >> .env

echo ".env file created successfully."