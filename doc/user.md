# Using the APEL Accounting REST Interface

## As a Provider

Providers can publish accounting records to the endpoint:

`.../api/v1/cloud/record`

To do this, Providers must be running OpenStack or OpenNebula and install the appropriate collectors. Links to these can be found at [List of Artifacts](https://indigo-dc.gitbooks.io/indigo-datacloud-releases/content/indigo1/accounting1.html)

### Expected Responses
* 202: The data has been successfully saved for future loading and summarising.
* 401: An X.509 certifcate was not provided by the request, your data was not saved.
* 403: An X.509 certifcate was provided, but it was not authorised to publish, your data was not saved.
* 500: An unknown error has a occured, your data was not saved.

## As a Member of Indigo DataCloud

Micro services can retrieve accounting summaries from the endpoint.

`.../api/v1/cloud/record/summary`

The query space is limited by key=value pairs after a "?" seperated by "&".

For Example:

`.../api/v1/cloud/record/summary?service="service_name"&from="YYYYMMDD"`

### Supported key=value pairs

* `group`: The group within Indigo DataCloud.
* `service`: The site that provided the resource.
* `to`: Display summaries for dates (YYYYMMDD) up until this value, but exclusive of it.
* `from`: Display summaries for dates (YYYYMMDD) after this value, but exclusive of it.

`from` is the only compulsary option, failure to include it will result in a 400 response.

### Expected Status Codes
* 200: Your request was succesfully met.
* 400: No key=value pair provided for from.
* 401: Your service's OAuth token was not provided by the request, or was not successfully extracted by the server.
* 403: Your service's OAuth token was extracted by the server, but the IAM does not recognise it.
* 500: An unknown error has a occured.

### Example Response Body
```
{
    "count": 2, 
    "next": null, 
    "previous": null, 
    "results": [
        {
            "VOGroup": "/TEST1", 
            "WallDuration": 86400, 
            "UpdateTime": null, 
            "Year": 2013, 
            "SiteName": "Test-Site", 
            "LatestStartTime": "2013-02-25T17:37:27", 
            "EarliestStartTime": "2013-02-25T17:37:27", 
            "Day": 26, 
            "Month": 2
        }, 
        {
            "VOGroup": "/TEST1", 
            "WallDuration": 86399, 
            "UpdateTime": null, 
            "Year": 2013, 
            "SiteName": "Test-Site", 
            "LatestStartTime": "2013-02-25T17:37:27", 
            "EarliestStartTime": "2013-02-25T17:37:27", 
            "Day": 27, 
            "Month": 2
        }
    ]
}
```
