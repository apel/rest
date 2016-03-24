import glob
import logging
import os
import shutil
import unittest

from django.test import Client, TestCase

QPATH_TEST = '/tmp/django-test/'


class IndexTest(TestCase):
    def setUp(self):
        logger = logging.getLogger(__name__)
        logging.disable(logging.INFO)

    def test_index_get(self):
        test_client = Client()
        response = test_client.get('/index/')

        self.assertEqual(response.status_code, 200)

        expected_content = '"Hello, world. You\'re at the index."'
        self.assertEqual(response.content, expected_content)

    def test_index_post(self):
        with self.settings(QPATH=QPATH_TEST):
            test_client = Client()
            response = test_client.post("/index/",
                                        MESSAGE,
                                        content_type="text/xml",
                                        HTTP_EMPA_ID="Test Process",
                                        SSL_CLIENT_S_DN="Test Process")

            # check the expected response code has been received
            self.assertEqual(response.status_code, 202)

            # check one and only one message body saved
            self.assertEqual(self.saved_message_count(), 1)

    def tearDown(self):
        INCOMING_PATH = '%sincoming' % QPATH_TEST
        self.delete_messages(INCOMING_PATH)
        logging.disable(logging.NOTSET)

    def delete_messages(self, message_path):
        if os.path.exists(message_path):
            shutil.rmtree(message_path)

    def saved_messages(self):
        return glob.glob('%s*/*/*/body' % QPATH_TEST)

    def saved_message_count(self):
        return len(self.saved_messages())

MESSAGE = """APEL-individual-job-message: v0.2
Site: RAL-LCG2
SubmitHost: ce01.ncg.ingrid.pt:2119/jobmanager-lcgsge-atlasgrid
LocalJobId: 31564872
LocalUserId: atlasprd019
GlobalUserName: /C=whatever/D=someDN
FQAN: /voname/Role=NULL/Capability=NULL
WallDuration: 234256
CpuDuration: 2345
Processors: 2
NodeCount: 2
StartTime: 1234567890
EndTime: 1234567899
MemoryReal: 1000
MemoryVirtual: 2000
ServiceLevelType: Si2k
ServiceLevel: 1000
%%
Site: RAL-LCG2
SubmitHost: ce01.ncg.ingrid.pt:2119/jobmanager-lcgsge-atlasgrid
LocalJobId: 31564873
LocalUserId: atlasprd018
GlobalUserName: /C=whatever/D=someDN
FQAN: /voname/Role=NULL/Capability=NULL
WallDuration: 234257
CpuDuration: 2347
Processors: 3
NodeCount: 3
StartTime: 1234567891
EndTime: 1234567898
MemoryReal: 1000
MemoryVirtual: 2000
ServiceLevelType: Si2k
ServiceLevel: 1000
%%"""
