#!/bin/bash

#echo "Downloading Anaconda setup script..."
#wget https://repo.anaconda.com/archive/Anaconda3-2024.02-1-Linux-x86_64.sh

#echo "Running Anaconda setup script..."
#bash Anaconda3-2024.02-1-Linux-x86_64.sh -b -p ~/anaconda

#echo "Removing Anaconda setup script..."
#rm Anaconda3-2024.02-1-Linux-x86_64.sh

#activate conda
#eval "$($HOME/anaconda/bin/conda shell.bash hook)"

#echo "Running conda init..."
#conda init

#echo "Running conda update..."
#conda update -y conda

#echo "Installed conda version..."
#conda --version

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
docker-compose build

echo "Starting up airflow in detached mode..."
docker-compose up -d

echo "Airflow started successfully."
echo "Airflow is running in detached mode. "
echo "Run 'docker-compose logs --follow' to see the logs."
