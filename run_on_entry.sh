#!/bin/bash

# Need to add trust anchor repo
touch /etc/yum.repos.d/EGI-trustanchors.repo
echo -e "# EGI Software Repository - REPO META (releaseId,repositoryId,repofileId) - (10824,-,2000)\n[EGI-trustanchors]\nname=EGI-trustanchors\nbaseurl=http://repository.egi.eu/sw/production/cas/1/current/\nenabled=1\ngpgcheck=1\ngpgkey=http://repository.egi.eu/sw/production/cas/1/GPG-KEY-EUGridPMA-RPM-3" >> /etc/yum.repos.d/EGI-trustanchors.repo

# install IGTF trust bundle
yum -y install ca-policy-egi-core

# make dir for ssl keys
mkdir -p /etc/httpd/ssl

# create self signed certificates
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/httpd/ssl/apache.key -out /etc/httpd/ssl/apache.crt -subj "/C=GB/ST=Example/L=Example/O=Example/OU=Example/CN=$(hostname).$(domainname)"

# start apache
service httpd start
# start mysql
service mysqld start

#keep docker running
while true
do
  sleep 1
done
