"""This module tests the helper methods of the CloudRecordView class."""

import logging

from api.views.CloudRecordSummaryView import CloudRecordSummaryView
from django.core.urlresolvers import reverse
from django.test import TestCase
from mock import Mock
from rest_framework.test import APIRequestFactory

QPATH_TEST = '/tmp/django-test/'


class CloudRecordSummaryHelperTest(TestCase):
    """
    Tests the helper methods of the CloudRecordSummaryView class.

    Some of these do make GET Request objects, as the helper methods
    expect take the whole request as input, they do not call
    CloudRecordSummaryView.get() however.
    """

    def setUp(self):
        """Prevent logging from appearing in test output."""
        logging.disable(logging.CRITICAL)

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

        # Test we can extract the token from a
        # normaly structured Authorization header
        request = factory.get(url, HTTP_AUTHORIZATION='Bearer ThisIsAToken')
        token = test_cloud_view._request_to_token(request)
        self.assertEqual(token, 'ThisIsAToken')

        # Test we return None when failing to extract the token
        # from a malformed Authorization header
        request = factory.get(url, HTTP_AUTHORIZATION='ThisIsAToken')
        token = test_cloud_view._request_to_token(request)
        self.assertEqual(token, None)

        # Test we return None when no token provided
        request = factory.get(url)
        token = test_cloud_view._request_to_token(request)
        self.assertEqual(token, None)

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
