FROM centos:6

MAINTAINER APEL Administrator <apel-admins@stfc.ac.uk>

# Add EPEL repo so we can get pip
RUN rpm -ivh http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm

# Add IGTF trust repo, so it can be installed
RUN touch /etc/yum.repos.d/EGI-trustanchors.repo
RUN echo -e $'# EGI Software Repository - REPO META (releaseId,repositoryId,repofileId) - (10824,-,2000)\n\
[EGI-trustanchors]\n\
name=EGI-trustanchors\n\
baseurl=http://repository.egi.eu/sw/production/cas/1/current/\n\
enabled=1\n\
gpgcheck=1\n\
gpgkey=http://repository.egi.eu/sw/production/cas/1/GPG-KEY-EUGridPMA-RPM-3' >> /etc/yum.repos.d/EGI-trustanchors.repo

# install tools needed to get files from GitHub
# install python tools
# install mysql
# install apache
# install cron
# install at (for scheduling the IGTF update after start up)
# install IGTF trust bundle
# install APEL requirements
RUN yum -y install wget unzip python-pip python-devel mysql mysql-devel gcc httpd httpd-devel mod_wsgi mod_ssl vixie-cron at ca-policy-egi-core MySQL-python python-iso8601 python-ldap

# get APEL codebase
RUN wget https://github.com/apel/apel/releases/download/1.5.1-1/apel-lib-1.5.1-1.el6.noarch.rpm
RUN wget https://github.com/apel/apel/releases/download/1.5.1-1/apel-server-1.5.1-1.el6.noarch.rpm

# Install APEL code base
# use --nodeps because we dont need the ssm
RUN rpm -i apel-lib-1.5.1-1.el6.noarch.rpm --nodeps
RUN rpm -i apel-server-1.5.1-1.el6.noarch.rpm --nodeps

# get APEL REST interface
RUN wget https://github.com/indigo-dc/Accounting/archive/1.0.0-1.zip -O apel_rest.zip

# unzip APEL REST interface and mv to apel_rest dir
RUN unzip apel_rest.zip && mv Accounting-1.0.0-1 apel_rest

# remove APEL REST zip
RUN rm apel_rest.zip

# install APEL REST requirements
RUN cd apel_rest && pip install -r requirements.txt

# copy APEL REST files to apache root
RUN cp -r apel_rest/* /var/www/html/

# copy APEL REST conf files to apache conf
RUN cp /var/www/html/conf/apel_rest_api.conf /etc/httpd/conf.d/apel_rest_api.conf

# copy SSL conf files to apache conf
RUN cp /var/www/html/conf/ssl.conf /etc/httpd/conf.d/ssl.conf
# make a directory for the certificates
RUN mkdir /etc/httpd/ssl/

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

# Make cloud log and run directory
RUN mkdir /var/log/cloud &&  mkdir /var/run/cloud

# Generate static files
RUN cd /var/www/html/ && echo "yes" | python manage.py collectstatic 

# Make cloud spool dir
RUN mkdir -p /var/spool/apel/cloud/

# expose apache and SSL ports
EXPOSE 80
EXPOSE 443

ENTRYPOINT /apel_rest/docker/run_on_entry.sh
