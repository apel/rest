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

        logging.info("Received message. ID = %s", empaid)

        try:
            signer = request.META['SSL_CLIENT_S_DN']
        except KeyError:
            logging.error("No DN supplied in header")
            return Response(status=401)

        # authorise DNs here
        if not self._signer_is_valid(signer):
            logging.error("%s not a valid provider", signer)
            return Response(status=403)

        if "_content" in request.POST.dict():
            # then POST likely to come via the rest api framework
            # hence use the content of request.POST as message
            body = request.POST.get('_content')

        else:
            # POST likely to comes through a browser client or curl
            # hence use request.body as message
            body = request.body

        logging.debug("Message body received: %s", body)

        for header in request.META:
            logging.debug("%s: %s", header, request.META[header])

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
            logging.error("Could not save %s/%s: %s", inqpath, name, err)

            response = "Data could not be saved to disk, please try again."
            return Response(response, status=500)

        logging.info("Message saved to in queue as %s/%s", inqpath, name)

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
            logging.error("List of providers could not be retrieved.")
            logging.error("%s: %s", type(error), error)
            return {}

    def _signer_is_valid(self, signer_dn):
        """Return True if signer's host is listed as a Resource Provider."""
        # Get the hostname from the DN
        signer_split = signer_dn.split("=")
        signer = signer_split[len(signer_split)-1]

        providers = self._get_provider_list()

        try:
            for site_num, _ in enumerate(providers['rows']):
                if signer in providers['rows'][site_num]['value']['hostname']:
                    return True
        except KeyError:
            logging.error('Could not parse list of providers.')

        # If we have not returned while in for loop
        # then site must be invalid
        logging.info('Site is not found on list of providers')
        return False
