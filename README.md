# rest
Experimental REST API for APEL

# Setup

1. Install python, pip, apache, apache modules and IGTF trust bundle
    ```
    yum install python-pip python-devel httpd httpd-devel mod_ssl mod_wsgi ca-policy-egi-core
    ```
    
2. upgrade pip and setuptools
    ```
    pip install pip --upgrade
    pip install setuptools --upgrade
    ```
3. install requirements.txt

4. Clone the repo to `/var/www/html`


5. Create a new, self signed, certificate
    ```
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/httpd/ssl/apache.key -out /etc/httpd/ssl/apache.crt
    ```
6. Open up the SSL config file: `vim /etc/httpd/conf.d/ssl.conf`

7. Find the section that begins with `<VirtualHost _default_:443>` and edit the following lines
    ```
    SSLEngine on
    SSLCertificateFile /etc/httpd/ssl/apache.crt
    SSLCertificateKeyFile /etc/httpd/ssl/apache.key
    SSLCACertificatePath /etc/grid-security/certificates
    SSLVerifyClient require
    SSLVerifyDepth  10
    ```

8. Open up the httpd config file: `vim /etc/httpd/conf/httpd.conf`

9. Find the section that begins with "# Redirect allows you" and add
    ```
    RewriteEngine On # enable http -> https redirects
    RewriteCond %{HTTPS} off
    RewriteRule (.*) https://%{HTTP_HOST}%{REQUEST_URI}
    ```

10. At the bottom of `httpd.conf`, add:
    ```
    <Directory /var/www/html/apel_rest>
    <Files wsgi.py>
    Allow from all
    </Files>
    </Directory>

    WSGISocketPrefix /var/run/wsgi
    WSGIDaemonProcess apel_rest python-path=/var/www/html:/usr/lib/python2.6/site-packages
    WSGIProcessGroup apel_rest
    WSGIScriptAlias / /var/www/html/apel_rest/wsgi.py
    
    Alias /static "/usr/lib/python2.6/site-packages/rest_framework/static"
    <Directory "/usr/lib/python2.6/site-packages/rest_framework/static">
    Allow from all
    </Directory>
    ```
    
11. Run `python manage.py collectstatic`

12. Start Apache with `service httpd start`

13. Navigate a web browser to "https://<hostname>/index/"
