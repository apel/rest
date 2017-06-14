"""This module tests GET requests to the Cloud Sumamry Record endpoint."""

import logging
import MySQLdb

from api.views.CloudRecordSummaryView import CloudRecordSummaryView
from django.core.urlresolvers import reverse
from django.test import Client, TestCase
from mock import Mock

QPATH_TEST = '/tmp/django-test/'


class CloudRecordSummaryGetTest(TestCase):
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
                       'CloudType, ImageId, '
                       'CloudComputeServiceID) '
                       'VALUES '
                       '("TEST-VM", 1, 1, 1, 1, 1, "Running", '
                       '"2016-07-30 00:00:00", 0, 86399, 1, "TEST", "1", '
                       '1);')

        # Insert example usage data
        cursor.execute('INSERT INTO CloudRecords '
                       '(VMUUID, SiteID, GlobalUserNameID, VOID, '
                       'VOGroupID, VORoleID, Status, StartTime, '
                       'SuspendDuration, WallDuration, PublisherDNID, '
                       'CloudType, ImageId, '
                       'CloudComputeServiceID) '
                       'VALUES '
                       '("TEST-VM", 1, 1, 1, 1, 1, "Running", '
                       '"2016-07-30 00:00:00", 0, 129599, 1, "TEST", "1", '
                       '1);')

        # These INSERT statements are needed
        # because we query VCloudSummaries
        cursor.execute('INSERT INTO Sites VALUES (1, "TestSite");')
        cursor.execute('INSERT INTO VOs VALUES (1, "TestVO");')
        cursor.execute('INSERT INTO VOGroups VALUES (1, "TestGroup");')
        cursor.execute('INSERT INTO VORoles VALUES (1, "TestRole");')
        cursor.execute('INSERT INTO DNs VALUES (1, "TestDN");')
        cursor.execute('INSERT INTO CloudComputeServices '
                       'VALUES (1, "TestService");')

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

        cursor.execute('DELETE FROM CloudComputeServices '
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
