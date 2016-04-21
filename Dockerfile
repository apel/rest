FROM centos:6

MAINTAINER APEL Administrator <apel-admins@stfc.ac.uk>

RUN yum -y install wget

RUN wget https://github.com/gregcorbett/apel/archive/apel-setup-script.zip 
