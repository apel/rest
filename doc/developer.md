# Developers

If you would like to contribute to the APEL REST interface. 

* Fork us at https://github.com/apel/rest
* Create a feature branch off of `dev`
* When ready, submit a pull request.

See [here](README.md#running-the-docker-image-on-centos-7-and-ubuntu-1604) for instructions to run the Docker Images locally using docker-compose

# Setup from source (on Centos 6)
We recommend this for development work ONLY.

1. Install python, pip, mysql, apache, apache modules, trust bundle and other required RPMS for development.
    ```
    yum -y install python-pip python-devel mysql mysql-devel gcc httpd httpd-devel mod_wsgi mod_ssl cronie at ca-policy-egi-core fetch-crl python-iso8601 python-ldap git bash-completion tree
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
    git clone https://github.com/apel/rest.git /var/www/html
    ```

5. Create the database
    ```
    mysql -u root -e "create database apel_rest"
    mysql -u root apel_rest < schemas/cloud.sql
    mysql -u root apel_rest < schemas/cloud-extra.sql
    ```

6. Create a new, self signed, certificate
    ```
    mkdir /etc/httpd/ssl/
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/httpd/ssl/apache.key -out /etc/httpd/ssl/apache.crt
    ```

7. Copy the configuration files
    ```
    cp /var/www/html/conf/apel_rest_api.conf /etc/httpd/conf.d/apel_rest_api.conf
    cp /var/www/html/conf/ssl.conf /etc/httpd/conf.d/ssl.conf
    cp /var/www/html/conf/cloudloader.cfg /etc/apel/cloudloader.cfg
    cp /var/www/html/conf/cloudsummariser.cfg /etc/apel/cloudsummariser.cfg
    ```

8. Copy the script files
    ```
    cp /var/www/html/scripts/cloudsummariser /etc/cron.d/cloudsummariser
    cp /var/www/html/scripts/run_cloud_summariser.sh /usr/bin/run_cloud_summariser.sh
    cp /var/www/html/scripts/apeldbloader-cloud /etc/init.d/apeldbloader-cloud
    ```

9. Create log, run and spool directories
   ```
   mkdir /var/log/cloud
   mkdir /var/run/cloud
   mkdir -p /var/spool/apel/cloud/
   chown apache -R /var/spool/apel/cloud/
   ```

10. To allow successful GET requests, you will need to register your APEL REST instance with the Indigo DataCloud IAM and add IAM variables in `/var/www/html/apel_rest/settings.py`. You will also need to register a second service (the querying test service), and authorise it by adding it's ID to `ALLOWED_FOR_GET`
    ```
    SERVER_IAM_ID=
    SERVER_IAM_SECRET=
    ALLOWED_FOR_GET=
    ```

11. Run `python manage.py collectstatic`

12. Start Apache with `service httpd start`

13. Start the loader with `service apeldbloader-cloud start`

14. Navigate a web browser to "https://<hostname>/api/v1/cloud/record/summary/"
