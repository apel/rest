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
        response = test_client.post("/index/",
                                    "<note><to>Tove</to><from>Jani</from></note>", 
                                    content_type="text/xml",
                                    HTTP_EMPA_ID="Test Process",
                                    SSL_CLIENT_S_DN="Test Process")

        self.assertEqual(response.status_code, 202)

        # need to clean up data written to dirq
