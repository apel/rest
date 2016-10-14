# Service Reference Card Template

* Daemons running
  * httpd
  * crond
  * atd
  * apeldbloader-cloud

* Init commands (services started on container creation)
  * service httpd start
  * service crond start
  * service atd start
  * service apeldbloader-cloud start

* Configuration files location
  * /etc/httpd/conf.d/apel_rest_api.conf - forces SSL
  * /etc/httpd/conf.d/ssl.conf - configures SSL
  * /etc/apel/cloudloader.cfg - configuration for the loader
  * /etc/apel/cloudsummariser.cfg - configuration for the summariser

* Logfile locations
  * /var/log/cloud/loader.log - log file for the loader
  * /var/log/cloud/summariser.log - log file for the summariser

* Open ports
  * 80 - used by the APEL server service, by the Apache server and forwarded to the APEL server.
  * 443 - used by the APEL server service, by the Apache server (for HTTPS) and forwarded to the APEL server.
  * 3306 - used by the APEL server service and the MySQL service.

* Possible unit test of the service
  * Unit tests conducted during development via [TravisCI](https://travis-ci.org/apel/rest)
  * For end to end testing, data could be POSTED to the endpoint, summarised and the retrieved from the GET endpoint

* Where is service state held (and can it be rebuilt)
  * Service is deployed in a docker container, do not rebuild released docker containers without incrementing package information in version, i.e 1.1.0-1 => 1.1.0-2

* Cron jobs
  * /etc/cron.d/cloudsummariser - runs the summariser
  * /etc/cron.d/IGTF-bundle-update - updates the IGTF bundle on the first day of the month

* Security information
  * Access control Mechanism description (authentication & authorization)
    * X.509 certificates for POST requests
    * IAM tokens for GET requests
  
  * How to block/ban a user
    * To ban users accessing summaries, remove them from `ALLOWED_FOR_GET` in `/var/www/html/apel_rest/settings.py`
  
  * Network Usage
    * None
  
  * Firewall configuration
    * None
    
  * Security recommendations
    * None
