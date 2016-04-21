FROM centos:6

MAINTAINER APEL Administrator <apel-admins@stfc.ac.uk>

RUN yum -y install wget unzip python-pip python-devel 

RUN pip install pip --upgrade

RUN pip install setuptools --upgrade

RUN wget https://github.com/gregcorbett/apel/archive/apel-setup-script.zip 

RUN unzip apel-setup-script.zip

RUN cd apel-apel-setup-script && python setup.py install


