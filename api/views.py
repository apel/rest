import datetime
import logging
import MySQLdb
import os

from dirq.queue import Queue, QueueError
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView


class IndexView(APIView):
    """An example URL."""

    def get(self, request, format=None):
        """An example get method."""
        logger = logging.getLogger(__name__)

        # parse query parameters
        group_name = request.GET.get('group', '')
        if group_name is "":
            group_name = None
        service_name = request.GET.get('service', '')

        if service_name is "":
            service_name = None

        start_date = request.GET.get('from', '')
        if start_date is "":
            # querying without a from is not supported
            return Response(status=501)

        end_date = request.GET.get('to', '')
        if end_date is "":
            end_date = datetime.datetime.now()

        logger.info("%s %s %s %s",
                    group_name,
                    service_name,
                    start_date,
                    end_date)

        # get the data requested
        database = MySQLdb.connect('localhost', 'root', '', 'apel_rest')
        cursor = database.cursor()

        if group_name is not None:
            cursor.execute('select * from CloudSummaries where VOGroupID = %s and EarliestStartTime > %s and LatestStartTime < %s',
                           [group_name, start_date, end_date])

        elif service_name is not None:
            cursor.execute('select * from CloudSummaries where SiteID = %s and EarliestStartTime > %s and LatestStartTime < %s',
                           [service_name, start_date, end_date])

        else:
            cursor.execute('select * from CloudSummaries where EarliestStartTime > %s',
                           [start_date])

        return_headers = ["VOGroupID",
                          "SiteID",
                          "UpdateTime",
                          "WallDuration",
                          "EarliestStartTime",
                          "LatestStartTime"]

        columns = cursor.description
        results = []
        for value in cursor.fetchall():
            result = {}
            for index, column in enumerate(value):
                header = columns[index][0]
                if header in return_headers:
                    result.update({header: column})
            results.append(result)

        return Response(results, status=200)

    def post(self, request, format=None):
        """An example post method."""
        logger = logging.getLogger(__name__)

        try:
            empaid = request.META['HTTP_EMPA_ID']
        except KeyError:
            empaid = 'noid'

        logger.info("Received message. ID = %s", empaid)

        try:
            signer = request.META['SSL_CLIENT_S_DN']
        except KeyError:
            signer = "None"

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
        # rejectqpath = os.path.join(qpath, 'reject')
        inq = Queue(inqpath, schema=QSCHEMA)
        # rejectq = Queue(rejectqpath, schema=REJECT_SCHEMA)

        try:
            name = inq.add({'body': body,
                            'signer': signer,
                            'empaid': empaid})
        except QueueError as err:
            logger.error("Could not save %s/%s: %s", inqpath, name, err)

            response = "Data could not be saved to disk, please try again."
            return Response(response, status=500)

        logger.info("Message saved to in queue as %s/%s", inqpath, name)
