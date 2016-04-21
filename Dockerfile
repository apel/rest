FROM centos:6

MAINTAINER APEL Administrator <apel-admins@stfc.ac.uk>

RUN cd

RUN yum -y install wget unzip python.x86_64 

RUN wget https://github.com/gregcorbett/apel/archive/apel-setup-script.zip 

RUN unzip apel-setup-script.zip

RUN cd apel-apel-setup-script

RUN ls

RUN python setup.py install


