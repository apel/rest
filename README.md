# REST API for APEL
[![Build Status](https://travis-ci.org/apel/rest.svg?branch=dev)](https://travis-ci.org/apel/rest)
[![Coverage Status](https://coveralls.io/repos/github/apel/rest/badge.svg?branch=dev)](https://coveralls.io/github/apel/rest?branch=dev)

The APEL project provides accounting for the Indigo DataCloud project. It is written in Python and uses MySQL.

## Overview
APEL Cloud Accounting can account for the usage of OpenNebula and OpenStack instances. Accounting "collectors" need to be installed on machines with access to the underlying Cloud infrastructure. The collectors can be found [here](https://indigo-dc.gitbooks.io/indigo-datacloud-releases/content/indigo1/accounting1.html).

The collectors produce "Usage Records" in the APEL-Cloud v0.2 or v0.4 message formats. Information about these format can be found [here](https://wiki.egi.eu/wiki/Federated_Cloud_Accounting#Documentation).

These records need to be sent as POST requests to the REST endpoint `.../api/v1/cloud/record`, where `...` is the machine hosting the docker image. A POST request requires an X.509 certificate to authenticate the request. The hostname, which should be the same as the common name (CN) contained in the X.509 certificate, must be listed as a provider [here](http://indigo.cloud.plgrid.pl/cmdb/service/list) or be given special access via the `ALLOWED_TO_POST` enviroment variable for the request to be authorized.

Accepted records are summarised twice daily. These summaries can be accessed with a GET request to `.../api/v1/cloud/record/summary`. Summaries can be filtered using `key=value` pairs. See [Supported key=value pairs](doc/user.md#supported-keyvalue-pairs) for a list of valid supported `key=value` pairs. A GET request requires an IAM access token be included in the request. This token is then sent to the IAM to authenticate the ID of the service requesting access to the summary. This ID needs to be in `ALLOWED_FOR_GET` in `yaml/apel_rest_interface.env` for access to be authorized.

It is currently expected that only the QoS/SLA tool will interact with these summaries.

### Features of Version 1.4.0-1

- Accept APEL-Cloud v0.2 and v0.4 usage records via POST requests to the REST endpoint `.../api/v1/cloud/record`
- Provide access to summaries via GET requests to REST endpoint `.../api/v1/cloud/record/summary`

## Running the Docker image on Centos 7 and Ubuntu 16.04
We recommend using the Docker image to run the Accounting server and REST interface. As such, having Docker installed is a prerequisite.

See [Ubuntu 16.04 Instructions](https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/) or [Centos 7 Instructions](https://docs.docker.com/engine/installation/linux/docker-ce/centos/) for details of how to install Docker. There is no requirement to undertake the 'Post-installation steps for Linux'.

We also reccomend using Docker Compose or Anisble to deploy the containers.
* See [Install Docker Compose](https://docs.docker.com/compose/install/) for details of how to install Docker Compose.
* See [Install Ansible ](http://docs.ansible.com/ansible/latest/intro_installation.html#installation) for details of how to install Ansible.

The instructions below are for both Docker Compose and Ansibe.

1. Download the compressed source code from [here](https://github.com/indigo-dc/Accounting/releases/latest), it does not matter where the source code is downloaded to. As the source code contains schemas and yaml files needed for deploying via docker-compose or ansible, you will need to unzip the source code and then `cd` into the inflated directory.

2. Register the service as a protected resource with the Indigo Identity Access Management (IAM) service. See [Register the service as a protected resource with the Indigo Identity Access Management (IAM)](doc/admin.md#register-the-service-as-a-protected-resource-with-the-indigo-identity-access-management-iam) for instructions, before proceeding to step 3.

3. Populate the following variables in `yaml/apel_rest_interface.env`
   ```
   DJANGO_SECRET_KEY: The Django server requires its own "secret".

   PROVIDERS_URL: Points to the JSON list of Resource Providers

   IAM_URL: The introspect URL for the IAM repsonsible for token based authN/authZ

   SERVER_IAM_ID: An IAM ID corresponding to this instance, used to validate tokens.

   SERVER_IAM_SECRET: An IAM secret corresponding to this instance, used to validate tokens.

   ALLOWED_FOR_GET: A (Python) list of IAM service IDs allowed to submit GET requests.
                    (e.g. ['ac2f23e0-8103-4581-8014-e0e82c486e36'])

   ALLOWED_TO_POST: A (Python) list of X.509 HostDNs allowed to submit POST requests,
                    in addition to those listed by the PROVIDERS_URL.
                    (e.g. ['/C=XX/O=XX/OU=XX/L=XX/CN=special_host.test'])

   BANNED_FROM_POST: A (Python) list of X.509 HostDNs banned from submitting POST requests,
                    even if they are listed by the PROVIDERS_URL.
                    (e.g. ['/C=XX/O=XX/OU=XX/L=XX/CN=banned_host.test'])
   ```

4. Populate the following variables in `yaml/mysql.env`
   ```
   MYSQL_ROOT_PASSWORD: The APEL server will use this to communicate with the database. If run_container.sh
                        is deploying the database (which by default it will be), the database root password
                        is set to this.

   MYSQL_PASSWORD: The APEL server will use this to communicate with the database. If run_container.sh
                   is deploying the database (which by default it will be) the APEL user password
                   is set to this.
   ```

5. `MYSQL_PASSWORD` will also need to be added to the password field `docker/etc/apel/clouddb.cfg` and `docker/etc/mysql/my.cnf`

6. Before the REST interface will start, a certificate needs to be added to the container. This can be done by placing a certificate (`apache.crt`) and key (`apache.key`) under `/etc/httpd/ssl/`. This directory will be mounted into the container by docker-compose.

7. If you are running Docker as a non-root user, you will need to make `docker/etc/cron.d` owned by `root`. This is because this directory gets mounted into the container and it needs to be owned by `root` for cron jobs in the container to run.
   ```
   sudo chown -R root docker/etc/cron.d
   ```

8. Launch the containers.

- With Docker Compose:

   It is recommeded to wait 1 minute after launching the database in order for it to configure fully before launching the APEL containers
   ```
   docker-compose -f yaml/docker-compose.yaml up -d --force-recreate apel_mysql
   # Wait 1 minute
   docker-compose -f yaml/docker-compose.yaml up -d --force-recreate apel_server
   docker-compose -f yaml/docker-compose.yaml up -d --force-recreate apel_rest_interface
   ```

- With Ansible:

   First, replace `<working directory>` in `yaml/ansible.yaml` with the absolute file path of the decompressed source code, then run the command below.
   ```
   ansible-playbook yaml/ansible.yml
   ```

9. Navigate a web browser to `https://<hostname>/api/v1/cloud/record/summary`
