"""
This module contains a simple class for sending Accounting Records.

Accounting Records are sent to a REST endpoint.
If run as a python script, this module will
send messages to the REST endpoint defined in main().
"""


import httplib
import json
import logging
import ssl
import socket
import sys
import time

from dirq.QueueSimple import QueueSimple

log = logging.getLogger(__name__)


class Sender(object):
    """A simple class for sending Accounting Records to a REST endpoint."""

    def __init__(self, dest, qpath, cert, key):
        """Initialize a Sender."""
        self._cert = cert
        self._key = key
        self._outq = QueueSimple(qpath)
        self._dest = dest

    def send_all(self):
        """Send all the messages in the outgoing queue via REST."""
        log.info('Found %s messages.', self._outq.count())
        for msgid in self._outq:
            if not self._outq.lock(msgid):
                log.warn('Message was locked. %s will not be sent.', msgid)
                continue

            text = self._outq.get(msgid)

            url = '/api/v1/cloud/record'
            data = text

            self._rest_connect('POST', url, data, {}, 202)
            log.info("Sent %s", msgid)

            time.sleep(0.1)

            self._outq.remove(msgid)

        log.info('Tidying message directory.')
        try:
            # Remove empty dirs and unlock msgs older than 5 min (default)
            self._outq.purge()
        except OSError, e:
            log.warn('OSError raised while purging message queue: %s', e)

    def _rest_connect(self, verb, url, data, headers, expected_response_code):
        """
        Send a HTTPS request to self._dest.

        Will attempt to repeat if expected_response is not returned.
        """
        attempt_number = 0

        while attempt_number < 3:
            try:
                attempt_number = attempt_number + 1

                conn = httplib.HTTPSConnection(self._dest,
                                               cert_file=self._cert,
                                               key_file=self._key,
                                               strict=False)

                conn.request(verb, url, json.dumps(data), headers)

                response = conn.getresponse()

                if response.status == expected_response_code:
                    return response
                else:
                    log.warning("Could not connect to endpoint, retrying")
                    time.sleep(attempt_number)
                    continue

            except socket.gaierror as e:
                log.info('socket.gaierror: %s, %s',
                         e.errno, e.strerror)
                sys.exit()

        # if here, attempt_number has been exceeded
        log.info('Could not connect to endpoint. Error: %s - %s',
                 response.status, response.reason)
        sys.exit()


def main():
    """Configure a Sender and send Records to an APEL REST interface."""
    # The web address of the accounting server you wish to send to
    # i.e accounting.indigio-datacloud.eu
    dest = ''
    # The directory to read saved accounting messages to
    # i.e /var/spool/apel/cloud
    qpath = ''
    # The location of this machines private key
    # i.e. /etc/httpd/ssl/key.file
    key = ''
    # The location of this machines X.509 certifcate
    # i.e. /etc/httpd/ssl/cert.file
    cert = ''

    sender = Sender(dest, qpath, cert, key)

    sender.send_all()

if __name__ == '__main__':
    main()
