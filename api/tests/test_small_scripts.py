"""This module tests the small scripts - admin, model, and wsgi."""

# Using unittest and not django.test as no need for overhead of database
import unittest


class SmallScriptsTest(unittest.TestCase):
    def test_admin(self):
        """Check that admin is importable."""
        import api.admin

    def test_models(self):
        """Check that models is importable."""
        import api.models

    def test_wsgi(self):
        """Check that wsgi is importable."""
        import apel_rest.wsgi
