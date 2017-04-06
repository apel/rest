"""This module tests POST requests to the Cloud Record endpoint."""

import glob
import logging
import os
import shutil

from django.core.urlresolvers import reverse
from django.test import Client, TestCase
from mock import Mock
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from api.views.CloudRecordView import CloudRecordView

QPATH_TEST = '/tmp/django-test/'


class CloudRecordTest(TestCase):
    """Tests POST requests to the Cloud Record endpoint."""

    def setUp(self):
        """Prevent logging from appearing in test output."""
        logging.disable(logging.CRITICAL)

    def test_cloud_record_post_provider_banned(self):
        """Test that a banned provider on the provider list cannot POST."""
        example_dn = "/C=XX/O=XX/OU=XX/L=XX/CN=allowed_host.test"
        with self.settings(BANNED_FROM_POST=[example_dn]):

            # Mock the functionality of the provider list
            # Used in the underlying POST handling method
            CloudRecordView._get_provider_list = Mock(return_value=PROVIDERS)

            test_client = Client()
            response = test_client.post(reverse('CloudRecordView'),
                                        MESSAGE,
                                        content_type="text/plain",
                                        HTTP_EMPA_ID="Test Process",
                                        SSL_CLIENT_S_DN=example_dn)

            self.assertEqual(response.status_code, 403)

    def test_cloud_record_post_provider_special(self):
        """
        Test that a provider granted POST rights can, indeed, POST.

        Even if they aren't on the provider list.
        This test DOES NOT check that the saved message is correct.
        For that, see test_cloud_record_post_202()
        """
        example_dn = "/C=XX/O=XX/OU=XX/L=XX/CN=special_host.test"
        with self.settings(ALLOWED_TO_POST=[example_dn],
                           QPATH=QPATH_TEST):

            # Mock the functionality of the provider list
            # Used in the underlying POST handling method
            CloudRecordView._get_provider_list = Mock(return_value=PROVIDERS)

            test_client = Client()
            response = test_client.post(reverse('CloudRecordView'),
                                        MESSAGE,
                                        content_type="text/plain",
                                        HTTP_EMPA_ID="Test Process",
                                        SSL_CLIENT_S_DN=example_dn)

            self.assertEqual(response.status_code, 202)

    def test_cloud_record_post_provider_fail(self):
        """Test what happens if we fail to retrieve the providers."""
        # Mock the functionality of the provider list
        # Used in the underlying POST handling method
        # Shouldn't allow any POSTs,
        # i.e. we have failed to retrieve the providers list
        CloudRecordView._get_provider_list = Mock(return_value={})

        test_client = Client()
        example_dn = "/C=XX/O=XX/OU=XX/L=XX/CN=allowed_host.test"
        response = test_client.post(reverse('CloudRecordView'),
                                    MESSAGE,
                                    content_type="text/plain",
                                    HTTP_EMPA_ID="Test Process",
                                    SSL_CLIENT_S_DN=example_dn)

        self.assertEqual(response.status_code, 403)

    def test_cloud_record_post_403(self):
        """Test unknown provider POST request returns a 403 code."""
        # Mock the functionality of the provider list
        # Used in the underlying POST handling method
        # Allows only allowed_host.test to POST
        CloudRecordView._get_provider_list = Mock(return_value=PROVIDERS)

        test_client = Client()
        example_dn = "/C=XX/O=XX/OU=XX/L=XX/CN=prohibited_host.test"
        url = reverse('CloudRecordView')

        response = test_client.post(url,
                                    MESSAGE,
                                    content_type="text/plain",
                                    HTTP_EMPA_ID="Test Process",
                                    SSL_CLIENT_S_DN=example_dn)

        # check the expected response code has been received
        self.assertEqual(response.status_code, 403)

    def test_cloud_record_post_401(self):
        """Test certificate-less POST request returns a 401 code."""
        test_client = Client()
        # No SSL_CLIENT_S_DN in POST to
        # simulate a certificate-less request
        url = reverse('CloudRecordView')

        response = test_client.post(url,
                                    MESSAGE,
                                    content_type="text/plain",
                                    HTTP_EMPA_ID="Test Process")

        # check the expected response code has been received
        self.assertEqual(response.status_code, 401)

    def test_cloud_record_post_202(self):
        """Test POST request for content equality and a 202 return code."""
        # Mock the functionality of the provider list,
        # used in the underlying POST handling method so that the
        # POST request is authorized, as allowed_host.test (the
        # default dn of _check_record_post) is listed in PROVIDERS
        CloudRecordView._get_provider_list = Mock(return_value=PROVIDERS)
        # Make (and check) the POST request
        self._check_record_post(MESSAGE, 202)

    def tearDown(self):
        """Delete any messages under QPATH and re-enable logging.INFO."""
        self._delete_messages(QPATH_TEST)
        logging.disable(logging.NOTSET)

    def _delete_messages(self, message_path):
        """Delete any messages under message_path."""
        if os.path.exists(message_path):
            shutil.rmtree(message_path)

    def _saved_messages(self, message_path):
        """Return a list of messages under message_path."""
        return glob.glob(message_path)

    def _check_record_post(self, message, expected_status,
                          dn='/C=XX/O=XX/OU=XX/L=XX/CN=allowed_host.test',
                          empaid='Test Process'):
        """
        Helper method to make a POST request.

        This method makes a POST request that is authenticated by
        the supplied dn and identified (in the queue logs) by empaid.
        It checks the message as receieved is the same as
        the message saved.

        By default,
         - dn is /C=XX/O=XX/OU=XX/L=XX/CN=allowed_host.test
         - empaid is 'Test Process'

        These defaults are set so that the majority of tests can use this
        method with minimal parameters in the method call, but that edge
        cases can still be tested using this method.

        i.e. a successful POST need only call
          self._check_record_post(MESSAGE, 202)
        """
        # This avoids the test writing to the QPATH
        # set in apel_rest/settings.py 
        with self.settings(QPATH=QPATH_TEST):

            # Make the POST request
            test_client = Client()
            url = reverse('CloudRecordView')

            if dn is not None:
                # Include the in dn SSL_CLIENT_S_DN so the
                # request is able to be authenticated
                response = test_client.post(url,
                                            message,
                                            content_type="text/plain",
                                            HTTP_EMPA_ID=empaid,
                                            SSL_CLIENT_S_DN=dn)
            else:
                # Omit the SSL_CLIENT_S_DN header so the request is
                # made without any certificate (and not authenticated)
                response = test_client.post(url,
                                            message,
                                            content_type="text/plain",
                                            HTTP_EMPA_ID=empaid)

            # check the expected response code has been received
            self.assertEqual(response.status_code, expected_status)

            # If the message was expected to be successfull, check for
            # equality between the sent message and the saved message
            if expected_status == 202:
                # get saved messages under QPATH_TEST
                messages = self._saved_messages('%s*/*/*/body' % QPATH_TEST)

                # check one and only one message body saved
                self.assertEqual(len(messages), 1)

                # get message content
                # can unpack sequence because we have asserted length 1
                [message_path] = messages
                with file(message_path) as message_file:
                    message_content = message_file.read()

                # check saved message content
                self.assertEqual(message, message_content)

PROVIDERS = {'total_rows': 735,
             'offset': 695,
             'rows': [
                 {'id': '1',
                  'key': ['service'],
                  'value':{
                      'sitename': 'TEST2',
                      'provider_id': 'TEST2',
                      'type': 'cloud'}},
                 {'id': '2',
                  'key': ['service'],
                  'value':{
                      'sitename': 'TEST',
                      'provider_id': 'TEST',
                      'hostname': 'allowed_host.test',
                      'type': 'cloud'}}]}

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
