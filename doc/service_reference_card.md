# Accounting Service Reference Card

The Accounting service is made up of three containers
* APEL REST Interface
* APEL Server
* MySQL Database [Standard MySQL:5.6 image](https://hub.docker.com/_/mysql/) 

* Daemons running
  * APEL REST Interface
    * httpd
    * crond
    * atd
  * APEL Server 
    * apeldbloader-cloud
    * crond

* Init commands (services started on container creation)
  * APEL REST Interface
    * service httpd start
    * service crond start
    * service atd start
  * APEL Server
    * service apeldbloader-cloud start
    * service crond start

* Configuration file locations
  * APEL REST Interface
    * /etc/httpd/conf.d/apel_rest_api.conf - forces SSL.
    * /etc/httpd/conf.d/ssl.conf - configures SSL.
  * APEL Server
    * /etc/apel/cloudloader.cfg - configuration for the loader.
    * /etc/apel/cloudsummariser.cfg - configuration for the summariser.

* Logfile locations
  * APEL REST Interface
    * /var/log/httpd/error_log - the log file for the Django interface. All such
                                 messages get captured by the Apache server and
                                 are treated as errors
  * APEL Server
    * /var/log/cloud/loader.log - log file for the loader.
    * /var/log/cloud/summariser.log - log file for the summariser.

* Open ports
  * 80 - all traffic to this port is forwarded to port 443 by the Apache server.
  * 443 - the Apache server forwards (HTTPS) traffic to the APEL server, which returns a Django view for recognised URL patterns.
  * 3306 - used by the APEL server service and the MySQL service to communicate with each other.

* Possible unit test of the service
  * Continuous integration tests conducted during development via [TravisCI](https://travis-ci.org/apel/rest).
  * For end to end testing, data could be POSTED to the endpoint, summarised and then retrieved from the GET endpoint.

* Where is service state held (and can it be rebuilt)
  * Service is deployed in a docker container, do not rebuild released docker containers without incrementing package information in version, i.e 1.1.0-1 => 1.1.0-2

* Cron jobs
  * APEL REST Interface
    * /etc/cron.d/cloudsummariser - runs the summariser.
  * APEL Server
    * /etc/cron.d/IGTF-bundle-update - updates the IGTF bundle on the first day of the month.
    * /etc/cron.d/fetch-crl - updates the Certificate Revocation Lists every 6 hours

* Security information

The APEL REST Interface container is the only container with a public endpoint, as such it deals with authentication & authorization.

  * Access control Mechanism description (authentication & authorization)
    * X.509 certificates for POST requests
    * IAM tokens for GET requests
  
  * How to block/ban a user
    * To ban users accessing summaries, remove them from `ALLOWED_FOR_GET` in `/var/www/html/yaml/apel_rest_interface.env`.
    * To ban users sending job records, perhaps because a provider in the Indigo provider list is negatively effecting the quality of the service for users by bulk reppublishing, add their HostDN to `BANNED_FROM_POST` in `/var/www/html/yaml/apel_rest_interface.env`.
    * Additional users, not on the providers list, can also be granted POST rights, by adding their HostDN to `ALLOWED_TO_POST` in `/var/www/html/yaml/apel_rest_interface.env`.
    * Any changes to `/var/www/html/yaml/apel_rest_interface.env` require a container restart to take effect.
 
  * Network Usage
    * Managed by the Kubernetes cluster.
  
  * Firewall configuration
    * Managed by the Kubernetes cluster.
    
  * Security recommendations
    * Do not use a self signed certifcate in production.
