FROM centos:6

MAINTAINER APEL Administrator <apel-admins@stfc.ac.uk>

RUN rpm -ivh http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm

RUN yum -y install wget unzip python-pip python-devel gcc 

RUN pip install pip --upgrade

RUN pip install setuptools --upgrade

RUN wget https://github.com/gregcorbett/apel/archive/apel-setup-script.zip 

RUN unzip apel-setup-script.zip

RUN cd apel-apel-setup-script && python setup.py install


