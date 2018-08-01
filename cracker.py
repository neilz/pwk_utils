#!/usr/bin/python3
""" Utility for neding hshdumps to http://cracker.offensive-security.com/
"""
import argparse
from html.parser import HTMLParser
import sys

import requests as req


URL = "http://cracker.offensive-security.com/insert.php"


class MLStripper(HTMLParser):
    """ Parser class used to strip HTML tags from server response
    """
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)


def check_hash(priority_code, lm_hash):
    """ Function used to send crack requests to cracked app
    """
    if not lm_hash:
        raise ValueError("Will not submit invalid hash: <%s>" % lm_hash)
    data = {"type": "lm", "method": "table"}
    data["priority"] = str(priority_code)
    data["hash"] = lm_hash
    result = req.post(URL, data=data)
    if len(result.text) > 512:
        raise RuntimeError("Recieved bad response from service (too long)")

    s = MLStripper()
    s.feed(result.text)
    return s.get_data().strip()


def parse_line(line):
    """ Function used to parse LM+NT hash(es) from input line
    """
    parts = line.strip().split(":")
    if len(parts) == 1:
        return parts[0]
    elif len(parts) == 2:
        if parts[0] and parts[1]:
            return ":".join(parts)
    elif len(parts) >= 4:
        return ":".join(parts[2:4])
    raise ValueError("Could not parse hash(es) from input: <%s>" % line)


def crack_input(priority_code, line):
    """ Function used to coordinate crack requests
    """
    try:
        hash_val = parse_line(line)
    except ValueError as err:
        print(err)
        return

    try:
        passwd = check_hash(priority_code, hash_val)
    except ValueError as err:
        print(err)
        return
    except RuntimeError as err:
        print(err)
        return

    print_result(line, passwd)


def print_result(hash_in, passwd_out):
    """ Funtion userd to print result to console
    """
    print("%s\n\t=> %s" % (hash_in, passwd_out))

def main():
    """ Main function for handling user arguments
    """
    parser = argparse.ArgumentParser(description='Check windows hashdumps against http://cracker.offensive-security.com')
    parser.add_argument('priority_code', help='Priority code provided by PWK course console')
    parser.add_argument('hash_dump', default='-', nargs='?',
            help='LM/NTLM hash to be sent to cracker; default reads from STDIN')
    args = parser.parse_args()

    if args.hash_dump == "-":
        for line in sys.stdin.readlines():
            crack_input(args.priority_code, line.strip())
    else:
        crack_input(args.priority_code, args.hash_dump)


if __name__ == "__main__":
    main()
