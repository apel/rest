# REST API for APEL
[![Build Status](https://travis-ci.org/apel/rest.svg?branch=dev)](https://travis-ci.org/apel/rest)
[![Coverage Status](https://coveralls.io/repos/github/apel/rest/badge.svg?branch=dev)](https://coveralls.io/github/apel/rest?branch=dev)

The APEL project provides accounting for the Indigo DataCloud project. It is written in Python and uses MySQL.

## Overview
APEL Cloud Accounting can account for the usage of OpenNebula and OpenStack instances. Accounting "collectors" need to be installed on machines with access to the underlying Cloud infrastructure. The collectors can be found [here](https://indigo-dc.gitbooks.io/indigo-datacloud-releases/content/indigo1/accounting1.html).

The collectors produce "Usage Records" in the APEL-Cloud v0.2 message format. Information about this format can be found [here](https://wiki.egi.eu/wiki/Federated_Cloud_Accounting#Cloud_Accounting_Message_Format_for_use_with_SSM_2.0).

These records need to be sent as POST requests to the REST endpoint `.../api/v1/cloud/record`, where `...` is the machine hosting the docker image. A POST request requires an X.509 certificate to authenticate the request. The hostname, which should be the same as the common name (CN) contained in the X.509 certificate, must be listed as a provider [here](http://indigo.cloud.plgrid.pl/cmdb/service/list) for the request to be authorized.

Accepted records are summarised twice daily. These summaries can be accessed with a GET request to `.../api/v1/cloud/record/summary`. Summaries can be filtered using `key=value` pairs. See [Supported key=value pairs](doc/user.md#supported-keyvalue-pairs) for a list of valid supported `key=value` pairs. A GET request requires an IAM access token be included in the request. This token is then sent to the IAM to authenticate the ID of the service requesting access to the summary. This ID needs to be in `ALLOWED_FOR_GET` in `apel_rest/settings.py` for access to be authorized. See [Authorize new WP5 components to view Summaries](doc/admin.md#authorize-new-wp5-components-to-view-summaries) for instructions on adding service to `ALLOWED_FOR_GET`

It is currently expected that only the QoS/SLA tool will interact with these summaries.

### Features of Version 1.2.1-1

- Accept APEL-Cloud v0.2 usage records via POST requests to the REST endpoint `.../api/v1/cloud/record`
- Provide access to summaries via GET requests to REST endpoint `.../api/v1/cloud/record/summary`

## Running the docker image on Centos 7 and Ubuntu 14.04
We recommend using the docker image to run the Accounting server and REST interface. As such, having Docker installed is a prerequisite.

See [Ubuntu 14.04 Instructions](https://docs.docker.com/engine/installation/linux/ubuntulinux/) or [Centos 7 Instructions](https://docs.docker.com/engine/installation/linux/centos/) for details of how to install Docker.

1. Download the run_container.sh script corresponding to the release, see [here](https://github.com/indigo-dc/Accounting/releases) for a list of releases and corresponding docker image tag. This script launches the APEL Server container and can (by default) set up an instance of the database needed to store the accounting data. This database itself is within a docker container.

2. Register the service as a protected resource with the Indigo Identity Access Management (IAM). See [here](doc/admin.md#register-the-service-as-a-protected-resource-with-the-indigo-identity-access-management-iam) for instructions.

3. Populate the following variables in `docker/run_container.sh`
   ```
   MYSQL_ROOT_PASSWORD: The APEL server will use this to communicate with the database. If run_container.sh
                        is deploying the database (which by default it will be) the database root password
                        is set to this.

   MYSQL_PASSWORD: The APEL server will use this to communicate with the database. If run_container.sh
                   is deploying the database (which by default it will be) the APEL user password
                   is set to this.

   ALLOWED_FOR_GET: A (python) list of IAM service IDs allowed to submit GET requests. This bash variable
                    needs to be interpreted by python as a list of strings
                    (i.e. [\'ac2f23e0-8103-4581-8014-e0e82c486e36\'])

   SERVER_IAM_ID: An IAM ID corresponding to this instance, used to validate tokens.

   SERVER_IAM_SECRET: An IAM secret corresponding to this instance, used to validate tokens.

   DJANGO_SECRET_KEY: The Django server requires its own "secret".
   ```

4. Run `./docker/run_container.sh indigodatacloud/accounting:X.X.X-X`, where X.X.X-X is the version number container to launch.

5. Before the server will start, a certificate needs to be added to the container. This can be done by either modifying `./run_container.sh` to load the docker image with a certificate mounted into it, or by interacting with the image after start up with `docker exec -it <docker_id> bash`. If choosing the latter, run `service httpd start` before exiting the container.

6. Navigate a web browser to `https://\<hostname\>/index/`
