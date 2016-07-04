"""
This module tests GET and POST requests.
to the Cloud Sumamry Record endpoint.
"""

import logging

from api.views.CloudRecordSummaryView import CloudRecordSummaryView
from django.test import TestCase
from rest_framework.test import APIRequestFactory

QPATH_TEST = '/tmp/django-test/'


class CloudRecordSummaryTest(TestCase):
    """Tests GET requests to the Cloud Sumamry Record endpoint."""

    def setUp(self):
        """Disable logging.INFO from appearing in test output."""
        logging.disable(logging.INFO)

    def test_parse_query_parameters(self):
        """Test the parsing of query parameters."""
        # test a get with group, summary, start and end
        test_cloud_view = CloudRecordSummaryView()
        factory = APIRequestFactory()
        request = factory.get('/api/v1/cloud/record/summary?group=Group1&service=Service1&from=FromDate&to=ToDate', {})
        parsed_responses = test_cloud_view._parse_query_parameters(request)
        self.assertEqual(parsed_responses,
                         ("Group1", "Service1", "FromDate", "ToDate"))

        # test a get with just an end date
        request = factory.get('/api/v1/cloud/record/summary?to=ToDate', {})
        parsed_responses = test_cloud_view._parse_query_parameters(request)
        self.assertEqual(parsed_responses,
                         (None, None, None, "ToDate"))

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
        request = factory.get('/api/v1/cloud/record/summary?page=a')
        content = test_cloud_view._paginate_result(request, [])
        self.assertEqual(content, expected_content)

        # test when page number is out of bounds
        request = factory.get('/api/v1/cloud/record/summary?page=9999')
        content = test_cloud_view._paginate_result(request, [])
        self.assertEqual(content, expected_content)

    def test_request_to_token(self):
        """Test a token can be extracted from request."""
        test_cloud_view = CloudRecordSummaryView()
        factory = APIRequestFactory()
        request = factory.get('/api/v1/cloud/record/summary?from=FromDate',
                              HTTP_AUTHORIZATION='Bearer ThisIsAToken')

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
        with self.settings(ALLOWED_FOR_GET='IAmAllowed'):
            self.assertTrue(test_cloud_view._is_client_authorized('IAmAllowed'))

    def test_is_client_authorized_fail(self):
        """Test the failure of un-authorised clients."""
        test_cloud_view = CloudRecordSummaryView()
        with self.settings(ALLOWED_FOR_GET='IAmAllowed'):
            self.assertFalse(test_cloud_view._is_client_authorized('IAmNotAllowed'))

    # def test_filter_cursor(self):
    #    pass

    def tearDown(self):
        """Delete any messages under QPATH and re-enable logging.INFO."""
        logging.disable(logging.NOTSET)
