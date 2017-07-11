"""This module contains the TokenChecker class."""
import base64
import datetime
import httplib
import json
import logging
import socket
import urllib2

from django.conf import settings
from django.core.cache import cache
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTClaimsError, JWTError


class TokenChecker:
    """This class contains methods to check a JWT token for validity."""

    def __init__(self, cert, key):
        """Initialize a new TokenChecker."""
        self.logger = logging.getLogger(__name__)
        # cache is used to maintain an dicitonary of issuer/cache cut off pairs
        self.cache = {}
        self._cert = cert
        self._key = key

    def valid_token_to_id(self, token):
        """Introspect a token to determine it's origin."""
        jwt_unverified_json = jwt.get_unverified_claims(token)

        unverified_token_id = jwt_unverified_json['sub']
        # if token is in the cache, we say it is valid
        if cache.get(unverified_token_id) == token:
            self.logger.info("Token for user %s is in cache." %
                             unverified_token_id)

            return jwt_unverified_json['sub']

        # otherwise, we need to validate the token
        if not self._is_token_json_temporally_valid(jwt_unverified_json):
            return None

        if not self._is_token_issuer_trusted(jwt_unverified_json):
            return None

        issuer = jwt_unverified_json['iss']
        # we can pass issuer because the previous 'if' statement
        #  returns if jwt_unverified_json['iss'] is missing.
        issuer = jwt_unverified_json['iss']
        if not self._verify_token(token, issuer):
            return None

        # check the token has not been revoked
        verifed_token_id = self._check_token_not_revoked(token, issuer)
        # if the IAM disagrees with the token sub, reject ir
        if verifed_token_id != jwt_unverified_json['sub']:
            return None

        # if the execution gets here, we can cache the token
        # cache is a key: value like structure with an optional timeout
        # as we only need the token stored we use that as the key
        # and None as the value.
        # Cache timeout set to 300 seconds to enable quick revocation
        # but also limit the number of requests to the IAM instance
        # Caching is also done after token validation to ensure
        # only valids tokens are cached
        cache.set(jwt_unverified_json['sub'], token, 300)

        return jwt_unverified_json['sub']

    def _check_token_not_revoked(self, token, issuer):
        """Contact issuer to check if the token has been revoked or not."""
        if "https://" not in issuer:
            self.logger.info('Issuer not https! Ending revokation check!')
            return None

        try:
            auth_request = urllib2.Request('%s/introspect' % issuer,
                                           data='token=%s' % token)

            server_id = settings.SERVER_IAM_ID
            server_secret = settings.SERVER_IAM_SECRET

            encode_string = '%s:%s' % (server_id, server_secret)

            base64string = base64.encodestring(encode_string).replace('\n', '')

            auth_request.add_header("Authorization", "Basic %s" % base64string)
            auth_result = urllib2.urlopen(auth_request)

            auth_json = json.loads(auth_result.read())
            client_id = auth_json['client_id']

        except (urllib2.HTTPError,
                urllib2.URLError,
                httplib.HTTPException,
                KeyError) as error:
            self.logger.error("%s: %s", type(error), str(error))
            return None

        self.logger.info("Token identifed as belonging to %s", client_id)
        return client_id

    def _verify_token(self, token, issuer):
        """Fetch IAM public key and veifry token against it."""
        if "https://" not in issuer:
            self.logger.info('Issuer not https! Will not verify token!')
            return False

        # extract the IAM hostname from the issuer
        hostname = issuer.replace("https://", "").replace("/", "")

        # get the IAM's public key
        key_json = self._get_issuer_public_key(hostname)

        # if we couldn't get the IAM public key, we cannot verify the token.
        if key_json is None:
            self.logger.info('No IAM Key found. Cannot verfiy token.')
            return False

        try:
            jwt.decode(token, key_json)
        except (ExpiredSignatureError, JWTClaimsError, JWTError) as err:
            self.logger.error('Could not validate token: %s, %s',
                              type(err), str(err))
            return False

        return True

    def _get_issuer_public_key(self, hostname):
        """Return the public key of an IAM Hostname."""
        try:
            conn = httplib.HTTPSConnection(hostname,
                                           cert_file=self._cert,
                                           key_file=self._key)

            conn.request('GET', '/jwk', {}, {})
            return conn.getresponse().read()

        except socket.gaierror as e:
            slef.logger.info('socket.gaierror: %s, %s',
                             e.errno, e.strerror)

            return None

    def _is_token_issuer_trusted(self, token_json):
        """
        Return True if the 'issuer' hostname is in settings.IAM_HOSTNAME_LIST.

        Otherwise (or if 'iss' missng) return False.
        """
        try:
            issuer = token_json['iss']
        except KeyError:
            self.logger.info("Token missing 'iss'")
            self.logger.debug(token_json)
            return False

        # extract the IAM hostname from the issuer
        hostname = issuer.replace("https://", "").replace("/", "")

        if hostname in settings.IAM_HOSTNAME_LIST:
            self.logger.info("Token 'iss' is an approved IAM")
            self.logger.debug(token_json)
            return True
        else:
            self.logger.info("Token 'iss' is not an approved IAM")
            self.logger.debug(token_json)
            return False

    def _is_token_json_temporally_valid(self, token_json):
        """
        Check JWT Token JSON is temporarily valid.

        Return True if:
         - Both 'Issued At' (iat) and Expired' (exp) are present
         - iat is in the past
         - exp is in the future
        """
        now = int(datetime.datetime.now().strftime('%s'))
        try:
            # check 'iat' (issued at) is in the past and 'exp' (expires at)
            # is in the future
            if token_json['iat'] > now or token_json['exp'] < now:
                self.logger.info("Token 'iat' or 'exp' invalid")
                self.logger.debug(token_json)
                self.logger.debug("Time now: %s", now)
                return False
        # it's possible a token doesn't have an 'iat' or 'exp'
        except KeyError:
            self.logger.info("Token missing 'iat' or 'exp'")
            self.logger.debug(token_json)
            return False

        # if we get here, the token is temporarily valid
        return True
