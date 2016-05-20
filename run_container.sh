#!/bin/bash

echo "This script will deploy the containers for INDIGO-DataCloud Accounting."

HOSTNAME=$(hostname)

echo "Creating (self-signed) cert of $HOSTNAME"

docker run -d -p 80:80 -p 443:443 gregcorbett/rest  -e "HOSTNAME=$HOSTNAME"
