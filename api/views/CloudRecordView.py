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
        logger = logging.getLogger(__name__)

        try:
            empaid = request.META['HTTP_EMPA_ID']
        except KeyError:
            empaid = 'noid'

        logger.info("Received message. ID = %s", empaid)

        try:
            signer = request.META['SSL_CLIENT_S_DN']
        except KeyError:
            logger.error("No DN supplied in header")
            return Response(status=401)

        # authorise DNs here
        if not self._signer_is_valid(signer):
            logger.error("%s not a valid provider", signer)
            return Response(status=403)

        if "_content" in request.POST.dict():
            # then POST likely to come via the rest api framework
            # hence use the content of request.POST as message
            body = request.POST.get('_content')

        else:
            # POST likely to comes through a browser client or curl
            # hence use request.body as message
            body = request.body

        logger.debug("Message body received: %s", body)

        for header in request.META:
            logger.debug("%s: %s", header, request.META[header])

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
            logger.error("Could not save %s/%s: %s", inqpath, name, err)

            response = "Data could not be saved to disk, please try again."
            return Response(response, status=500)

        logger.info("Message saved to in queue as %s/%s", inqpath, name)

        response = "Data successfully saved for future loading."
        return Response(response, status=202)

###############################################################################
#                                                                             #
# Helper methods                                                              #
#                                                                             #
###############################################################################

    def _get_provider_list(self):
        """Return a list of Indigo Providers."""
        logger = logging.getLogger(__name__)

        provider_list_request = urllib2.Request(settings.PROVIDERS_URL)
        provider_list_response = urllib2.urlopen(provider_list_request)

        try:
            return json.loads(provider_list_response.read())
        except ValueError:
            logger.error("List of providers could not be retrieved.")
            return {}

    def _signer_is_valid(self, signer_dn):
        """Return True is signer's host is listed as a Indigo Provider."""
        logger = logging.getLogger(__name__)

        # Get the hostname from the DN
        signer_split = signer_dn.split("=")
        signer = signer_split[len(signer_split)-1]

        providers = self._get_provider_list()

        try:
            for site_num, _ in enumerate(providers['rows']):
                if signer in providers['rows'][site_num]['value']['hostname']:
                    return True
        except KeyError:
            pass

        # If we have not returned while in for loop
        # then site must be invalid
        logger.info('Site is not found on list of providers')
        return False
