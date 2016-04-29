#!/bin/bash

echo "This script will deploy the containers for INDIGO-DataCloud Accounting."

docker run -d -p 80:80 -p 443:443 gregcorbett/rest /usr/sbin/apachectl -D FOREGROUND
