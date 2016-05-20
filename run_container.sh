#!/bin/bash

echo "This script will deploy the containers for INDIGO-DataCloud Accounting."

MYSQL_ROOT_PASSWORD="EagerOmega"

docker run -v /var/lib/mysql --name apel-mysql -p 3306:3306 -e "MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD" -d mysql

HOST_NAME=$(hostname)

echo "Creating (self-signed) cert of $HOST_NAME"

docker run -it --link apel-mysql:mysql -p 80:80 -p 443:443 -e "HOST_NAME=$HOST_NAME" gregcorbett/rest

# this is the mysql command to run from inside linked container
# mysql -h $MYSQL_PORT_3306_TCP_ADDR -u root -p
