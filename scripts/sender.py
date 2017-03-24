"""
This module contains a simple class for sending Accounting Records.

Accounting Records are sent to a REST endpoint.
If run as a python script, this module will
send messages to the REST endpoint defined in main().
"""


import argparse
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

    def __init__(self, dest, qpath, cert, key, api_version):
        """Initialize a Sender."""
        self._cert = cert
        self._key = key
        self._outq = QueueSimple(qpath)
        self._dest = dest
        self._api_version = api_version

    def send_all(self):
        """Send all the messages in the outgoing queue via REST."""
        log.info('Found %s messages.', self._outq.count())
        for msgid in self._outq:
            if not self._outq.lock(msgid):
                log.warn('Message was locked. %s will not be sent.', msgid)
                continue

            text = self._outq.get(msgid)

            path = '/api/%s/cloud/record' % self._api_version
            data = text

            self._rest_send('POST', path, data, {}, 202)
            log.info("Sent %s", msgid)

            time.sleep(0.1)

            self._outq.remove(msgid)

        log.info('Tidying message directory.')
        try:
            # Remove empty dirs and unlock msgs older than 5 min (default)
            self._outq.purge()
        except OSError, e:
            log.warn('OSError raised while purging message queue: %s', e)

    def _rest_send(self, verb, path, data, headers, expected_response_code):
        """
        Send an HTTPS request to self._dest.

        Will attempt to repeat if expected_response is not returned.
        """
        attempt_number = 0

        while attempt_number < 3:
            try:
                attempt_number += 1

                conn = httplib.HTTPSConnection(self._dest,
                                               cert_file=self._cert,
                                               key_file=self._key,
                                               strict=False)

                conn.request(verb, path, json.dumps(data), headers)

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
                sys.exit(1)

        # if here, attempt_number has been exceeded
        log.info('Could not connect to endpoint. Error: %s - %s',
                 response.status, response.reason)
        sys.exit(1)


def main():
    """
    Configure a Sender and send Records to an APEL REST interface.

    Usage:
    sender.py -d DESTINATION -q QUEUE -k KEY -c CERTIFICATE [-v VERSION]

    Options:
    -h, --help        show this help message and exit
    -d DESTINATION, --destination DESTINATION
                      The web address of the accounting server you wish to
                      send to. e.g. accounting.indigio-datacloud.eu (note the
                      lack of 'https://' and endpoint, these are currently
                      assumed)
    -q QUEUE, --queue QUEUE
                      The directory to read saved accounting messages from.
                      e.g. /var/spool/apel/cloud
    -k KEY, --key KEY
                      The path to this machine's private key. e.g.
                      /etc/httpd/ssl/key.file
    -c CERTIFICATE, --certificate CERTIFICATE
                      The location of this machine's X.509 certifcate. e.g.
                      /etc/httpd/ssl/cert.file
    -v VERSION, --version VERSION
                      Version of the APEL REST API Version, expected to be
                      v1
    """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-d", "--destination", type=str, required=True,
                            help=("The web address of the accounting "
                                  "server you wish to send to. "
                                  "e.g. accounting.indigio-datacloud.eu"))

    arg_parser.add_argument("-q", "--queue", type=str, required=True,
                            help=("The directory to read saved accounting "
                                  " messages from. "
                                  "e.g. /var/spool/apel/cloud"))

    arg_parser.add_argument("-k", "--key", type=str, required=True,
                            help=("The path to this machine's private key. "
                                  "e.g. /etc/httpd/ssl/key.file"))

    arg_parser.add_argument("-c", "--certificate", type=str, required=True,
                            help=("The location of this "
                                  "machine's X.509 certifcate. "
                                  "e.g. /etc/httpd/ssl/cert.file"))

    arg_parser.add_argument("-v", "--version", type=str, default="v1",
                            help=("Version of the APEL REST API Version, "
                                  "expected to be v1"))

    args = arg_parser.parse_args()

    sender = Sender(args.destination,
                    args.queue,
                    args.certificate,
                    args.key,
                    args.version)

    sender.send_all()

if __name__ == '__main__':
    main()
