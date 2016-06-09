#!/bin/bash

# Need to add trust anchor repo
touch /etc/yum.repos.d/EGI-trustanchors.repo
echo -e "# EGI Software Repository - REPO META (releaseId,repositoryId,repofileId) - (10824,-,2000)\n[EGI-trustanchors]\nname=EGI-trustanchors\nbaseurl=http://repository.egi.eu/sw/production/cas/1/current/\nenabled=1\ngpgcheck=1\ngpgkey=http://repository.egi.eu/sw/production/cas/1/GPG-KEY-EUGridPMA-RPM-3" >> /etc/yum.repos.d/EGI-trustanchors.repo

# install IGTF trust bundle
yum -y install ca-policy-egi-core

if [ -z $MYSQL_PORT_3306_TCP_ADDR ]
then
    $MYSQL_PORT_3306_TCP_ADDR = $MYSQL_HOST
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
hostname = 10.254.10.21
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

# start apache
service httpd start

#start cron
service crond start

# start the loader service
service apeldbloader-cloud start

# Make cloud spool dir owned by apache
chown apache -R /var/spool/apel/cloud/

#keep docker running
while true
do
  sleep 1
done
