#!/bin/bash

echo "This script will deploy the containers for INDIGO-DataCloud Accounting."

docker run -d -v /var/lib/mysql --name apel-mysql --entrypoint /bin/echo mysql

HOST_NAME=$(hostname)

echo "Creating (self-signed) cert of $HOST_NAME"

docker run -d --volumes-from apel-mysql -p 80:80 -p 443:443 -e "HOST_NAME=$HOST_NAME" gregcorbett/rest
