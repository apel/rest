import ConfigParser
import datetime
import logging
import MySQLdb
import os

from dirq.queue import Queue, QueueError
from rest_framework.pagination import PaginationSerializer
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.response import Response
from rest_framework.views import APIView


class CloudRecordSummaryView(APIView):
    """
    Submit Cloud Accounting Records or Retrieve Cloud Accounting Summaries.
    GET Useage:

    .../computing/summaryrecord?Group=<group_name>&from=<date_from>&to=<date_to>

    Will return the summary for group_name at all services,
    between date_from and date_to as daily summaries

    .../computing/summaryrecord?service=<service_name>&from=<date_from>&to=<date_to>

    Will return the summary for service_name at all groups,
    between date_from and date_to as daily summaries

    .../computing/summaryrecord?&from=<date_from>
    Will give summary for whole infrastructure from <data> to now
    """

    def get(self, request, format=None):
        """
        Retrieve Cloud Accounting Summaries.

        .../computing/summaryrecord?Group=<group_name>&from=<date_from>&to=<date_to>

        Will return the summary for group_name at all services,
        between date_from and date_to as daily summaries

        .../computing/summaryrecord?service=<service_name>&from=<date_from>&to=<date_to>

        Will return the summary for service_name at all groups,
        between date_from and date_to as daily summaries

        .../computing/summaryrecord?&from=<date_from>
        Will give summary for whole infrastructure from <data> to now
        """
        logger = logging.getLogger(__name__)

        # parse query parameters
        (group_name,
         service_name,
         start_date,
         end_date) = self._parse_query_parameters(request)

        if start_date is None:
            # querying without a from is not supported
            return Response(status=501)

        # Read configuration from file
        try:
            dbcp = ConfigParser.ConfigParser()
            dbcp.read(settings.CLOUD_DB_CONF)

            db_hostname = dbcp.get('db', 'hostname')
            # db_port = int(dbcp.get('db', 'port'))
            db_name = dbcp.get('db', 'name')
            db_username = dbcp.get('db', 'username')
            db_password = dbcp.get('db', 'password')
        except (ConfigParser.Error, ValueError, IOError) as err:
            logger.warning('Error in configuration file %s: %s',
                           settings.CLOUD_DB_CONF,
                           str(err))
            logger.warning('Using default configuration.')

            db_hostname = 'localhost'
            db_name = 'apel_rest'
            db_username = 'root'
            db_password = ''

        # get the data requested
        try:
            database = MySQLdb.connect(db_hostname,
                                       db_username,
                                       db_password,
                                       db_name)
        except MySQLdb.OperationalError:
            logger.error("Could not connect to %s at %s using %s, %s",
                         db_name, db_hostname, db_username, db_password)
            return Response(status=500)

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

        results = self._filter_cursor(cursor)
        results = self._paginate_result(request, results)
        return Response(results, status=200)

###############################################################################
#                                                                             #
# Helper methods                                                              #
#                                                                             #
###############################################################################

    def _parse_query_parameters(self, request):
        """Parse expected query parameters from the given HTTP request."""
        group_name = request.GET.get('group', '')
        if group_name is "":
            group_name = None

        service_name = request.GET.get('service', '')
        if service_name is "":
            service_name = None

        start_date = request.GET.get('from', '')
        if start_date is "":
            start_date = None

        end_date = request.GET.get('to', '')
        if end_date is "":
            end_date = datetime.datetime.now()

        return (group_name, service_name, start_date, end_date)

    def _paginate_result(self, request, result):
        """Paginate result based on the request and apel_rest settings."""
        paginator = Paginator(result, settings.RESULTS_PER_PAGE)
        try:
            page = request.GET.get('page')
        except AttributeError:
            page = 1

        try:
            result = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            result = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999),
            # deliver last page of results.
            result = paginator.page(paginator.num_pages)

        # context allows for clickable REST Framework links
        serializer = PaginationSerializer(instance=result,
                                          context={'request': request})
        return serializer.data

    def _filter_cursor(self, cursor):
        """Filter database results based on setting.RETURN_HEADERS."""
        columns = cursor.description
        results = []
        for value in cursor.fetchall():
            result = {}
            for index, column in enumerate(value):
                header = columns[index][0]
                if header in settings.RETURN_HEADERS:
                    result.update({header: column})
            results.append(result)

        return results
