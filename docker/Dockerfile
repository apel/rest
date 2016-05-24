FROM centos:6

MAINTAINER APEL Administrator <apel-admins@stfc.ac.uk>

# add EPEL repo so we can get pip
RUN rpm -ivh http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm

# install tools needed to get files from GitHub
# install python tools
# install mysql
# install apache
# install cron
RUN yum -y install wget unzip python-pip python-devel python-ldap mysql mysql-devel gcc httpd httpd-devel mod_wsgi mod_ssl vixie-cron

# get APEL codebase
RUN wget https://github.com/gregcorbett/apel/archive/apel-setup-script.zip

# unzip APEL codebase
RUN unzip apel-setup-script.zip

# install APEL
RUN cd apel-apel-setup-script && python setup.py install

# delete APEL codebase zip
RUN rm -f apel-setup-script.zip

# delete APEL codebase directory
RUN rm -rf apel-apel-setup-script

# get APEL REST interface
RUN wget https://github.com/apel/rest/archive/summariser.zip

# unzip APEL REST interface
RUN unzip summariser.zip

# remove APEL REST zip
RUN rm summariser.zip

# install APEL REST requirements
RUN cd rest-summariser && pip install -r requirements.txt

# copy APEL REST files to apache root
RUN cp -r rest-summariser/* /var/www/html/

# copy APEL REST conf files to apache conf
RUN cp /var/www/html/conf/apel_rest_api.conf /etc/httpd/conf.d/apel_rest_api.conf

# copy SSL conf files to apache conf
RUN cp /var/www/html/conf/ssl.conf /etc/httpd/conf.d/ssl.conf

# copy the cron job that runs the summariser
RUN cp /var/www/html/conf/cloudsummariser /etc/cron.d/cloudsummariser

# copy the script the cron job runs
RUN cp /var/www/html/conf/run_cloud_summariser.sh /usr/bin/run_cloud_summariser.sh

# register the dbloader-cloud as a service
RUN cp /var/www/html/conf/apeldbloader-cloud /etc/init.d/apeldbloader-cloud

# copy the cloud loader conf
RUN cp /var/www/html/conf/cloudloader.cfg /etc/apel/cloudloader.cfg

# cop the cloud summariser conf
RUN cp /var/www/html/conf/cloudsummariser.cfg /etc/apel/cloudsummariser.cfg

# expose apache and SSL ports
EXPOSE 80
EXPOSE 443

ENTRYPOINT /rest-summariser/docker/run_on_entry.sh
