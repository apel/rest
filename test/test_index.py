from django.test import Client
import unittest

class IndexTest(unittest.TestCase):
    def test_index_get(self):
        test_client = Client()
        response = test_client.get('/index/')

        self.assertEqual(response.status_code, 200)

        expected_content = '"Hello, world. You\'re at the index."'
        self.assertEqual(response.content, expected_content)

    def test_index_post(self):
        test_client = Client()
        message = "<note><to>Tove</to><from>Jani</from></note>"
        response = test_client.post("/index/",
                                    message, 
                                    content_type="text/xml",
                                    HTTP_EMPA_ID="Test Process",
                                    SSL_CLIENT_S_DN="Test Process")

        # check the expected response code has been received
        self.assertEqual(response.status_code, 202)

        # check the message saved equals the message sent
        self.assertEqual(message, response["FILE_CONTENTS"])

        # need to clean up data written to dirq
