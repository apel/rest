#!/bin/bash

# Replace locally configured variables in apel_rest
#SECRET_KEY
sed -i "s|not_a_secure_secret|$DJANGO_SECRET_KEY|g" /home/apel_rest_interface/apel_rest/settings.py

#PROVIDERS_URL
sed -i "s|provider_url|$PROVIDERS_URL|g" /home/apel_rest_interface/apel_rest/settings.py

# IAM_URL
sed -i "s|\['allowed_iams'\]|$IAM_URLS|g" /home/apel_rest_interface/apel_rest/settings.py

# SERVER_IAM_ID
sed -i "s|server_iam_id|$SERVER_IAM_ID|g" /home/apel_rest_interface/apel_rest/settings.py

# SERVER_IAM_SECRET
sed -i "s|server_iam_secret|$SERVER_IAM_SECRET|g" /home/apel_rest_interface/apel_rest/settings.py

# ALLOWED_TO_POST
sed -i "s|\['allowed_to_post'\]|$ALLOWED_TO_POST|g" /home/apel_rest_interface/apel_rest/settings.py

# BANNED_FROM_POST
sed -i "s|\['banned_from_post'\]|$BANNED_FROM_POST|g" /home/apel_rest_interface/apel_rest/settings.py

# ALLOWED_FOR_GET
sed -i "s|\['allowed_for_get'\]|$ALLOWED_FOR_GET|g" /home/apel_rest_interface/apel_rest/settings.py


# fetch the crl first
fetch-crl

# alter the fetch-crl cron to run regardless of any services
echo "# Cron job running by default every 6 hours, at 45 minutes past the hour
# with  +/- 3 minutes sleep.

45 */6 * * * root /usr/sbin/fetch-crl -q -r 360" >  /etc/cron.d/fetch-crl

# start apache
/usr/sbin/httpd

# start cron
/usr/sbin/crond

# start at
/usr/sbin/atd

# install IGTF trust bundle 10 minutes after start up
echo "yum -y update ca-policy-egi-core >> /var/log/IGTF-startup-update.log" | at now + 10 min

# set cronjob to update trust bundle every month
echo "0 10 1 * * root yum -y update ca-policy-egi-core >> ~/cronlog 2>&1" >> /etc/cron.d/IGTF-bundle-update

#keep docker running
while true
do
  sleep 1
done
