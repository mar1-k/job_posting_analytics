#!/bin/bash
echo "Running sudo apt-get update..."
sudo apt-get update

echo "Granting Permissions to airflow folder..."
sudo chmod -R 777 ./

echo "Installing unzip..."
sudo apt-get -y install unzip

echo "Installing Docker..."
sudo apt-get -y install docker

echo "Installing docker-compose..."
sudo apt-get -y install docker-compose

echo "docker-compose version: " 
docker-compose --version

echo "Building airflow docker images..."
sudo docker-compose build

echo "Starting up airflow in detached mode..."
sudo docker-compose up -d

echo "Airflow started successfully."
echo "Airflow is running in detached mode. "
echo "Run 'docker-compose logs --follow' to see the logs."
