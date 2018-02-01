# Developers

If you would like to contribute to the APEL REST interface. 

* Fork us at https://github.com/apel/rest
* Create a feature branch off of `dev`
* When ready, submit a pull request.

See [here](README.md#running-the-docker-image-on-centos-7-and-ubuntu-1604) for instructions to run the Docker Images locally using docker-compose

# Setup from source (on CentOS 7)
We recommend this for development work ONLY.

1. Install python, pip, mysql, apache, apache modules, trust bundle and other required RPMS for development.
    ```
    yum -y install python-pip python-devel mysql-server mysql mysql-devel gcc httpd httpd-devel mod_wsgi mod_ssl cronie at ca-policy-egi-core fetch-crl python-iso8601 python-ldap git bash-completion tree
    ```
    
2. Upgrade pip and setuptools
    ```
    pip install pip --upgrade
    pip install setuptools --upgrade
    ```
    
3. Clone the repo to `/var/www/html
    ```
    git clone https://github.com/apel/rest.git /var/www/html
    ```

4. Install requirements.txt
    ```
    pip install -r /var/www/html/requirements.txt
    ```

5. Create the database
    ```
    mysql -u root -e "create user 'apel'@'localhost';"
    mysql -u root -e "GRANT ALL PRIVILEGES ON apel_rest.* TO 'apel'@'localhost';"
    mysql -u root -e "FLUSH PRIVILEGES;"
    mysql -u apel -e "create database apel_rest"
    mysql -u apel apel_rest < /var/www/html/schemas/10-cloud.sql
    mysql -u apel apel_rest < /var/www/html/schemas/20-cloud-extra.sql
    ```

6. Create a new, self signed, certificate
    ```
    mkdir /etc/httpd/ssl/
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/httpd/ssl/apache.key -out /etc/httpd/ssl/apache.crt
    ```

7. Create etc, log, run and spool directories
   ```
   mkdir /etc/apel
   mkdir /var/log/cloud
   mkdir /var/run/cloud
   mkdir -p /var/spool/apel/cloud/
   chown apache -R /var/spool/apel/cloud/
   ```

8. Symlink the local config files into the `/etc` directory. Note: these commands will override any existing configurations in those locations.
    ```
    ln -sf /var/www/html/conf/apel_rest_api.conf /etc/httpd/conf.d/apel_rest_api.conf
    ln -sf /var/www/html/conf/ssl.conf /etc/httpd/conf.d/ssl.conf
    ```

9. To allow successful GET requests, you will need to register your APEL REST instance with the Indigo DataCloud IAM and add IAM variables in `/var/www/html/apel_rest/settings.py`. You will also need to register a second service (the querying test service), and authorise it by adding it's ID to `ALLOWED_FOR_GET`
    ```
    IAM_HOSTNAME_LIST=
    SERVER_IAM_ID=
    SERVER_IAM_SECRET=
    ALLOWED_FOR_GET=
    ```

10. Run `python /var/www/html/manage.py collectstatic`

11. Start Apache with `service httpd start`

12. Navigate a web browser to `https://<hostname>/api/v1/cloud/record/summary`

## Optional: Set up a Docker-ized version of the APEL Server

Deploying an APEL Server along with the REST interface and database is not necessary, but is useful for allowing data to flow from input via the REST interface to summarised output via the REST interface. For the purposes of developing the APEL Rest interface we treat the APEL Server as a 'black box', so we recommend deploying it as a Docker image.

You will need to install Docker and Docker Compose first, see the [README.md](../README.md#running-the-docker-image-on-centos-7-and-ubuntu-1604) for a link to the instructions.

Then:

1. cd into `/var/www/html`

2. Follow step 7 in the [README.md](../README.md#running-the-docker-image-on-centos-7-and-ubuntu-1604).

3. Modify `docker/etc/apel/clouddb.cfg` so that the host with the database is `localhost`.

4. Run `docker-compose -f yaml/docker-compose.yaml run -v /var/lib/mysql:/var/lib/mysql -d --no-deps apel_server`

You should now have a running instance of the Docker-ized APEL Server, capable of talking to your development REST interface and database.

