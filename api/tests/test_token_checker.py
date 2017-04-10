"""This module tests the JSON Web Token validation."""

import logging
import unittest
import time

from jose import jwt

from api.utils.TokenChecker import TokenChecker


# Using unittest and not django.test as no need for overhead of database
class TokenCheckerTest(unittest.TestCase):
    """Tests the JSON Web Token validation."""

    def setUp(self):
        """Create a new TokenChecker and disable logging."""
        self._token_checker = TokenChecker()
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        """Re-enable logging."""
        logging.disable(logging.NOTSET)

    def test_is_token_json_temporally_valid(self):
        """
        Check that temporally invalid payload/token is detected.

        Both by:
         - _is_token_json_temporally_valid
         - is_token_valid

        The first method checks the temporal validity of the payload
        The second method detemines wether the token is invalid
        """
        payload_list = []

        # Add a payload wihtout 'iat' or 'exp' to the payload list
        # to test we reject these (as we are choosing to)
        payload_list.append({
            'sub': 'ac2f23e0-8103-4581-8014-e0e82c486e36',
            'iss': 'https://iam-test.indigo-datacloud.eu/',
            'jti': '714892f5-014f-43ad-bea0-fa47579db222'})

        # Add a payload without 'exp' to the payload_list
        # to test we reject these (as we are choosing to)
        payload_list.append({
            'iss': 'https://iam-test.indigo-datacloud.eu/',
            'jti': '098cb343-c45e-490d-8aa0-ce1873cdc5f8',
            'iat': int(time.time()) - 2000000,
            'sub': 'ac2f23e0-8103-4581-8014-e0e82c486e36'})

        # Add a payload without 'iat'
        # to test we reject these (as we are choosing to)
        payload_list.append({
            'iss': 'https://iam-test.indigo-datacloud.eu/',
            'jti': '098cb343-c45e-490d-8aa0-ce1873cdc5f8',
            'sub': 'ac2f23e0-8103-4581-8014-e0e82c486e36',
            'exp': int(time.time()) + 200000})

        # Add a payload with an 'iat' and 'exp' in the past
        # (e.g. they have expired) to test we are
        # rejecting these
        payload_list.append({
            'iss': 'https://iam-test.indigo-datacloud.eu/',
            'jti': '098cb343-c45e-490d-8aa0-ce1873cdc5f8',
            'iat': int(time.time()) - 2000000,
            'sub': 'ac2f23e0-8103-4581-8014-e0e82c486e36',
            'exp': int(time.time()) - 200000})

        # Add a payload with an 'iat' and 'exp' in the future
        # to test we are rejecting these (as we should as they
        # are not yet valid)
        payload_list.append({
            'iss': 'https://iam-test.indigo-datacloud.eu/',
            'jti': '098cb343-c45e-490d-8aa0-ce1873cdc5f8',
            'iat': int(time.time()) + 200000,
            'sub': 'ac2f23e0-8103-4581-8014-e0e82c486e36',
            'exp': int(time.time()) + 2000000})

        for payload in payload_list:
            # Assert the underlying helper method reponsible for
            # checking temporal validity returns False when passed
            # temporally invalid payloads
            self.assertFalse(
                self._token_checker._is_token_json_temporally_valid(payload),
                "Payload %s should not be accepted!" % payload)

            # Assert the wrapper method is_token_valid reutrns
            # False when passed temporally invalid tokens
            token = self._create_token(payload, PRIVATE_KEY)
            self.assertFalse(
                self._token_checker.is_token_valid(token),
                "Token with payload %s should not be accepted!" % payload)

    def _create_token(self, payload, key):
        """Return a token, signed by key, correspond to the payload."""
        return jwt.encode(payload, key, algorithm='RS256')

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
