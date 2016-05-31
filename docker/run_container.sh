#!/bin/bash
echo "This script will deploy the containers for INDIGO-DataCloud Accounting."

docker pull gregcorbett/rest

echo "Configuring Database"
MYSQL_ROOT_PASSWORD="EagerOmega"
MYSQL_APEL_PASSWORD="${MYSQL_ROOT_PASSWORD}APEL"

docker run -v /var/lib/mysql --name apel-mysql -p 3306:3306 -e "MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD" -d mysql

#wait for apel-mysql to configure
sleep 30

docker exec apel-mysql mysql -u root -p$MYSQL_ROOT_PASSWORD -e "create database apel_rest"
docker exec apel-mysql mysql -u root -p$MYSQL_ROOT_PASSWORD apel_rest -e "`cat schemas/cloud.sql`"

echo "Done"

HOST_NAME=$(hostname)
echo "Creating (self-signed) cert of $HOST_NAME"

echo "Configuring APEL Server"
docker run -d --link apel-mysql:mysql -p 80:80 -p 443:443 -e "HOST_NAME=$HOST_NAME" -e "MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD" -e"MYSQL_APEL_PASSWORD=$MYSQL_APEL_PASSWORD" gregcorbett/rest

# this allows the APEL REST interface to configure
sleep 60
echo "Done!"
