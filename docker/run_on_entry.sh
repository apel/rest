#!/bin/bash

# Replace locally configured variables in apel_rest
#SECRET_KEY
sed -i "s|not_a_secure_secret|$DJANGO_SECRET_KEY|g" /var/www/html/apel_rest/settings.py

#PROVIDERS_URL
sed -i "s|provider_url|$PROVIDERS_URL|g" /var/www/html/apel_rest/settings.py

# IAM_URL
sed -i "s|iam_url|$IAM_URL|g" /var/www/html/apel_rest/settings.py

# SERVER_IAM_ID
sed -i "s|server_iam_id|$SERVER_IAM_ID|g" /var/www/html/apel_rest/settings.py

# SERVER_IAM_SECRET
sed -i "s|server_iam_secret|$SERVER_IAM_SECRET|g" /var/www/html/apel_rest/settings.py

# ALLOWED_TO_POST
sed -i "s|\['allowed_to_post'\]|$ALLOWED_TO_POST|g" /var/www/html/apel_rest/settings.py

# BANNED_FROM_POST
sed -i "s|\['banned_from_post'\]|$BANNED_FROM_POST|g" /var/www/html/apel_rest/settings.py

# ALLOWED_FOR_GET
sed -i "s|\['allowed_for_get'\]|$ALLOWED_FOR_GET|g" /var/www/html/apel_rest/settings.py


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

# install IGTF trust bundle 10 minutes after start up
echo "yum -y update ca-policy-egi-core >> /var/log/IGTF-startup-update.log" | at now + 10 min

# set cronjob to update trust bundle every month
echo "0 10 1 * * root yum -y update ca-policy-egi-core >> ~/cronlog 2>&1" >> /etc/cron.d/IGTF-bundle-update

#keep docker running
while true
do
  sleep 1
done
