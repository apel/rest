#!/bin/bash
echo "This script will deploy the containers for INDIGO-DataCloud Accounting."

if [ $# -ne 1 ]
then
    echo "ERROR: Must supply APEL REST Image name as first arguement."
    exit -1
fi

apel_rest_image=$1

docker pull $apel_rest_image

echo "Configuring Database"

MYSQL_ROOT_PASSWORD=
MYSQL_DATABASE="apel_rest"
MYSQL_USER="apel"
MYSQL_PASSWORD="${MYSQL_ROOT_PASSWORD}APEL"

docker run -v /var/lib/mysql --name apel-mysql -p 3306:3306 -e "MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD" -e "MYSQL_DATABASE=$MYSQL_DATABASE" -e "MYSQL_USER=$MYSQL_USER" -e "MYSQL_PASSWORD=$MYSQL_PASSWORD" -d mysql:5.6

#wait for apel-mysql to configure
sleep 30

# Create schema
docker exec apel-mysql mysql -u root -p$MYSQL_ROOT_PASSWORD apel_rest -e "`cat schemas/cloud.sql`"

# Partition tables
docker exec apel-mysql mysql -u root -p$MYSQL_ROOT_PASSWORD apel_rest -e "`cat schemas/cloud-extra.sql`"

echo "Done"

echo "Configuring APEL Server"

ALLOWED_FOR_GET=
SERVER_IAM_ID=
SERVER_IAM_SECRET=
DJANGO_SECRET_KEY=

docker run -d --link apel-mysql:mysql -p 80:80 -p 443:443 -e "MYSQL_PASSWORD=$MYSQL_PASSWORD" -e "ALLOWED_FOR_GET=$ALLOWED_FOR_GET" -e "SERVER_IAM_ID=$SERVER_IAM_ID" -e "SERVER_IAM_SECRET=$SERVER_IAM_SECRET" -e "DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY" $apel_rest_image

# this allows the APEL REST interface to configure
sleep 60
echo "Done!"
