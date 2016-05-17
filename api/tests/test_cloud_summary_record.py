import glob
import logging
# import MySQLdb
import os
from subprocess import call
import shutil

from django.test import Client, TestCase

# from apel.db.loader import Loader, LoaderException

QPATH_TEST = '/tmp/django-test/'


class IndexTest(TestCase):
    def setUp(self):
        logging.disable(logging.INFO)

    def test_cloud_summary_get_fail(self):
        test_client = Client()
        response = test_client.get('/api/v1/cloud/summaryrecord')

        # without a from parameter, the request will fail
        self.assertEqual(response.status_code, 501)

    def test_cloud_summary_get(self):
        test_client = Client()
        response = test_client.get('/api/v1/cloud/summaryrecord?from=2000/01/01')

        self.assertEqual(response.status_code, 200)

        expected_content = '{"count":0,"next":null,"previous":null,"results":[]}'
        self.assertEqual(response.content, expected_content)

    def test_cloud_summary_post(self):
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

    def tearDown(self):
        self.delete_messages(QPATH_TEST)
        logging.disable(logging.NOTSET)

    def delete_messages(self, message_path):
        if os.path.exists(message_path):
            shutil.rmtree(message_path)

    def saved_messages(self, message_path):
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
