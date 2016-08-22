# REST API for APEL
[![Build Status](https://travis-ci.org/apel/rest.svg?branch=dev)](https://travis-ci.org/apel/rest)
[![Coverage Status](https://coveralls.io/repos/github/apel/rest/badge.svg?branch=dev)](https://coveralls.io/github/apel/rest?branch=dev)

The APEL project provides accounting for the Indigo DataCloud project. It is written in Python and uses MySQL.

## Overview
APEL Cloud Accounting can account for the usage of OpenNebula and OpenStack instances. Accounting "collectors" need to be installed on machines with access to the underlying Cloud infrastructure. The collectors can be found here: https://indigo-dc.gitbooks.io/indigo-datacloud-releases/content/indigo1/accounting1.html

The collectors produce "Usage Records" in the APEL-Cloud v0.2 message format. Information about this format can be found here: https://wiki.egi.eu/wiki/Federated_Cloud_Accounting#Cloud_Accounting_Message_Format_for_use_with_SSM_2.0

These records need to be sent as POST requests to the REST end point .../api/v1/cloud/record, where ... is the machine hosting the docker image. A POST request requires a X.509 certificate to authenticate the request. The hostnam eof the X.509 certificate must be listed as a provider here http://indigo.cloud.plgrid.pl/cmdb/service/list for the request to be authorized.

Accepted records are summarised twice daily. These summaries can be accessed with a GET request to .../api/v1/cloud/record/summary. Summaries can be filtered using key=value pairs. See [Supported key=value pairs](doc/user.md) for a list of valid supported key=value pairs. A GET request requires a IAM access token be included in the request. This token is then sent to the IAM to authenticate the ID of the service requesting access to the summary. This ID needs to be in "ALLOWED_FOR_GET" in apel_rest/settings.py for access to be authorized. See [Authorize new WP5 components to view Summaries](doc/admin.md) for instructions on adding service to "ALLOWED_FOR_GET"

It is currently expected that only the QoS/SLA tool will interact with these summaries.


## Using the docker image

1. Install docker

2. Download the corresponding run_container.sh script corresponding to the release.

3. Populate the MYSQL variables and and IAM variables

4. Run `./run_container.sh indigo-dc/Accounting:X.X.X-X`

5. Before the server will start, a certificate needs to be added to the container. Run `docker exec -it <docker_id> bash` to enter the container and then execute step 6 of the "Setup from source" instructions.

6. Navigate a web browser to "https://\<hostname\>/index/"

## Setup from source

1. Install python, pip, mysql, apache, apache modules, trust bundle and other required RPMS for development.
    ```
    yum -y install wget unzip python-pip python-devel mysql mysql-devel gcc httpd httpd-devel mod_wsgi mod_ssl vixie-cron at ca-policy-egi-core MySQL-python python-iso8601 python-ldap git bash-completion tree
    ```
    
2. Upgrade pip and setuptools
    ```
    pip install pip --upgrade
    pip install setuptools --upgrade
    ```
    
3. Install requirements.txt
    ```
    pip install -r requirements.txt
    ```

4. Clone the repo to `/var/www/html`
    ```
    cd /var/www/
    git clone git@github.com:apel/rest.git
    mv rest html
    ```

5. Run `mysql -u root -e "create database apel_rest"` and `mysql -u root apel_rest < schemas/cloud.sql` to set up database

6. Partition the database with `mysql -u root apel_rest < schemas/cloud-extra.sql`

7. Create a new, self signed, certificate
    ```
    mkdir /etc/httpd/ssl/
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/httpd/ssl/apache.key -out /etc/httpd/ssl/apache.crt
    ```

8. Copy the configuration files
    ```
    cp /var/www/html/conf/apel_rest_api.conf /etc/httpd/conf.d/apel_rest_api.conf
    cp /var/www/html/conf/ssl.conf /etc/httpd/conf.d/ssl.conf
    cp /var/www/html/conf/cloudloader.cfg /etc/apel/cloudloader.cfg
    cp /var/www/html/conf/cloudsummariser.cfg /etc/apel/cloudsummariser.cfg
    ```

9. Copy the script files
    ```
    cp /var/www/html/scripts/cloudsummariser /etc/cron.d/cloudsummariser
    cp /var/www/html/scripts/run_cloud_summariser.sh /usr/bin/run_cloud_summariser.sh
    cp /var/www/html/scripts/apeldbloader-cloud /etc/init.d/apeldbloader-cloud
    ```

10. Create log, run and spool directories
     ```
     mkdir /var/log/cloud
     mkdir /var/run/cloud
     mkdir -p /var/spool/apel/cloud/
     chown apache -R /var/spool/apel/cloud/
     ```

11. To allow successful GET requests, you will need to register your APEL REST instance with the Indigo DataCloud IAM and add IAM variables in `/var/www/html/apel_rest/settings.py`. You will also need to register a second service (the querying service), and authorise it by adding it's ID to `ALLOWED_FOR_GET`
    ```
    SERVER_IAM_ID=
    SERVER_IAM_SECRET=
    ALLOWED_FOR_GET=
    ```

12. Run `python manage.py collectstatic`

13. Start Apache with `service httpd start`

14. Start the loader with `service apeldbloader-cloud start`

15. Navigate a web browser to "https://<hostname>/api/v1/cloud/record/summary/"
