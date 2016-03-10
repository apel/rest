# REST
Experimental REST API for APEL

# Setup

1. Install python, pip, apache, apache modules and IGTF trust bundle
    ```
    yum install python-pip python-devel httpd httpd-devel mod_ssl mod_wsgi ca-policy-egi-core
    ```
    
2. Upgrade pip and setuptools
    ```
    pip install pip --upgrade
    pip install setuptools --upgrade
    ```
    
3. Install requirements.txt

4. Clone the repo to `/var/www/html`

5. Create a new, self signed, certificate
    ```
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/httpd/ssl/apache.key -out /etc/httpd/ssl/apache.crt
    ```
6. Copy `conf/httpd.conf` to `/etc/httpd/conf/httpd.conf` 

7. Copy `conf/ssl.connf` to `/etc/httpd/conf.d/ssl.conf`

8. Run `python manage.py collectstatic`

9. Start Apache with `service httpd start`

10. Navigate a web browser to "https://\<hostname\>/index/"
