# Description

This is a Python module and command line interface to convert a PGP/MIME email
to a clearsigned message.

# Command line usage

    clearsign.py [-v] [-h] [file]

    file          the file containing the MIME email
                  If no file is given, stdin is used.

    -v, --verify  passes the output to gpg to verify the signature
    -h, --help    displays a help message and exits

# Author

The script was originally written by Lenny Domnitser but is no longer
maintained. Nathan Grigg wrote a tiny bug fix and enriched the command
line interface.
