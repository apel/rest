#from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from dirq.queue import Queue
import logging
import os

LOG_BREAK = "=================================================="

@require_http_methods(["GET", "POST"])
def index(request):
    logger = logging.getLogger(__name__)
    

    if request.method == 'GET':
        return HttpResponse("Hello, world. You're at the index.", status=200)

    elif request.method == 'POST': # tecnically we dont need to check
                                   # as the only methods we allow
                                   # are get and post;
                                   # but better explicit then implicit
        qpath = '/tmp/flask/'
        # taken from ssm2
        QSCHEMA = {'body': 'string',
                   'signer': 'string',
                   'empaid': 'string?'}

        body = request.body
        logger.debug("Message Body")
        logger.debug(LOG_BREAK)
        logger.debug(body)

        logger.debug("Headers")
        logger.debug(LOG_BREAK)
        for header in request.META:
            logger.debug("%s: %s" % (header, request.META[header]))
        logger.debug(LOG_BREAK)

        inqpath = os.path.join(qpath, 'incoming')
        # rejectqpath = os.path.join(qpath, 'reject')
        inq = Queue(inqpath, schema=QSCHEMA)
        # rejectq = Queue(rejectqpath, schema=REJECT_SCHEMA)

        name = inq.add({'body': body,
                        'signer': 'Greg-Test-signer',
                        'empaid': 'Greg-Test-empaid'})

        response = "Message saved to in queue as %sincoming/%s" % (qpath, name)
        logger.debug("Response")
        logger.debug(LOG_BREAK)
        logger.debug(response)
        logger.debug(LOG_BREAK)
        return HttpResponse(response, status=202)
