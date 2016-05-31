"""
This module tests GET and POST requests.
to the Cloud Sumamry Record endpoint.
"""

import glob
import logging
import os
import shutil

from api.views.CloudRecordSummaryView import CloudRecordSummaryView
from django.test import Client, TestCase
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

QPATH_TEST = '/tmp/django-test/'


class CloudRecordSummaryTest(TestCase):
    """
    Tests GET and POST requests to the Cloud Sumamry Record endpoint.
    """
    def setUp(self):
        """Disable logging.INFO from appearing in test output."""
        logging.disable(logging.INFO)

    def test_cloud_summary_get_fail(self):
        """
        Test if a GET call on Clud Summaries returns 501
        if querying with no FROM parameter
        """
        test_client = Client()
        response = test_client.get('/api/v1/cloud/summaryrecord')

        # without a from parameter, the request will fail
        self.assertEqual(response.status_code, 501)

    def test_cloud_summary_get(self):
        """Test a GET call returning empty data."""
        test_client = Client()
        response = test_client.get('/api/v1/cloud/summaryrecord?from=2000/01/01')

        self.assertEqual(response.status_code, 200)

        expected_content = '{"count":0,"next":null,"previous":null,"results":[]}'
        self.assertEqual(response.content, expected_content)

    def test_cloud_summary_post(self):
        """
        Test a POST call for content equality and a 202 return code,
        with a test cloud message.
        """
        with self.settings(QPATH=QPATH_TEST):
            test_client = Client()
            response = test_client.post("/api/v1/cloud/summaryrecord",
                                        MESSAGE,
                                        content_type="text/plain",
                                        HTTP_EMPA_ID="Test Process",
                                        SSL_CLIENT_S_DN="Test Process")

            # check the expected response code has been received
            self.assertEqual(response.status_code, 202)

            # get save messages under QPATH_TEST
            messages = self.saved_messages('%s*/*/*/body' % QPATH_TEST)

            # check one and only one message body saved
            self.assertEqual(len(messages), 1)

            # get message content
            # can unpack sequence because we have asserted length 1
            [message] = messages
            message_file = open(message)
            message_content = message_file.read()
            message_file.close()

            # check saved message content
            self.assertEqual(MESSAGE, message_content)
            self.delete_messages(QPATH_TEST)

    def test_paginate_result(self):
        """Test an empty result is paginated correctly."""
        test_cloud_view = CloudRecordSummaryView()
        content = test_cloud_view._paginate_result(None, [])
        expected_content = {'count': 0,
                            'previous': None,
                            u'results': [],
                            'next': None}

        self.assertEqual(content, expected_content)

    def test_parse_query_parameters(self):
        test_cloud_view = CloudRecordSummaryView()
        factory = APIRequestFactory()
        request = factory.post('/api/v1/cloud/summaryrecord?group=Group1&service=Service1&from=FromDate&to=ToDate', {})

        parsed_responses = test_cloud_view._parse_query_parameters(request)
        self.assertEqual(parsed_responses,
                         ("Group1", "Service1", "FromDate", "ToDate"))



    def test_filter_cursor(self):
        pass

    def tearDown(self):
        """Delete any messages under QPATH and re-enable logging.INFO."""
        logging.disable(logging.NOTSET)

    def delete_messages(self, message_path):
        """Delete any messages under message_path."""
        if os.path.exists(message_path):
            shutil.rmtree(message_path)

    def saved_messages(self, message_path):
        """
        Return a list of file locations,
        corresponding to messages under message_path.
        """
        return glob.glob(message_path)

MESSAGE = """APEL-cloud-message: v0.2
VMUUID: TestVM1 2013-02-25 17:37:27+00:00
SiteName: CESGA
MachineName: one-2421
LocalUserId: 19
LocalGroupId: 101
GlobalUserName: NULL
FQAN: NULL
Status: completed
StartTime: 1361813847
EndTime: 1361813870
SuspendDuration: NULL
WallDuration: NULL
CpuDuration: NULL
CpuCount: 1
NetworkType: NULL
NetworkInbound: 0
NetworkOutbound: 0
Memory: 1000
Disk: NULL
StorageRecordId: NULL
ImageId: NULL
CloudType: OpenNebula
%%
VMUUID: TestVM1 2015-06-25 17:37:27+00:00
SiteName: CESGA
MachineName: one-2422
LocalUserId: 13
LocalGroupId: 131
GlobalUserName: NULL
FQAN: NULL
Status: completed
StartTime: 1361413847
EndTime: 1361811870
SuspendDuration: NULL
WallDuration: NULL
CpuDuration: NULL
CpuCount: 1
NetworkType: NULL
NetworkInbound: 0
NetworkOutbound: 0
Memory: 1000
Disk: NULL
StorageRecordId: NULL
ImageId: NULL
CloudType: OpenNebula
%%"""
