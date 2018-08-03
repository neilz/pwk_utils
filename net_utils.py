''' Functions for doing vairous common network tasks
'''
import socket
import sys
import fcntl
import subprocess

def get_iface_ipv4(iface):
    if iface:
        out = subprocess.check_output(["ifconfig", iface]).decode(sys.getfilesystemencoding())
        lines = [line.strip() for line in out.split("\n")]
        for l in lines:
            if l.startswith("inet "):            
                return l.split(" ")[1]
