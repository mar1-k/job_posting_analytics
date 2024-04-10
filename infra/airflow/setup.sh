#!/bin/bash
echo "Running sudo apt-get update..."
sudo apt-get update

echo "Installing Docker..."
sudo apt-get -y install docker

echo "Docker without sudo setup..."
sudo groupadd docker
sudo gpasswd -a $USER docker
sudo service docker restart

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
