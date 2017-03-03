"""This module tests GET requests to the Cloud Sumamry Record endpoint."""

import logging
import MySQLdb

from api.views.CloudRecordSummaryView import CloudRecordSummaryView
from django.core.urlresolvers import reverse
from django.test import Client, TestCase
from mock import Mock
from rest_framework.test import APIRequestFactory

QPATH_TEST = '/tmp/django-test/'


class CloudRecordSummaryTest(TestCase):
    """Tests GET requests to the Cloud Sumamry Record endpoint."""

    def setUp(self):
        """Prevent logging from appearing in test output."""
        logging.disable(logging.CRITICAL)

    def test_cloud_record_summary_get_IAM_fail(self):
        """
        Test what happens if we fail to contact the IAM.

        i.e, _token_to_id returns None

        IAM = Identity and Access Management
        """
        # Mock the functionality of the IAM
        # Used in the underlying GET method
        # Simulates a failure to translate a token to an ID
        CloudRecordSummaryView._token_to_id = Mock(return_value=None)

        with self.settings(ALLOWED_FOR_GET='TestService',
                           RETURN_HEADERS=["WallDuration",
                                           "Day",
                                           "Month",
                                           "Year"]):

            test_client = Client()
            url = ''.join((reverse('CloudRecordSummaryView'),
                           '?group=TestGroup',
                           '&from=20000101',
                           '&to=20191231'))

            response = test_client.get(url,
                                       HTTP_AUTHORIZATION="Bearer TestToken")

        # Check the expected response code has been received.
        self.assertEqual(response.status_code, 401)

    def test_cloud_record_summary_get_400(self):
        """Test a GET request without the from field."""
        # Mock the functionality of the IAM
        # Simulates the translation of a token to an ID
        # Used in the underlying GET method
        CloudRecordSummaryView._token_to_id = Mock(return_value="TestService")

        with self.settings(ALLOWED_FOR_GET='TestService',
                           RETURN_HEADERS=["WallDuration",
                                           "Day",
                                           "Month",
                                           "Year"]):
            test_client = Client()
            url = ''.join((reverse('CloudRecordSummaryView'),
                           '?group=TestGroup'))

            response = test_client.get(url,
                                       HTTP_AUTHORIZATION="Bearer TestToken")

        # Check the expected response code has been received.
        self.assertEqual(response.status_code, 400)

    def test_cloud_record_summary_get_403(self):
        """Test an unauthorized GET request."""
        # Mock the functionality of the IAM
        # Simulates the translation of a token to an unauthorized ID
        # Used in the underlying GET method
        CloudRecordSummaryView._token_to_id = Mock(return_value="FakeService")

        with self.settings(ALLOWED_FOR_GET='TestService',
                           RETURN_HEADERS=["WallDuration",
                                           "Day",
                                           "Month",
                                           "Year"]):
            test_client = Client()
            url = ''.join((reverse('CloudRecordSummaryView'),
                           '?group=TestGroup',
                           '&from=20000101',
                           '&to=20191231'))

            response = test_client.get(url,
                                       HTTP_AUTHORIZATION="Bearer TestToken")

        # Check the expected response code has been received.
        self.assertEqual(response.status_code, 403)

    def test_cloud_record_summary_get_401(self):
        """Test an unauthenticated GET request."""
        test_client = Client()
        # Test without the HTTP_AUTHORIZATION header
        url = ''.join((reverse('CloudRecordSummaryView'),
                       '?group=TestGroup',
                       '&from=20000101',
                       '&to=20191231'))

        response = test_client.get(url)

        # Check the expected response code has been received.
        self.assertEqual(response.status_code, 401)

        # Test with a malformed HTTP_AUTHORIZATION header
        response = test_client.get(url,
                                   HTTP_AUTHORIZATION='TestToken')

        # Check the expected response code has been received.
        self.assertEqual(response.status_code, 401)

    def test_cloud_record_summary_get_200(self):
        """Test a successful GET request."""
        # Connect to database
        database = self._connect_to_database()
        # Clean up any lingering example data.
        self._clear_database(database)
        # Add example data
        self._populate_database(database)

        # Mock the functionality of the IAM
        CloudRecordSummaryView._token_to_id = Mock(return_value="TestService")

        with self.settings(ALLOWED_FOR_GET='TestService',
                           RETURN_HEADERS=["WallDuration",
                                           "Day",
                                           "Month",
                                           "Year"]):
            test_client = Client()
            url = ''.join((reverse('CloudRecordSummaryView'),
                           '?group=TestGroup',
                           '&from=20000101',
                           '&to=20191231'))

            response = test_client.get(url,
                                       HTTP_AUTHORIZATION="Bearer TestToken")

        expected_response = ('{'
                             '"count":2,'
                             '"next":null,'
                             '"previous":null,'
                             '"results":[{'
                             '"WallDuration":86399,'
                             '"Year":2016,'
                             '"Day":30,'
                             '"Month":7'
                             '},{'
                             '"WallDuration":43200,'
                             '"Year":2016,'
                             '"Day":31,'
                             '"Month":7}]}')

        try:
            # Check the expected response code has been received.
            self.assertEqual(response.status_code, 200)
            # Check the response received is as expected.
            self.assertEqual(response.content, expected_response)
            # Clean up after test.
        finally:
            self._clear_database(database)
            database.close()

    def test_parse_query_parameters(self):
        """Test the parsing of query parameters."""
        # test a get with group, summary, start, end and user
        test_cloud_view = CloudRecordSummaryView()
        factory = APIRequestFactory()
        url = ''.join((reverse('CloudRecordSummaryView'),
                       '?group=Group1',
                       '&service=Service1',
                       '&from=FromDate',
                       '&to=ToDate',
                       '&user=UserA'))

        request = factory.get(url)

        parsed_responses = test_cloud_view._parse_query_parameters(request)
        self.assertEqual(parsed_responses,
                         ("Group1", "Service1", "FromDate",
                          "ToDate", "UserA"))

        # test a get with just an end date
        url = ''.join((reverse('CloudRecordSummaryView'),
                       '?to=ToDate'))

        request = factory.get(url)
        parsed_responses = test_cloud_view._parse_query_parameters(request)
        self.assertEqual(parsed_responses,
                         (None, None, None,
                          "ToDate", None))

    def test_paginate_result(self):
        """Test an empty result is paginated correctly."""
        # test when no page is given.
        test_cloud_view = CloudRecordSummaryView()
        content = test_cloud_view._paginate_result(None, [])
        expected_content = {'count': 0,
                            'previous': None,
                            u'results': [],
                            'next': None}

        self.assertEqual(content, expected_content)

        # test when page number is incorrect/invalid
        factory = APIRequestFactory()

        # test when page number is not a number
        url = ''.join((reverse('CloudRecordSummaryView'),
                       '?page=a'))

        request = factory.get(url)
        content = test_cloud_view._paginate_result(request, [])
        self.assertEqual(content, expected_content)

        # test when page number is out of bounds
        url = ''.join((reverse('CloudRecordSummaryView'),
                       '?page=9999'))

        request = factory.get(url)
        content = test_cloud_view._paginate_result(request, [])
        self.assertEqual(content, expected_content)

    def test_request_to_token(self):
        """Test a token can be extracted from request."""
        test_cloud_view = CloudRecordSummaryView()
        factory = APIRequestFactory()
        url = ''.join((reverse('CloudRecordSummaryView'),
                       '?from=FromDate'))

        request = factory.get(url, HTTP_AUTHORIZATION='Bearer ThisIsAToken')

        token = test_cloud_view._request_to_token(request)
        self.assertEqual(token, 'ThisIsAToken')

    def test_request_to_token_fail(self):
        """Test the response of a tokenless request."""
        test_client = Client()

        url = ''.join((reverse('CloudRecordSummaryView'),
                       '?from=FromDate'))

        response = test_client.get(url)

        self.assertEqual(response.status_code, 401)

    def test_is_client_authorized(self):
        """Test a example client is authorised."""
        test_cloud_view = CloudRecordSummaryView()
        with self.settings(ALLOWED_FOR_GET='IAmAllowed'):
            self.assertTrue(
                test_cloud_view._is_client_authorized(
                    'IAmAllowed'))

    def test_is_client_authorized_fail(self):
        """Test the failure of un-authorised clients."""
        test_cloud_view = CloudRecordSummaryView()
        with self.settings(ALLOWED_FOR_GET='IAmAllowed'):
            self.assertFalse(
                test_cloud_view._is_client_authorized(
                    'IAmNotAllowed'))

    def test_filter_cursor(self):
        """Test the filtering of a query object based on settings."""
        test_cloud_view = CloudRecordSummaryView()

        # A list of test summaries.
        test_data = [{'Day': 30,
                      'Month': 7,
                      'Year': 2016,
                      'SiteName': 'TEST'}]

        cursor = Mock()
        # Get the mock cursor object return the test_data.
        cursor.fetchall = Mock(return_value=test_data)

        with self.settings(RETURN_HEADERS=['SiteName', 'Day']):
            result = test_cloud_view._filter_cursor(cursor)

        expected_result = [{'SiteName': 'TEST',
                            'Day': 30}]

        self.assertEqual(result, expected_result)

    def tearDown(self):
        """Delete any messages under QPATH and re-enable logging.INFO."""
        logging.disable(logging.NOTSET)

    def _populate_database(self, database):
        """Populate the database with example summaries."""
        cursor = database.cursor()

        # Insert example usage data
        cursor.execute('INSERT INTO CloudRecords '
                       '(VMUUID, SiteID, GlobalUserNameID, VOID, '
                       'VOGroupID, VORoleID, Status, StartTime, '
                       'SuspendDuration, WallDuration, PublisherDNID, '
                       'CloudType, ImageId) '
                       'VALUES '
                       '("TEST-VM", 1, 1, 1, 1, 1, "Running", '
                       '"2016-07-30 00:00:00", 0, 86399, 1, "TEST", "1");')

        # Insert example usage data
        cursor.execute('INSERT INTO CloudRecords '
                       '(VMUUID, SiteID, GlobalUserNameID, VOID, '
                       'VOGroupID, VORoleID, Status, StartTime, '
                       'SuspendDuration, WallDuration, PublisherDNID, '
                       'CloudType, ImageId) '
                       'VALUES '
                       '("TEST-VM", 1, 1, 1, 1, 1, "Running", '
                       '"2016-07-30 00:00:00", 0, 129599, 1, "TEST", "1");')

        # These INSERT statements are needed
        # because we query VCloudSummaries
        cursor.execute('INSERT INTO Sites VALUES (1, "TestSite");')
        cursor.execute('INSERT INTO VOs VALUES (1, "TestVO");')
        cursor.execute('INSERT INTO VOGroups VALUES (1, "TestGroup");')
        cursor.execute('INSERT INTO VORoles VALUES (1, "TestRole");')
        cursor.execute('INSERT INTO DNs VALUES (1, "TestDN");')

        # Summarise example usage data
        cursor.execute('CALL SummariseVMs();')
        database.commit()

    def _clear_database(self, database):
        """Clear the database of example data."""
        cursor = database.cursor()

        cursor.execute('DELETE FROM CloudRecords '
                       'WHERE VMUUID="TEST-VM";')

        cursor.execute('DELETE FROM CloudSummaries '
                       'WHERE CloudType="TEST";')

        cursor.execute('DELETE FROM Sites '
                       'WHERE id=1;')

        cursor.execute('DELETE FROM VOs '
                       'WHERE id=1;')

        cursor.execute('DELETE FROM VOGroups '
                       'WHERE id=1;')

        cursor.execute('DELETE FROM VORoles '
                       'WHERE id=1;')

        cursor.execute('DELETE FROM DNs '
                       'WHERE id=1;')

        database.commit()

    def _connect_to_database(self,
                             host='localhost',
                             user='root',
                             password='',
                             name='apel_rest'):
        """Connect to and return a cursor to the given database."""
        database = MySQLdb.connect(host, user, password, name)
        return database
