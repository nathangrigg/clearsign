#!/usr/bin/python

# With minor changes by Nathan Grigg
#
# Original Copyright 2008 Lenny Domnitser <http://domnit.org/>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

__all__ = 'clarify',
__author__ = 'Lenny Domnitser'
__version__ = '0.1'

import email
import re

TEMPLATE = '''-----BEGIN PGP SIGNED MESSAGE-----
Hash: %(hashname)s
NotDashEscaped: You need GnuPG to verify this message

%(text)s%(sig)s'''


def _clarify(message, messagetext):
    if message.get_content_type() == 'multipart/signed':
        if message.get_param('protocol') == 'application/pgp-signature':
            # normalize line endings to \n for processing
            messagetext=messagetext.replace('\r\n', '\n').replace('\r', '\n')
            hashname = message.get_param('micalg').upper()
            assert hashname.startswith('PGP-')
            hashname = hashname.replace('PGP-', '', 1)
            textmess, sigmess = message.get_payload()
            assert sigmess.get_content_type() == 'application/pgp-signature'
            #text = textmess.as_string() - not byte-for-byte accurate
            text = messagetext.split('\n--%s\n' % message.get_boundary(), 2)[1]
            sig = sigmess.get_payload()
            assert isinstance(sig, str)
            # Setting content-type to application/octet instead of text/plain
            # to maintain CRLF endings. Using replace_header instead of
            # set_type because replace_header clears parameters.
            message.replace_header('Content-Type', 'application/octet')
            clearsign = TEMPLATE % locals()
            clearsign = clearsign.replace(
                '\r\n', '\n').replace('\r', '\n').replace('\n', '\r\n')
            message.set_payload(clearsign)
    elif message.is_multipart():
        for message in message.get_payload():
            _clarify(message, messagetext)


def clarify(messagetext):
    '''given a string containing a MIME message, returns a string
    where PGP/MIME messages are replaced with clearsigned messages.'''

    message = email.message_from_string(messagetext)
    _clarify(message, messagetext)
    return message.as_string()

def verify(text):
    '''Pipe to gpg for verification and exit'''
    import subprocess
    process=subprocess.Popen(['/usr/bin/env', 'gpg','--verify','--batch'],stdin=subprocess.PIPE)
    process.communicate(text)
    process.wait()
    # preserve the gpg error code
    sys.exit(process.returncode)

if __name__ == '__main__':
    import sys,argparse
    parser=argparse.ArgumentParser(
        description='Convert a PGP/MIME signed email to a clearsigned message.  If no file is given, input is read from stdin.')
    parser.add_argument('file',metavar='file',type=argparse.FileType('r'),
        nargs="?",default=sys.stdin,help='a file containing the whole MIME email')
    parser.add_argument('-v','--verify',help="pass output to gpg to verify signature",
        action='store_true')
    args=parser.parse_args()
    output = (clarify(args.file.read()))
    if args.verify:
        verify(output)
    else:
        sys.stdout.write(output)

