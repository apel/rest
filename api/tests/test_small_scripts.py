"""This module tests the small scripts - admin, model, and wsgi."""

import unittest


class SmallScriptsTest(unittest.TestCase):
    def test_admin(self):
        import api.admin

    def test_models(self):
        import api.models

    def test_wsgi(self):
        import apel_rest.wsgi
