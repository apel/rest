# Administrators

## Kubernetes Deployment

YAML files have been provided for deployment in the `yaml` directory.

They are split by whether they pertain to the APEL Server or to the persistant MySQL database. These are then further divided into files for the service itself and the service's replication controller, which is responsible for keeping the service containers running.

There are, therefore, four YMAL files.

* `yaml/accounting-mysql-rc.yaml`       - This configures the replication controller for the MySQL service
* `yaml/accounting-mysql-service.yaml`  - This is the MySQL service
* `yaml/accounting-server-rc.yaml`      - This configures the replication controller for the APEL Server service
* `yaml/accounting-server-service.yaml` - This is the APEL server service

## Interacting with Running Docker Containers on Kubernetes

To do this, you must first install kubectl (See https://coreos.com/kubernetes/docs/latest/configure-kubectl.html for a guide how to do this)

1. List the "pods", you are looking for something of the form "accounting-server-rc-XXXXX"

   `kubectl -s kubernetes_ip --user="kubectl" --token="auth_token" --insecure-skip-tls-verify=true get pods --namespace=kube-system`

   Note, you will need to replace `kubernetes_ip` and `auth_token` with there proper values.

2. Open a terminal running on the Indigo Datacloud APEL Accounting Server

   `kubectl -s kubernetes_ip --user="kubectl" --token="auth_token" --insecure-skip-tls-verify=true exec -it accounting-server-rc-XXXXX --namespace=kube-system bash`

   Note, you will need to replace `accounting-server-rc-XXXXX` with its true value.

You should now have terminal access to the Accounting Server.

## Services Running in the Accounting Server Container

* `httpd`: The Apache webserver hosting the REST interface
* `cron` : Necessary to periodically run the Summariser
* `apeldbloader-cloud` : Loads received messages into the MySQL image

## Important Configuration files

* `/etc/init.d/apeldbloader-cloud` : Registers the cloud loader as a service

* `/etc/apel/cloudloader.cfg` : Configures the cloud loader

* `/etc/apel/cloudsummariser.cfg` : Configures the cloud summariser

* `/etc/httpd/conf.d/apel_rest_api.conf` : Enforces HTTPS

* `/etc/httpd/conf.d/ssl.conf` : Handles the HTTPS

## Important Scripts

* `/etc/cron.d/cloudsummariser` : Cron job that runs `run_cloud_summariser.sh`

* `/usr/bin/run_cloud_summariser.sh` : Stops the loader servic, summarises the database and restarts the loader
