#!/bin/bash
echo "This script will deploy the containers for INDIGO-DataCloud Accounting."

if [ $# -ne 1 ]
then
    echo "ERROR: Must supply APEL REST Image name as first arguement."
    exit -1
fi

apel_rest_image = $1

docker pull $apel_rest_image

echo "Configuring Database"
MYSQL_ROOT_PASSWORD="EagerOmega"
MYSQL_APEL_PASSWORD="${MYSQL_ROOT_PASSWORD}APEL"

docker run -v /var/lib/mysql --name apel-mysql -p 3306:3306 -e "MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD" -d mysql:5

#wait for apel-mysql to configure
sleep 30

docker exec apel-mysql mysql -u root -p$MYSQL_ROOT_PASSWORD -e "create database apel_rest"

# Create schema
docker exec apel-mysql mysql -u root -p$MYSQL_ROOT_PASSWORD apel_rest -e "`cat schemas/cloud.sql`"

# Partition tables
docker exec apel-mysql mysql -u root -p$MYSQL_ROOT_PASSWORD apel_rest -e "`cat schemas/cloud-extra.sql`"

echo "Done"

HOST_NAME=$(hostname)
echo "Creating (self-signed) cert of $HOST_NAME"

echo "Configuring APEL Server"
docker run -d --link apel-mysql:mysql -p 80:80 -p 443:443 -e "HOST_NAME=$HOST_NAME" -e "MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD" -e "MYSQL_APEL_PASSWORD=$MYSQL_APEL_PASSWORD" $apel_rest_image

# this allows the APEL REST interface to configure
sleep 60
echo "Done!"
