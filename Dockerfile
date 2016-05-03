FROM centos:6

MAINTAINER APEL Administrator <apel-admins@stfc.ac.uk>

RUN rpm -ivh http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm

# Need to add trust anchor repo
RUN touch /etc/yum.repos.d/EGI-trustanchors.repo 
RUN echo -e "# EGI Software Repository - REPO META (releaseId,repositoryId,repofileId) - (10824,-,2000)\n[EGI-trustanchors]\nname=EGI-trustanchors\nbaseurl=http://repository.egi.eu/sw/production/cas/1/current/\nenabled=1\ngpgcheck=1\ngpgkey=http://repository.egi.eu/sw/production/cas/1/GPG-KEY-EUGridPMA-RPM-3" >> /etc/yum.repos.d/EGI-trustanchors.repo

RUN yum -y install wget unzip

RUN yum -y install python-pip python-devel python-ldap

RUN yum -y install gcc

RUN yum -y install mysql-server mysql-devel mysql

RUN yum -y install httpd httpd-devel

RUN yum -y install mod_wsgi mod_ssl ca-policy-egi-core

RUN wget https://github.com/gregcorbett/apel/archive/apel-setup-script.zip 

RUN unzip apel-setup-script.zip

RUN cd apel-apel-setup-script && python setup.py install

RUN rm -f apel-setup-script.zip

RUN rm -rf apel-apel-setup-script

RUN wget https://github.com/apel/rest/archive/load_post_requests.zip

RUN unzip load_post_requests.zip 

RUN rm load_post_requests.zip

RUN cd rest-load_post_requests && pip install -r requirements.txt

RUN service mysqld start

RUN cd rest-load_post_requests && mysql -u root -h localhost apel_rest < schemas/cloud.sql

RUN cp -r rest-load_post_requests/* /var/www/html/

RUN rm -rf rest-load_post_requests

RUN mkdir -p /etc/httpd/ssl

RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/httpd/ssl/apache.key -out /etc/httpd/ssl/apache.crt -subj "/C=GB/ST=London/L=London/O=Example/OU=Example/CN=example.com"

RUN cp /var/www/html/conf/apel_rest_api.conf /etc/httpd/conf.d/apel_rest_api.conf

RUN cp /var/www/html/conf/ssl.conf /etc/httpd/conf.d/ssl.conf

RUN service httpd start

EXPOSE 80
EXPOSE 443
