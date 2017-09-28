"""This module tests the JSON Web Token validation."""

import logging
import time

from jose import jwt
from django.test import TestCase
from mock import patch

from api.utils.TokenChecker import TokenChecker


class TokenCheckerTest(TestCase):
    """Tests the JSON Web Token validation."""

    def setUp(self):
        """Create a new TokenChecker and disable logging."""
        self._token_checker = TokenChecker()
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        """Re-enable logging."""
        logging.disable(logging.NOTSET)

    @patch.object(TokenChecker, '_get_issuer_public_key')
    @patch.object(TokenChecker, '_check_token_not_revoked')
    def test_token_cache(self, mock_check_token_not_revoked,
                         mock_get_issuer_public_key):
        """
        Check a cached token is granted access.

        Method does this by checking a token is valid twice, the first time
        the token is validated and stored in a cache, the second time access
        should be granted because the token is in the cache, not because the
        token is valid.
        """
        # Mock the external call to retrieve the IAM public key
        # used in the _verify_token and valid_token_to_id call
        mock_get_issuer_public_key.return_value = PUBLIC_KEY
        # Mock the external call to check the token has not been rejected
        # used in the valid_token_to_id call
        mock_check_token_not_revoked.return_value = CLIENT_ID

        payload_list = []

        # This payload will be valid as we will sign it with PRIVATE_KEY
        payload = self._standard_token()

        # Add the same token twice, this is what tests the cache functionality
        payload_list = [payload, payload]

        for payload in payload_list:
            token = self._create_token(payload, PRIVATE_KEY)
            with self.settings(IAM_HOSTNAME_LIST=['iam-test.idc.eu']):
                self.assertEqual(
                    self._token_checker.valid_token_to_id(token), CLIENT_ID,
                    "Token with payload %s should not be accepted!" % payload
                )

    @patch.object(TokenChecker, '_get_issuer_public_key')
    @patch.object(TokenChecker, '_check_token_not_revoked')
    def test_token_cache_mis_match(self, mock_check_token_not_revoked,
                                   mock_get_issuer_public_key):
        """
        Check tokens with the same subject are handled correctly.

        Having a token cached for the subject should not be sufficent to grant
        access, the tokens must match.
        """
        # Mock the external call to retrieve the IAM public key
        # used in the _verify_token and valid_token_to_id call
        mock_get_issuer_public_key.return_value = PUBLIC_KEY
        # Mock the external call to check the token has not been rejected
        # used in the valid_token_to_id call
        mock_check_token_not_revoked.return_value = CLIENT_ID

        # This payload will be valid as we will sign it with PRIVATE_KEY
        payload1 = self._standard_token()

        # This payload has a subject that will be in the cache, but this
        # new token is not. We need to ensure this invalid token does not
        # get granted rights based only on it's subject being in the cache
        payload2 = {
            'iss': 'https://iam-test.idc.eu/',
            'jti': '098cb343-c45e-490d-8aa0-ce1873cdc5f8',
            'iat': int(time.time()) - 2000000,
            'sub': CLIENT_ID,
            'exp': int(time.time()) - 200
        }

        token1 = self._create_token(payload1, PRIVATE_KEY)
        token2 = self._create_token(payload2, PRIVATE_KEY)

        with self.settings(IAM_HOSTNAME_LIST=['iam-test.idc.eu']):
            self.assertEqual(
                self._token_checker.valid_token_to_id(token1), CLIENT_ID,
                "Token with payload %s should not be accepted!" % payload1
            )

            self.assertEqual(
                self._token_checker.valid_token_to_id(token2), None,
                "Token with payload %s should not be accepted!" % payload2
            )

    @patch.object(TokenChecker, '_get_issuer_public_key')
    @patch.object(TokenChecker, '_check_token_not_revoked')
    def test_valid_token(self, mock_check_token_not_revoked,
                         mock_get_issuer_public_key):
        """Check a valid and properly signed token is accepted."""
        # Mock the external call to retrieve the IAM public key
        # used in the _verify_token and valid_token_to_id call
        mock_get_issuer_public_key.return_value = PUBLIC_KEY
        # Mock the external call to check the token has not been rejected
        # used in the valid_token_to_id call
        mock_check_token_not_revoked.return_value = CLIENT_ID

        # This payload will be valid as we will sign it with PRIVATE_KEY
        payload = self._standard_token()

        token = self._create_token(payload, PRIVATE_KEY)

        with self.settings(IAM_HOSTNAME_LIST=['iam-test.idc.eu']):
            client_id = payload['sub']
            self.assertEqual(
                self._token_checker.valid_token_to_id(token), client_id,
                "Token with payload %s should be accepted!" % payload
            )

    @patch.object(TokenChecker, '_get_issuer_public_key')
    def test_verify_token(self, mock_get_issuer_public_key):
        """
        Check a mis-signed/'forged' token is detected.

        Both by:
         - _verify_token
         - valid_token_to_id

        The first method checks wether the key is properly signed
        The second method detemines wether the token is invalid
        """
        # Mock the external call to retrieve the IAM public key
        # used in the _verify_token and valid_token_to_id call
        mock_get_issuer_public_key.return_value = PUBLIC_KEY

        payload_list = []

        # This payload would be valid if properly signed, but we are going to
        # sign it with FORGED_PRIVATE_KEY which will not match the PUBLIC_KEY
        payload_list.append(self._standard_token())

        for payload in payload_list:
            token = self._create_token(payload, FORGED_PRIVATE_KEY)
            with self.settings(IAM_HOSTNAME_LIST=['iam-test.idc.eu']):
                self.assertFalse(
                    self._token_checker._verify_token(token, payload['iss']),
                    "Payload %s should not be accepted!" % payload
                )

                self.assertEqual(
                    self._token_checker.valid_token_to_id(token), None,
                    "Token with payload %s should not be accepted!" % payload
                )

    def test_is_token_issuer_trusted(self):
        """
        Check an untrusted 'issuer' (or missing 'issuer') is detected.

        Both by:
         - _is_token_issuer_trusted
         - valid_token_to_id

        The first method checks wether the issuer is
        in settings.IAM_HOSTNAME_LIST
        The second method detemines wether the token is invalid
        """
        payload_list = []

        # Test we reject a payload without 'iss' field
        # as we cannot tell where it came from (so can't verify it)
        payload_list.append({
            'jti': '098cb343-c45e-490d-8aa0-ce1873cdc5f8',
            'iat': int(time.time()) - 2000000,
            'sub': CLIENT_ID,
            'exp': int(time.time()) + 200000
        })

        # Test we reject a payload with a malicious 'iss' field
        # as we do not want to attempt to verify it
        payload_list.append({
            'iss': 'https://malicious-iam.idc.biz/',
            'jti': '098cb343-c45e-490d-8aa0-ce1873cdc5f8',
            'iat': int(time.time()) - 2000000,
            'sub': CLIENT_ID,
            'exp': int(time.time()) + 200000
        })

        for payload in payload_list:
            token = self._create_token(payload, PRIVATE_KEY)

            with self.settings(IAM_HOSTNAME_LIST=['iam-test.idc.eu']):
                self.assertFalse(
                    self._token_checker._is_token_issuer_trusted(payload),
                    "Payload %s should not be accepted!" % payload
                )

                self.assertEqual(
                    self._token_checker.valid_token_to_id(token), None,
                    "Token with payload %s should not be accepted!" % payload
                )

    def test_is_token_json_temporally_valid(self):
        """
        Check that temporally invalid payload/token is detected.

        Both by:
         - _is_token_json_temporally_valid
         - valid_token_to_id

        The first method checks the temporal validity of the payload
        The second method detemines wether the token is invalid
        """
        payload_list = []

        # Test that we reject a payload without 'iat' or 'exp'
        # as the tokens should have a lifetime
        payload_list.append({
            'sub': CLIENT_ID,
            'iss': 'https://iam-test.indigo-datacloud.eu/',
            'jti': '714892f5-014f-43ad-bea0-fa47579db222'
        })

        # Test that we reject a payload without 'exp'
        # as such a token would never expire
        payload_list.append({
            'iss': 'https://iam-test.indigo-datacloud.eu/',
            'jti': '098cb343-c45e-490d-8aa0-ce1873cdc5f8',
            'iat': int(time.time()) - 2000000,
            'sub': CLIENT_ID
        })

        # Test that we reject a payload without 'iat'
        # as all tokens should indicate when they were issued
        payload_list.append({
            'iss': 'https://iam-test.indigo-datacloud.eu/',
            'jti': '098cb343-c45e-490d-8aa0-ce1873cdc5f8',
            'sub': CLIENT_ID,
            'exp': int(time.time()) + 200000
        })

        # Test that we reject a payload with an 'iat' and 'exp'
        # in the past (e.g. they have expired)
        payload_list.append({
            'iss': 'https://iam-test.indigo-datacloud.eu/',
            'jti': '098cb343-c45e-490d-8aa0-ce1873cdc5f8',
            'iat': int(time.time()) - 2000000,
            'sub': CLIENT_ID,
            'exp': int(time.time()) - 200000
        })

        # Test that we reject a payload with an 'iat' and 'exp'
        # in the future (as we should as they are not yet valid)
        payload_list.append({
            'iss': 'https://iam-test.indigo-datacloud.eu/',
            'jti': '098cb343-c45e-490d-8aa0-ce1873cdc5f8',
            'iat': int(time.time()) + 200000,
            'sub': CLIENT_ID,
            'exp': int(time.time()) + 2000000
        })

        for payload in payload_list:
            # Assert the underlying helper method reponsible for
            # checking temporal validity returns False when passed
            # temporally invalid payloads
            self.assertFalse(
                self._token_checker._is_token_json_temporally_valid(payload),
                "Payload %s should not be accepted!" % payload
            )

            # Assert the wrapper method valid_token_to_id returns
            # None when passed temporally invalid tokens
            token = self._create_token(payload, PRIVATE_KEY)
            self.assertEqual(
                self._token_checker.valid_token_to_id(token), None,
                "Token with payload %s should not be accepted!" % payload
            )

    def test_garbage_token(self):
        """Test a garbage token is rejected."""
        token = 'ffnnsdifsdjofjfosdjfodsjfosdjofj'
        result = self._token_checker.valid_token_to_id(token)
        self.assertEqual(result, None)

    def test_http_issuer_ban(self):
        """Test a HTTP issuer is rejected."""
        self.assertEqual(
            self._token_checker._check_token_not_revoked(None,
                                                         'http://idc.org'),
            None
        )

        self.assertFalse(
            self._token_checker._verify_token(None,
                                              'http://idc.org')
        )

    def _create_token(self, payload, key):
        """Return a token, signed by key, correspond to the payload."""
        return jwt.encode(payload, key, algorithm='RS256')

    def _standard_token(self):
        """Return a token that will be valid if properly signed."""
        return {
            'iss': 'https://iam-test.idc.eu/',
            'jti': '098cb343-c45e-490d-8aa0-ce1873cdc5f8',
            'iat': int(time.time()) - 2000000,
            'sub': CLIENT_ID,
            'exp': int(time.time()) + 200000
        }


