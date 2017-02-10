"""This file contains the CloudRecordView class."""

import json
import logging
import os
import urllib2

from dirq.queue import Queue, QueueError
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView


class CloudRecordView(APIView):
    """
    Submit Cloud Accounting Records.

    .../api/v1/cloud/record

    Will save Cloud Accounting Records for later loading.
    """

    def __init__(self):
        """Set up class level logging."""
        self.logger = logging.getLogger(__name__)
        super(CloudRecordView, self).__init__()

    def post(self, request, format=None):
        """
        Submit Cloud Accounting Records.

        .../api/v1/cloud/record

        Will save Cloud Accounting Records for later loading.
        """
        try:
            empaid = request.META['HTTP_EMPA_ID']
        except KeyError:
            empaid = 'noid'

        self.logger.info("Received message. ID = %s", empaid)

        try:
            signer = request.META['SSL_CLIENT_S_DN']
        except KeyError:
            self.logger.error("No DN supplied in header")
            return Response(status=401)

        # authorise DNs here
        if not self._signer_is_valid(signer):
            self.logger.error("%s not a valid provider", signer)
            return Response(status=403)

        if "_content" in request.POST.dict():
            # then POST likely to come via the rest api framework
            # hence use the content of request.POST as message
            body = request.POST.get('_content')

        else:
            # POST likely to comes through a browser client or curl
            # hence use request.body as message
            body = request.body

        self.logger.debug("Message body received: %s", body)

        for header in request.META:
            self.logger.debug("%s: %s", header, request.META[header])

        # taken from ssm2
        QSCHEMA = {'body': 'string',
                   'signer': 'string',
                   'empaid': 'string?'}

        inqpath = os.path.join(settings.QPATH, 'incoming')
        inq = Queue(inqpath, schema=QSCHEMA)

        try:
            name = inq.add({'body': body,
                            'signer': signer,
                            'empaid': empaid})
        except QueueError as err:
            self.logger.error("Could not save %s/%s: %s", inqpath, name, err)

            response = "Data could not be saved to disk, please try again."
            return Response(response, status=500)

        self.logger.info("Message saved to in queue as %s/%s", inqpath, name)

        response = "Data successfully saved for future loading."
        return Response(response, status=202)

###############################################################################
#                                                                             #
# Helper methods                                                              #
#                                                                             #
###############################################################################

    def _get_provider_list(self):
        """Return a list of Resource Providers."""
        try:
            provider_list_request = urllib2.Request(settings.PROVIDERS_URL)
            provider_list_response = urllib2.urlopen(provider_list_request)
            return json.loads(provider_list_response.read())

        except (ValueError, urllib2.HTTPError) as error:
            self.logger.error("List of providers could not be retrieved.")
            self.logger.error("%s: %s", type(error), error)
            return {}

    def _signer_is_valid(self, signer_dn):
        """Return True if signer's host is listed as a Resource Provider."""
        # Get the hostname from the DN
        signer_split = signer_dn.split("=")
        signer = signer_split[len(signer_split)-1]

        if signer_dn in settings.BANNED_FROM_POST:
            self.logger.info("Host %s is banned.", signer)
            return False

        providers = self._get_provider_list()

        try:
            # Extract the site JSON objects from the returned JSON
            enumerated_providers = enumerate(providers['rows'])
        except KeyError:
            # The returned provider JSON is not of expected format.
            self.logger.error('Could not parse provider JSON.')
            return False

        for _, site_json in enumerated_providers:
            try:
                if signer in site_json['value']['hostname']:
                    return True
            except KeyError:
                # A KeyError is thrown if a hostname is not defined.
                # Log that a single site could not be parsed
                self.logger.warning('Could not parse site JSON.')
                self.logger.debug(site_json)
                # Continue looping through provider list, looking
                # for a match in the remaining site JSON

        if signer_dn in settings.ALLOWED_TO_POST:
            self.logger.info("Host %s has special access.", signer)
            return True

        # If we have not returned already
        # then site must be invalid
        self.logger.info('Site is not found on list of providers')
        return False
