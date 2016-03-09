# from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from dirq.queue import Queue
from rest_framework.views import APIView
from rest_framework.response import Response
import logging
import os

class IndexView(APIView):
    """An example URL."""

    def get(self,request,format=None):
        """An example get method"""
        logger = logging.getLogger(__name__)

        response = "Hello, world. You're at the index."
        logger.info(response)
        return Response(response, status=200)

    def post(self,request,format=None):
        """An example post method."""
        logger = logging.getLogger(__name__)

        try:
            empaid = request.META['HTTP_EMPA_ID']
        except KeyError:
            empaid = 'noid'

        logger.info("Received message. ID = %s", empaid)

        qpath = '/tmp/flask/'
        # taken from ssm2
        QSCHEMA = {'body': 'string',
                   'signer': 'string',
                   'empaid': 'string?'}

        body = request.body
        # logger.debug(body)

        for header in request.META:
            logger.debug("%s: %s", header, request.META[header])

        inqpath = os.path.join(qpath, 'incoming')
        # rejectqpath = os.path.join(qpath, 'reject')
        inq = Queue(inqpath, schema=QSCHEMA)
        # rejectq = Queue(rejectqpath, schema=REJECT_SCHEMA)

        name = inq.add({'body': body,
                        'signer': 'Greg-Test-signer',
                        'empaid': empaid})

        logger.info("Message saved to in queue as %s/%s" % (inqpath, name))
        return Response("The data received is well-formed and stored ready for later processing.", status=202)
