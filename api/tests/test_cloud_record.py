"""
This module tests GET and POST requests.
to the Cloud Sumamry Record endpoint.
"""

import glob
import logging
import os
import shutil

from django.test import Client, TestCase
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

QPATH_TEST = '/tmp/django-test/'


class CloudRecordTest(TestCase):
    """
    Tests POST requests to the Cloud Record endpoint.
    """
    def setUp(self):
        """Disable logging.INFO from appearing in test output."""
        logging.disable(logging.INFO)

    def test_cloud_record_post(self):
        """
        Test a POST call for content equality and a 202 return code,
        with a test cloud message.
        """
        with self.settings(QPATH=QPATH_TEST):
            test_client = Client()
            response = test_client.post(
                                    "/api/v1/cloud/record",
                                    MESSAGE,
                                    content_type="text/plain",
                                    HTTP_EMPA_ID="Test Process",
                                    SSL_CLIENT_S_DN="cloud.recas.ba.infn.it")

            # check the expected response code has been received
            self.assertEqual(response.status_code, 202)

            # get save messages under QPATH_TEST
            messages = self._saved_messages('%s*/*/*/body' % QPATH_TEST)

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
            self._delete_messages(QPATH_TEST)

    # def test_filter_cursor(self):
        # pass

    def tearDown(self):
        """Delete any messages under QPATH and re-enable logging.INFO."""
        logging.disable(logging.NOTSET)

    def _delete_messages(self, message_path):
        """Delete any messages under message_path."""
        if os.path.exists(message_path):
            shutil.rmtree(message_path)

    def _saved_messages(self, message_path):
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
