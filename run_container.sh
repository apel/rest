#!/bin/bash

echo "This script will deploy the containers for INDIGO-DataCloud Accounting."


echo "Configuring Database"
MYSQL_ROOT_PASSWORD="EagerOmega"

docker run -v /var/lib/mysql --name apel-mysql -p 3306:3306 -e "MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD" -d mysql

docker exec apel-mysql mysql -u root -p$MYSQL_ROOT_PASSWORD -e "create database apel_rest"
docker exec apel-mysql mysql -u root -p$MYSQL_ROOT_PASSWORD -e apel_rest < schemas/cloud.sql

echo "Done"

HOST_NAME=$(hostname)
echo "Creating (self-signed) cert of $HOST_NAME"

echo "Configuring APEL Server"
docker run -it --link apel-mysql:mysql -p 80:80 -p 443:443 -e "HOST_NAME=$HOST_NAME" -e "MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD" gregcorbett/rest
