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

# install python tools
# install mysql
# install apache
# install cron
# install at (for scheduling the IGTF update after start up)
# install IGTF trust bundle
# install fetch-crl
RUN yum -y install python-pip python-devel mysql mysql-devel gcc httpd httpd-devel mod_wsgi mod_ssl cronie at ca-policy-egi-core fetch-crl

# Copy APEL REST files to apache root
COPY . /var/www/html/

# install APEL REST requirements
RUN pip install -r /var/www/html/requirements.txt

# copy APEL REST conf files to apache conf
RUN cp /var/www/html/conf/apel_rest_api.conf /etc/httpd/conf.d/apel_rest_api.conf

# copy SSL conf files to apache conf
RUN cp /var/www/html/conf/ssl.conf /etc/httpd/conf.d/ssl.conf

# make a directory for the certificates
RUN mkdir /etc/httpd/ssl/

# Make apel config dir for db configs
RUN mkdir /etc/apel

# Make cloud spool dir
RUN mkdir -p /var/spool/apel/cloud/

# Make cloud spool dir owned by apache
RUN chown apache -R /var/spool/apel/cloud/

# Generate static files
RUN cd /var/www/html/ && echo "yes" | python manage.py collectstatic 

# expose apache and SSL ports
EXPOSE 80
EXPOSE 443

ENTRYPOINT /var/www/html/docker/run_on_entry.sh
