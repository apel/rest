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
    Tests GET requests to the Cloud Sumamry Record endpoint.
    """
    def setUp(self):
        """Disable logging.INFO from appearing in test output."""
        logging.disable(logging.INFO)

    def test_parse_query_parameters(self):
        test_cloud_view = CloudRecordSummaryView() 
        factory = APIRequestFactory()
        request = factory.get('/api/v1/cloud/record/summary?group=Group1&service=Service1&from=FromDate&to=ToDate', {})

        parsed_responses = test_cloud_view._parse_query_parameters(request)
        self.assertEqual(parsed_responses,
                         ("Group1", "Service1", "FromDate", "ToDate"))

    def test_paginate_result(self):
        """Test an empty result is paginated correctly."""
        test_cloud_view = CloudRecordSummaryView()
        content = test_cloud_view._paginate_result(None, [])
        expected_content = {'count': 0,
                            'previous': None,
                            u'results': [],
                            'next': None}

        self.assertEqual(content, expected_content)

    def test_request_to_token(self):
        """Test a token can be extracted from request"""
        test_cloud_view = CloudRecordSummaryView()
        factory = APIRequestFactory()
        request = factory.get('/api/v1/cloud/record/summary?from=FromDate', 
                              HTTP_AUTHORIZATION = 'Bearer ThisIsAToken')

        token = test_cloud_view._request_to_token(request)
        self.assertEqual(token, 'ThisIsAToken')

    def test_request_to_token_fail(self):
        """Test the response of a tokenless request."""
        test_cloud_view = CloudRecordSummaryView()
        factory = APIRequestFactory()
        request = factory.get('/api/v1/cloud/record/summary?from=FromDate')

        self.assertRaises(KeyError, test_cloud_view._request_to_token, request)


    def test_is_client_authorized(self):
        """Test a example client is authorised."""
        test_cloud_view = CloudRecordSummaryView()
        factory = APIRequestFactory()
        with self.settings(ALLOWED_FOR_GET='IAmAllowed'):
            self.assertTrue(test_cloud_view._is_client_authorized('IAmAllowed'))

    def test_is_client_authorized_fail(self):
        """Test the failure of un-authorised clients."""
        test_cloud_view = CloudRecordSummaryView()
        factory = APIRequestFactory()
        with self.settings(ALLOWED_FOR_GET='IAmAllowed'):
            self.assertFalse(test_cloud_view._is_client_authorized('IAmNotAllowed'))


    #def test_filter_cursor(self):
    #    pass

    def tearDown(self):
        """Delete any messages under QPATH and re-enable logging.INFO."""
        logging.disable(logging.NOTSET)
