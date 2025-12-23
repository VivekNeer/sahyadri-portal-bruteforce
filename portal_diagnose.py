#!/usr/bin/env python3
"""Simple portal/network diagnostic helper.

Usage: python3 portal_diagnose.py

Creates `portal_diag.log` with results and prints a short summary.
"""
import socket
import subprocess
import time
import urllib.request
import urllib.error
import sys

HOST = '172.21.0.1'
PORT = 8090
LOGFILE = 'portal_diag.log'

def log(msg):
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOGFILE, 'a') as f:
        f.write(line + '\n')

def run_ping(host):
    log(f"PING -> {host}")
    try:
        res = subprocess.run(['ping', '-c', '4', host], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=15)
        log(res.stdout.strip())
        return True
    except Exception as e:
        log(f"Ping failed: {e}")
        return False

def tcp_connect(host, port, timeout=5):
    log(f"TCP CONNECT -> {host}:{port}")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        s.close()
        log("TCP connect: SUCCESS")
        return True
    except Exception as e:
        log(f"TCP connect failed: {e}")
        return False

def http_get(url, timeout=10):
    log(f"HTTP GET -> {url}")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'portal_diagnose/1.0'})
        with urllib.request.urlopen(req, timeout=timeout) as res:
            code = res.getcode()
            body = res.read(512)
            log(f"HTTP {code}; first {len(body)} bytes: {body[:200]!r}")
            return code
    except urllib.error.HTTPError as e:
        log(f"HTTP error: {e.code} {e.reason}")
        return getattr(e, 'code', None)
    except Exception as e:
        log(f"HTTP request failed: {e}")
        return None

def detect_captive_portal():
    # Known URL that returns 204 when internet is open
    url = 'http://clients3.google.com/generate_204'
    code = http_get(url)
    if code == 204:
        log('No captive portal detected (204 from generate_204).')
    elif code and (300 <= code < 400):
        log('Received redirect; captive portal likely present.')
    else:
        log('Unable to determine captive portal state.')

def main():
    log('--- Starting portal diagnostics ---')
    run_ping(HOST)
    tcp_connect(HOST, PORT)
    http_get(f'http://{HOST}:{PORT}/login.xml')
    detect_captive_portal()
    log('--- Diagnostics complete ---')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        log('Interrupted by user')
        sys.exit(1)
