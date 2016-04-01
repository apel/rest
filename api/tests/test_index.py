import glob
import logging
import MySQLdb
import os
from subprocess import call
import shutil

from django.test import Client, TestCase

from apel.db.loader import Loader, LoaderException

QPATH_TEST = '/tmp/django-test/'


class IndexTest(TestCase):
    def setUp(self):
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

            # attempt to load messages
            database = MySQLdb.connect('localhost', 'root', '')
            cursor = database.cursor()

            # create test database
            cursor.execute('create database apelserver_test')

            # upload schemea
            # can't do this with a cursor object
            # as server.sql contains multiple commands

            status = call(['/usr/bin/mysql',
                           '-u',
                           'root',
                           '-e',
                           'use apelserver_test; source schemas/server.sql;'])

            # call doesnt pass up the exception, so have to do it like this
            if status is not 0:
                # if something went wrong,
                # try and drop database
                # so test can be re run
                cursor.execute('drop database apelserver_test')
                raise MySQLdb.Error

            try:
                # load messages into database
                loader = Loader(QPATH_TEST,
                                True,  # backend
                                'mysql',  # save messages
                                'localhost',  # hostname
                                3306,  # port
                                'apelserver_test',  # name
                                'root',  # username
                                '',  # password
                                '/var/run/apel/loader.pid')  # pidfile

                loader.startup()
                loader.load_all_msgs()
                loader.shutdown()

                cursor.execute('use apelserver_test')
                cursor.execute('select count(*) from JobRecords')
                row_count = cursor.fetchone()
            # don't want to catch exceptions
            # just want to ensure db dropped
            finally:
                cursor.execute('drop database apelserver_test')

            # check database had exactly 2 rows
            self.assertEqual((2L,), row_count)

            # check exactly 1 accepted messages
            messages = self.saved_messages('%saccept/*/*/body' % QPATH_TEST)
            self.assertEqual(len(messages), 1)

    def tearDown(self):
        self.delete_messages(QPATH_TEST)
        logging.disable(logging.NOTSET)

    def delete_messages(self, message_path):
        if os.path.exists(message_path):
            shutil.rmtree(message_path)

    def saved_messages(self, message_path):
        return glob.glob(message_path)

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
