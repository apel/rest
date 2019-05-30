"""This file contains the CloudRecordSummaryView class."""

try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser
import datetime
import logging
import MySQLdb

from rest_framework.pagination import PaginationSerializer
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.response import Response
from rest_framework.views import APIView

from api.utils.TokenChecker import TokenChecker


class CloudRecordSummaryView(APIView):
    """
    Retrieve Cloud Accounting Summaries.

    Usage:

    .../api/v1/cloud/record/summary?user=<global_user_name>&from=<date_from>&to=<date_to>

    Will return the summary for global_user_name at all services,
    between date_from and date_to (exclusive) as daily summaries

    .../api/v1/cloud/record/summary?group=<group_name>&from=<date_from>&to=<date_to>

    Will return the summary for group_name at all services,
    between date_from and date_to (exclusive) as daily summaries

    .../api/v1/cloud/record/summary?service=<service_name>&from=<date_from>&to=<date_to>

    Will return the summary for service_name at all groups,
    between date_from and date_to (exclusive) as daily summaries

    .../api/v1/cloud/record/summary?from=<date_from>

    Will give summary for whole infrastructure from date_from
    (exclusive) to now
    """

    def __init__(self):
        """Set up class level logging."""
        self.logger = logging.getLogger(__name__)
        self._token_checker = TokenChecker()
        super(CloudRecordSummaryView, self).__init__()

    def get(self, request, format=None):
        """
        Retrieve Cloud Accounting Summaries.

        .../api/v1/cloud/record/summary?user=<global_user_name>&from=<date_from>&to=<date_to>

        Will return the summary for global_user_name at all services,
        between date_from and date_to (exclusive) as daily summaries

        .../api/v1/cloud/record/summary?group=<group_name>&from=<date_from>&to=<date_to>

        Will return the summary for group_name at all services,
        between date_from and date_to (exclusive) as daily summaries

        .../api/v1/cloud/record/summary?service=<service_name>&from=<date_from>&to=<date_to>

        Will return the summary for service_name at all groups,
        between date_from and date_to (exclusive) as daily summaries

        .../api/v1/cloud/record/summary?from=<date_from>

        Will give summary for whole infrastructure from
        date_from (exclusive) to now
        """
        client_token = self._request_to_token(request)
        if client_token is None:
            return Response(status=401)

        # The token checker will introspect the token,
        # i.e. check it's in-date, correctly signed etc
        # and return the client_id of the token
        client_id = self._token_checker.valid_token_to_id(client_token)
        if client_id is None:
            return Response(status=401)

        if not self._is_client_authorized(client_id):
            return Response(status=403)

        # parse query parameters
        (group_name,
         service_name,
         start_date,
         end_date,
         global_user_name) = self._parse_query_parameters(request)

        # Check that at most one of group_name, service_name
        # and global_user_name is set as having more than
        # one defined is currently ambiguous while retrieval
        # against only one parameter per GET request is supported.
        parameters_to_check = (group_name, service_name, global_user_name)
        set_count = sum([1 for para in parameters_to_check if para is None])
        if set_count <= 1:
            self.logger.error("User, Group and/or Service combined.")
            self.logger.error("Rejecting request.")
            return Response("Only one of User, Group and Service can be set.",
                            status=400)

        if start_date is None:
            # querying without a from is not supported
            return Response("'from' must be set in GET requests.",
                            status=400)

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
            self.logger.warning('Error in configuration file %s: %s',
                                settings.CLOUD_DB_CONF,
                                err)
            self.logger.warning('Using default configuration.')

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
            self.logger.error("Could not connect to %s at %s using %s, %s",
                              db_name, db_hostname, db_username, db_password)
            return Response(status=500)

        cursor = database.cursor(MySQLdb.cursors.DictCursor)

        if global_user_name is not None:
            cursor.execute('select * from VCloudSummaries '
                           'where GlobalUserName = %s '
                           'and EarliestStartTime > %s '
                           'and LatestStartTime < %s',
                           [global_user_name, start_date, end_date])

        elif group_name is not None:
            cursor.execute('select * from VCloudSummaries '
                           'where VOGroup = %s '
                           'and EarliestStartTime > %s '
                           'and LatestStartTime < %s',
                           [group_name, start_date, end_date])

        elif service_name is not None:
            cursor.execute('select * from VCloudSummaries '
                           'where SiteName = %s and '
                           'EarliestStartTime > %s and '
                           'LatestStartTime < %s',
                           [service_name, start_date, end_date])

        else:
            cursor.execute('select * from VCloudSummaries '
                           'where EarliestStartTime > %s',
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

        global_user_name = request.GET.get('user', '')
        if global_user_name is "":
            global_user_name = None

        # Log query parameters
        self.logger.debug("Query Parameters")
        self.logger.debug("Group name = %s", group_name)
        self.logger.debug("Service name = %s", service_name)
        self.logger.debug("Start date = %s", start_date)
        self.logger.debug("End date = %s", end_date)
        self.logger.debug("Global Username = %s", global_user_name)

        return (group_name, service_name, start_date,
                end_date, global_user_name)

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
        """
        Filter database results based on settings.RETURN_HEADERS.

        Allows for configuration of what summary fields
        the REST interface returns on GET requests.
        """
        results_list = []
        # Use results_list to store individual summaries to before returning.
        for record in cursor.fetchall():
            # record refers to one day's summary
            result = {}
            # result is used to construct a new, filtered, summary with
            # only the values listed in settings.RETURN_HEADERS.
            for key, value in record.iteritems():
                if key in settings.RETURN_HEADERS:
                    # keys listed in settings.RETURN_HEADERS represent
                    # summary fields the REST interface has been configured
                    # to return. As such we need to add that field to the
                    # new summary we are constructing
                    result.update({key: value})

            results_list.append(result)

        return results_list

    def _request_to_token(self, request):
        """Get the token from the request."""
        try:
            token = request.META['HTTP_AUTHORIZATION'].split()[1]
        except KeyError:
            self.logger.error("No AUTHORIZATION header provided, "
                              "authentication failed.")
            return None
        except IndexError:
            self.logger.error("AUTHORIZATION header provided, "
                              "but not of expected form.")
            self.logger.error(request.META['HTTP_AUTHORIZATION'])
            return None
        self.logger.info("Successfully extracted Token")
        self.logger.debug("Full Token: %s", token)
        return token

    def _is_client_authorized(self, client_id):
        """
        Return true if and only if client_id can access summaries.

        i.e. client_id is not None and is in settings.ALLOWED_FOR_GET.
        """
        if client_id is None or client_id not in settings.ALLOWED_FOR_GET:
            self.logger.error("%s does not have permission to view summaries",
                              client_id)
            return False
        self.logger.info("Authorizing user request")
        return True
