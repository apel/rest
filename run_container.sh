#!/bin/bash

echo "This script will deploy the containers for INDIGO-DataCloud Accounting."

MYSQL_ROOT_PASSWORD="EagerOmega"

docker run -v /var/lib/mysql --name apel-mysql -p 3306:3306 -e "MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD" -d mysql




HOST_NAME=$(hostname)

echo "Creating (self-signed) cert of $HOST_NAME"

docker run -it --link apel-mysql:mysql -p 80:80 -p 443:443 -e "HOST_NAME=$HOST_NAME" -e "MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD" gregcorbett/rest

# configure mysql
echo "[client]
user=root
password=$MYSQL_ROOT_PASSWORD
host=$MYSQL_PORT_3306_TCP_ADDR" >> /etc/my.cnf

#create APEL database in container
mysql -e "create database apel_rest"
mysql apel_rest < schemas/cloud.sql
