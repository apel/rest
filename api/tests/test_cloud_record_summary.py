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
        response = test_client.get('/accounting-server/api/v1/cloud/record/summary')

        # without a from parameter, the request will fail
        self.assertEqual(response.status_code, 501)

    def test_cloud_summary_get(self):
        """Test a GET call returning empty data."""
        test_client = Client()
        response = test_client.get('/accounting-server/api/v1/cloud/record/summary?from=2000/01/01')

        self.assertEqual(response.status_code, 200)

        expected_content = '{"count":0,"next":null,"previous":null,"results":[]}'
        self.assertEqual(response.content, expected_content)

    def test_parse_query_parameters(self):
        test_cloud_view = CloudRecordSummaryView()
        factory = APIRequestFactory()
        request = factory.post('/accounting-server/api/v1/cloud/record/summary?group=Group1&service=Service1&from=FromDate&to=ToDate', {})

        parsed_responses = test_cloud_view._parse_query_parameters(request)
        self.assertEqual(parsed_responses,
                         ("Group1", "Service1", "FromDate", "ToDate"))

    def test_filter_cursor(self):
        pass

    def tearDown(self):
        """Delete any messages under QPATH and re-enable logging.INFO."""
        logging.disable(logging.NOTSET)
