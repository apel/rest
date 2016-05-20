FROM centos:6

MAINTAINER APEL Administrator <apel-admins@stfc.ac.uk>

# add EPEL repo so we can get pip
RUN rpm -ivh http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm

# install tools needed to get files from GitHub
# install python tools
# install mysql
# install apache
RUN yum -y install wget unzip python-pip python-devel python-ldap mysql mysql-devel gcc httpd httpd-devel mod_wsgi mod_ssl

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
RUN wget https://github.com/apel/rest/archive/start_docker_script.zip

# unzip APEL REST interface
RUN unzip start_docker_script.zip

# remove APEL REST zip
RUN rm start_docker_script.zip

# install APEL REST requirements
RUN cd rest-start_docker_script && pip install -r requirements.txt

# copy APEL REST files to apache root
RUN cp -r rest-start_docker_script/* /var/www/html/

# copy APEL REST conf files to apache conf
RUN cp /var/www/html/conf/apel_rest_api.conf /etc/httpd/conf.d/apel_rest_api.conf

# copy SSL conf files to apache conf
RUN cp /var/www/html/conf/ssl.conf /etc/httpd/conf.d/ssl.conf

# expose apache and SSL ports
EXPOSE 80
EXPOSE 443

ENTRYPOINT /rest-start_docker_script/docker/run_on_entry.sh
