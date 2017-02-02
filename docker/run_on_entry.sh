#!/bin/bash

if [ -z "$MYSQL_PORT_3306_TCP_ADDR" ]
then
    MYSQL_PORT_3306_TCP_ADDR=$MYSQL_HOST
fi

echo "[client]
user=apel
password=$MYSQL_PASSWORD
host=$MYSQL_PORT_3306_TCP_ADDR" >> /etc/my.cnf

# add clouddb.cfg, so that the default user of mysql is APEL
echo "[db]
# type of database
backend = mysql
# host with database
hostname = $MYSQL_PORT_3306_TCP_ADDR
# port to connect to
port = 3306
# database name
name = apel_rest
# database user
username = apel
# password for database
password = $MYSQL_PASSWORD
# how many records should be put/fetched to/from database
# in single query
records = 1000
# option for summariser so that SummariseVMs is called
type = cloud" >> /etc/apel/clouddb.cfg

echo "
ALLOWED_FOR_GET=$ALLOWED_FOR_GET
SERVER_IAM_ID=\"$SERVER_IAM_ID\"
SERVER_IAM_SECRET=\"$SERVER_IAM_SECRET\"

" >> /var/www/html/apel_rest/settings.py

sed -i "s/Put a secret here/$DJANGO_SECRET_KEY/g" /var/www/html/apel_rest/settings.py

# fetch the crl first
fetch-crl
# then start the periodic fetch-url
service fetch-crl-cron start

# start apache
service httpd start

# start cron
service crond start

# start at
service atd start

# start the loader service
service apeldbloader-cloud start

# Make cloud spool dir owned by apache
chown apache -R /var/spool/apel/cloud/

# install IGTF trust bundle 10 minutes after start up
echo "yum -y update ca-policy-egi-core >> /var/log/IGTF-startup-update.log" | at now + 10 min

# set cronjob to update trust bundle every month
echo "0 10 1 * * root yum -y update ca-policy-egi-core >> ~/cronlog 2>&1" >> /etc/cron.d/IGTF-bundle-update

#keep docker running
while true
do
  sleep 1
done
