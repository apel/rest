# Using the APEL Accounting REST Interface

## As a Provider

Providers can publish accounting records to the endpoint

https://indigo-paas.cloud.ba.infn.it/accounting/api/v1/cloud/record

To do this, Providers must be running OpenStack or OpenNubula and install the appropriate collectors.

* https://github.com/alvarolopez/caso if using OpenStack
* https://github.com/EGI-FCTF/oneacct_export if using OpenNebula

Providers may use APEL's Secure Stomp Messenger (SSM) to send accounting records. To do this, install the latest RPM and add `protocol: REST` to the sender.cfg

Set `https://indigo-paas.cloud.ba.infn.it/accounting/api/v1/cloud/record` to be the `destination:`

For more information on the SSM, please see https://github.com/apel/ssm



### Expected Responses
* 202: The data has been successfully saved for future loading and summarising.
* 401: A X509 certifcate was not provided by the request, your data was not saved.
* 403: A X509 certifcate was provided, but it was not authorised to publish, your data was not saved.
* 500: An unknown error has a occured, your data was not saved.

## As a Member of Indigo DataCloud

Micro services can retrieve accounting summaries from the endpoint

https://indigo-paas.cloud.ba.infn.it/accounting-server/api/v1/cloud/record/summary

The query space is limited by key=value pairs after a ? seperated by &

### For Example

https://indigo-paas.cloud.ba.infn.it/accounting/api/v1/cloud/record/summary?service="service_name"&from="YYYYMMDD"

### Supported key=value pairs

* group: The group with Indigo DataCloud
* service: The site that provided the resource
* to: Display summaries for dates (YYYYMMDD) up until this value
* from: Display summaries for dates (YYYYMMDD) up after this value

`from` is the only compulsary option, failure to include it will result in a 400 response.

### Expected Responses
* 200: Your request was succesfully met
* 400: No key=value pair provided for from
* 401: Your services OAuth token was not provided by the request, or was not successfully extracted by the server
* 403: Your services OAuth token was extracted by the server, but the IAM does not recognise it. 
* 500: An unknown error has a occured
