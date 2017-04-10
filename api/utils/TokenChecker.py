"""This module contains the TokenChecker class."""
import datetime
import logging

from jose import jwt


class TokenChecker:
    """This class contains methods to check a JWT token for validity."""

    def __init__(self):
        """Initialize a new TokenChecker."""
        self.logger = logging.getLogger(__name__)
        # cache is used to maintain an dicitonary of issuer/cache cut off pairs
        self.cache = {}

    def is_token_valid(self, token):
        """Introspect a token to determine it's origin."""
        jwt_unverified_json = jwt.get_unverified_claims(token)

        if not self._is_token_json_temporally_valid(jwt_unverified_json):
            return False

        return True

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
