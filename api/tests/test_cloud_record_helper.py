"""This module tests the helper methods of the CloudRecordView class."""

import logging

from django.test import TestCase
from mock import Mock

from api.tests import PROVIDERS
from api.views.CloudRecordView import CloudRecordView


class CloudRecordHelperTest(TestCase):
    """Tests the helper methods of the CloudRecordView class."""

    def setUp(self):
        """Prevent logging from appearing in test output."""
        logging.disable(logging.CRITICAL)

    def test_signer_is_valid(self):
        """
        Test the CloudRecordView._signer_is_valid method.

        That method determines wether a POST request should be allowed or not.
        """
        # mock the external call to the CMDB to retrieve the providers
        # used in the _signer_is_valid method we are testing
        CloudRecordView._get_provider_list = Mock(return_value=PROVIDERS)
        test_cloud_view = CloudRecordView()

        # The DN corresponds to a host listed as a provider
        allowed_dn = "/C=XX/O=XX/OU=XX/L=XX/CN=allowed_host.test"

        # The Host this DN corresponds to will
        # be explicitly granted POST rights
        extra_dn = "/C=XX/O=XX/OU=XX/L=XX/CN=special_host.test"

        # The Host this DN corresponds to will
        # have its POST rights explicitly revoked
        banned_dn = "/C=XX/O=XX/OU=XX/L=XX/CN=allowed_host2.test"

        # The Host this DN corresponds is unknown to the system,
        # it should not be granted POST rights
        unknown_dn = "/C=XX/O=XX/OU=XX/L=XX/CN=mystery_host.test"

        # Grant/Revoke POST fights
        with self.settings(ALLOWED_TO_POST=[extra_dn],
                           BANNED_FROM_POST=[banned_dn]):

            # DNs corresponding to hosts listed as a provider should be valid
            # i.e have POST rights
            self.assertTrue(test_cloud_view._signer_is_valid(allowed_dn))

            # DNs corresponding to hosts with explicit access should be valid
            # i.e have POST rights
            self.assertTrue(test_cloud_view._signer_is_valid(extra_dn))

            # DNs corresponding to banned hosts should be invalid
            # i.e not have POST rights
            self.assertFalse(test_cloud_view._signer_is_valid(banned_dn))

            # DNs corresponding to unknonw hosts should be invalid
            # i.e not have POST rights
            self.assertFalse(test_cloud_view._signer_is_valid(unknown_dn))

        # mock the external call to the CMDB to retrieve the providers
        # used in the _signer_is_valid method we are testing
        # now we are mocking a failure of the CMDB to respond as expected
        CloudRecordView._get_provider_list = Mock(return_value={})
        # in which case we should reject all POST requests
        self.assertFalse(test_cloud_view._signer_is_valid(allowed_dn))
