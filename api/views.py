#from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from dirq.queue import Queue
import logging
import os

@require_http_methods(["GET", "POST"])
def index(request):
    logger = logging.getLogger(__name__)

    if request.method == 'GET':
        response = "Hello, world. You're at the index."
        logger.info(response)
        return HttpResponse(response, status=200)

    elif request.method == 'POST': # tecnically we dont need to check
                                   # as the only methods we allow
                                   # are get and post;
                                   # but better explicit then implicit
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
        #logger.debug(body)

        for header in request.META:
            logger.debug("%s: %s", header, request.META[header])

        inqpath = os.path.join(qpath, 'incoming')
        # rejectqpath = os.path.join(qpath, 'reject')
        inq = Queue(inqpath, schema=QSCHEMA)
        # rejectq = Queue(rejectqpath, schema=REJECT_SCHEMA)

        name = inq.add({'body': body,
                        'signer': 'Greg-Test-signer',
                        'empaid': empaid})

        response = "Message saved to in queue as %sincoming/%s" % (qpath, name)
        logger.info(response)
        return HttpResponse(response, status=202)