# Use this Client ID in tokens
CLIENT_ID = 'ac2f23e0-8103-4581-8014-e0e82c486e36'

# Used to sign tokens
PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAqxAx1H7MabcEYhis3SJoaA3tq6wUgzKzv4c16nAW4yT21P8O
lL9qKYkzWuJWWiI90ecEHONEjDI+dFfaj/bK2O0jDT1NqVZbn2kW3sXaqUs4lUIg
5iPXysknitQjQsO1AmLZXFMNSPCKhBpMPxqG9vBMSxVMIXxXMZXeFpFIOqHFXgtq
+KmktwB2Aj/91NlSSj+Lw7bVSaZZNok/kuN/q43A6LS9uRHCQy9aeU0G8rZoqFSf
F6LypFBN8iZxaw8zlUKy2NYpu6opNUMhTxP7JmEy6yr4kMY7LUNRAKoP4tpgwwgt
hnecyprGGr93vh2qifP+bV3J3oa+ub1+jql63QIBIwKCAQAJxmk/V7PoyKEqLUu0
3WUNQp/d7JN1NhjmX39se28Fqlc/XwglwcuNWEwT0mtVm46BBeL6ViEslSgj58NY
rwRG6PqwTKVaIjEfDVHDlkcCXBHcpLFsPI/89Y07IhCkurni4RO8IgDCVuNYAYCz
JhZXQO5qsMKFkhOcbva/dgQgm2+yX6i1lFYNstpdr8ODBhiT6Tn7B5CONbLICJFd
7SdVAORFgdOvRLHkLPcL4I6x0hautCvEf2x47kRaLGtPMsFJQSZYl+Z81whwrJTM
zGTLH4kM6qHlIhABYhqME5bCVzHYmvXW+uIgVLznfIzQFyewRdMJZzCp0XxqjOkX
yixLAoGBANbKpZVf2giL26RpUsZ8waIFc7tQAzWSqwF384XPFn8tdN1DBT3R2rQk
8gnjX07Z6YrxkEvAhb7hDgB09EGPx1nDEXnFk1Y2xXePBccdSVQvjc/ExX0YGtBi
ZCbiJW5+ORx8olxkNiEVUvik62470fOkWtrwO6qq77lc5QQVKlopAoGBAMvh280v
K7o7auQxaVnjLQIoWlnKrz3+T58R/8nYFtAuiUjlT4dsBOUFKm1GE/bw8FDFc1Vo
Z0l++KFTKNnxT6NQPRoE4JH8MZ3ycS4x0cMUK4TEW2pO11KyqlmLLdMbq1v3zgLw
GwZ/fOOi0GlItoBY0zZYlEuXxQQUNotZLRmVAoGBAMRhgXKgx1hFWxn55UfChSZr
Yn9fGOCGGLDissN7gkhkExNwedIe89fnQ7FE6Wyp+hiiWAq+pircZJK0EoUVvZPl
jFITuehsl0i9RxxyjC+2cwcaTik6nCw8s1bAIjki8mMwH2pqQB4/Yc1jlWwZb3+s
Nc98jlLlbXZGTbqXAiaLAoGBAIvOExBa3CfuOqsakWI1YLEFukwzNlZlPelrbZG4
vy+q4cuV7WQs0CgDis6WdBcLnXk28AANE6AcjTtsOUT9PexURyfI1IFcectkat3Z
BN2KLHhMIW135BtzMvuSoxRqvqV2uSaWA+cy2Uui2A2uNAA86JpLXl+4hxi9Zzr7
UiArAoGBALrLwrhYtwOhMoJPK+XlMTJpLFSOUiGcFg06cvDtsUCz1H0Ma1TuHNSJ
/El54J1bGpJ/h212wB+gAHE7nRNJfFn5vPJtqwMv/SW675SA4mlKi2xoBO1NW/sw
FIusZ178P2e/lc+1QJoKkrM7ZKxnDvNj2Lt3B3JmXunXWZpn4i8Q
-----END RSA PRIVATE KEY-----"""

# Used to verify tokens signed with PRIVATE_KEY
PUBLIC_KEY = {"keys": [{"kty": "RSA",
                        "n": ("qxAx1H7MabcEYhis3SJoaA3tq6wUgzKzv4c"
                              "16nAW4yT21P8OlL9qKYkzWuJWWiI90ecEHO"
                              "NEjDI-dFfaj_bK2O0jDT1NqVZbn2kW3sXaq"
                              "Us4lUIg5iPXysknitQjQsO1AmLZXFMNSPCK"
                              "hBpMPxqG9vBMSxVMIXxXMZXeFpFIOqHFXgt"
                              "q-KmktwB2Aj_91NlSSj-Lw7bVSaZZNok_ku"
                              "N_q43A6LS9uRHCQy9aeU0G8rZoqFSfF6Lyp"
                              "FBN8iZxaw8zlUKy2NYpu6opNUMhTxP7JmEy"
                              "6yr4kMY7LUNRAKoP4tpgwwgthnecyprGGr9"
                              "3vh2qifP-bV3J3oa-ub1-jql63Q"),
                        "e": "Iw"}]}

# Used to 'forge' a token that PUBLIC_KEY will not be able to verify
FORGED_PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCxHCAbJMUth6NV
5dz3J6p13NY0deuhST4ped3ogFHvfMlj0ehJMxLVe/B5oooyQkaSyA0yc4eBfYxj
W4tmOGyWZic1wLhQUQpXvdVcmt+f26GewnIvWOI4MSg1C+Qg9E4I/eIlpz0jrkbq
q8k/x4pr/c+X8TNiaiZb2Sjp/SFdpwqZ4Eh8u3PPc/B5/mJfvg0T8mrjZ8kQkPcB
SH+JzbzyFuEpa1OqAWeSOaQniyS2SEdW8DT0/AlQcf3UmvR0Dh5N6KltwWdWdocg
1jsLCYa32/8uiBJ3JM/C+vWtBjFGGoHp4msk9VAUnq9oWA5z5NT7G1lpoAj1Hjuu
MnRM9cGnAgMBAAECggEBAIXzrri428TuxHNwMepgfsU77GqrETbgLXqzKEnz24SV
TcAIf3X1gfYjEiL88ybGB5h2Y7zXshIXAboX/9ulK0OpKVi3VO+yC2+HLTsoC6Bd
PeTUTgZPZHF5hF5yiuz9uZOFaahuz4gQBKTynnh1k9TPl1Xk4Kc7f52SJiarA7RP
In7R/YDW6Wxg8fCID1L2McFxlAdHF94oG1qNe1AriaUKZ9MUKaGxmdxuAk3pA1cC
IqTQYHb1zgJ8oFlhqYVubTL/85ADVV1aY0/UKZcwL1xLJ2xifGvbYPUs5gMJ0w0F
zHNdhZ6991/F4Txr9Q3kwZX8uwxFFgWSh2qE2aJno8ECgYEA5OLDb3G6zIpbmAU8
LbfWt/PgsQAa0XtnCrzyz5SnBjPqbesPrg6VxPVdP2/OW+yBvtxmgo3M5xC7LV8C
x1/In90FXa2KfSXj2OENR/ks55BVdKcI+Jmljmum8AkPvdwb42ztpKgSC8BhItKd
G5Ft1B2t6EJZY2SPL8UbUXtAkgcCgYEAxhcx2zPlC+x7Y0oKidZswR3M2iB56One
3dFabzWRA+P7/YA1VM+VPppSDr8AqGpiv0rLh7xK0R6usjmZ1Z/X4oQDF5uiH0uK
DqsXDF61fFjKClfY4WcUzlcolJ8AD9q50o7bc+hc2WEWxbh/iqfzEWYIa3Y+cuUz
XMOZJux+62ECgYBTFREV6fWBe5OF2hifC8VQHqFn/n69nYqoti95NB9wu/WTkqit
aLPqu5nuhfolGfN6wWwgZbKECWm4LW3Hyzf693KUL4M+rDtJpV95ybQIFjc+0ccK
3lLfIKqHJPLm2vfwlMCqbSunwlxAFK1crWxte5x921+xGXZ0Q5sH97JXjwKBgEGa
HODDZu9z+ckAFE1hvdKW0+jJKJaCHVTIqHJ8AvKO5j0l4IOd24dIBDTt/IHJ+bnw
Q0dIjF6FEsXjXZbpwM07euqumBpVIfuJnbBzDReJMCAMx76eLL3JD59oqNSXU0Lw
HK1eHqG/DZOdbl+1D0KLz+4G0teqIEBwZqAFYmMBAoGBANmBGtkC6APqRe5Dzz9F
z5L9Mt9Krz8EI6s43XA4fYhouw07zGY0816BGa7r772duZkfh/J8kuxWRdvseo5G
y3EDz4+nl+tzxzYvbsSNOK8ceJRHNwJQPZuq166svKGLe6tj65MtfvIUTzWUU9FW
OLxDCvBa2CgAJVfUO1MhtX/L
-----END PRIVATE KEY-----"""
