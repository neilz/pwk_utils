#!/usr/bin/python3
""" Script for validating credentials against an ftp server
"""
import argparse
from ftplib import FTP, Error as FTPError
from io import StringIO
import sys

SUCCESS_CODE = '230'
TMP_FILENAME = '.tmp1234.txt'

def check_credentials(ftp_server, username, password, verbose):
    """ Function used to check a set of credentials against an  FTP server
    """
    valid = False
    write = False
    with FTP(ftp_server) as ftp:
        try:
            resp = ftp.login(username, password)
            if verbose:
                print(resp)
        except FTPError as err:
            if verbose:
                print(err)
        else:
            valid = True

        if valid:
            # validate ability to write
            try:
                resp = ftp.storlines("STOR %s" % TMP_FILENAME, StringIO(""))
                if verbose:
                    print(resp)

                ftp.delete(TMP_FILENAME)
                if verbose:
                    print(resp)
            except FTPError as err:
                if verbose:
                    print(err)
            else:
                write = True
    
    # print result of check
    if valid:
        print("PASS (%s)" % ("W" if write else "R"), end='')
    else:
        print("FAIL", end='')
    print(" - %s:%s" % (username, password))

def check_stdin(ftp_server, verbose):
    """ Function used to read credentials from STDIN and check them
    """
    (username, password) = (None, None)
    for line in sys.stdin.readlines():
        if username is None:
            username = line
            continue
        elif password is None:
            password = line
            check_credentials(ftp_server, username, password, verbose)
            (username, password) = (None, None)

def main():
    """ Main function for handling user arguments
    """
    parser = argparse.ArgumentParser(description='Script for validating FTP credentials')
    parser.add_argument('ftp_server', help='Hostname/IP of the FTP server top validate agains')
    parser.add_argument('username', default='anonymous', nargs='?', help='Username to validate')
    parser.add_argument('password', default='', nargs='?', help='Username to validate')
    parser.add_argument('--stdin', dest='STDIN', action='store_const', const=True, default=False, help='Read credentials from STDIN; username and passwd on zeperate lines')
    parser.add_argument('-v', dest='verbose', action='store_const', const=True, default=False, help='Verbose output')
    args = parser.parse_args()

    if args.STDIN:
        check_stdin(args.ftp_server, args.verbose)
    else:
        check_credentials(args.ftp_server, args.username, args.password, args.verbose)


if __name__ == "__main__":
    main()
