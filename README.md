# REST

[![Build Status](https://travis-ci.org/apel/rest.svg?branch=dev)](https://travis-ci.org/apel/rest)
[![Coverage Status](https://coveralls.io/repos/github/apel/rest/badge.svg?branch=dev)](https://coveralls.io/github/apel/rest?branch=dev)

Experimental REST API for APEL

## Using the docker image

1. install docker and httpd (httpd is needed on the host machine for `/usr/sbin/apachectl`, do NOT start httpd)

2. pull in the latest image: `docker pull gregcorbett/rest`

3. Run the docker with `docker run -d -p 80:80 -p 443:443 gregcorbett/rest /usr/sbin/apachectl -D FOREGROUND`

4. Navigate a web browser to "https://\<hostname\>/index/"

The Docker Image does not enforce HTTPS connecitons due to it's primary deployment being on Indigo DataCloud infrastructure.

## Setup from source

1. Install python, pip, mysql, apache, apache modules and IGTF trust bundle
    ```
    yum install python-pip python-devel httpd httpd-devel mysql mysql-server mysql-devel gcc mod_ssl mod_wsgi ca-policy-egi-core
    ```
    
2. Upgrade pip and setuptools
    ```
    pip install pip --upgrade
    pip install setuptools --upgrade
    ```
    
3. Install requirements.txt

4. Clone the repo to `/var/www/html`

5. Run `mysql -u root -e "create database apel_rest"` and `mysql -u root apel_rest < schemas/cloud.sql` to set up database

6. Create a new, self signed, certificate
    ```
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/httpd/ssl/apache.key -out /etc/httpd/ssl/apache.crt
    ```
7. Copy `conf/httpd.conf` to `/etc/httpd/conf/httpd.conf` 

8. Copy `conf/ssl.connf` to `/etc/httpd/conf.d/ssl.conf`

9. Uncomment the HTTPS re-direct code in `conf/apel_rest_api.conf` for a secure instance

10. Copy `conf/apel_rest_api.conf` to `/etc/httpd/conf.d/apel_rest_api.conf`

11. Uncomment the HTTPS re-direct code in `conf/apel_rest_api.conf` for a secure instance

12. Run `python manage.py collectstatic`

13. Start Apache with `service httpd start`

14. Navigate a web browser to "https://\<hostname\>/index/"
