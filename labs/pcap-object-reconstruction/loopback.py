"""Prepare and transfer one dummy file on IPv4 loopback; never capture packets."""
import argparse
from datetime import datetime, timezone
from http.client import HTTPConnection, HTTPException
from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
from socketserver import TCPServer
import sys
import threading

from practice import ROOT, fresh_target, freeze, read_bytes, save, sha_bytes, write_new
from foundation_runtime import read_json, require, safe_path

HOST = '127.0.0.1'
PORT = 8765
BODY = b'Local training object. No personal data.\n'


def attempt_path(output):
    # Apply the same path contract without creating or overwriting a folder.
    import re
    require(isinstance(output, str) and re.fullmatch(r'run/[a-z0-9][a-z0-9-]{0,47}', output),
            'use the prepared run/a-new-short-name')
    target = safe_path(ROOT / output)
    require(safe_path(ROOT / 'run') in target.parents and target.is_dir(),
            'prepare a fresh attempt first')
    return target


def prepare(output):
    target = fresh_target(output)
    source = target / 'source' / 'dummy.txt'
    write_new(source, BODY)
    digest = freeze(source)
    save(target / 'setup.json', {
        'operation': 'local HTTP dummy-transfer preparation',
        'host': HOST, 'port': PORT, 'request_path': '/dummy.txt',
        'source_bytes': len(BODY), 'source_sha256': digest,
        'capture_performed_by_helper': False})
    write_new(target / 'prediction.txt', b'Prediction:\nEvidence to expect:\nOne limitation:\n')
    write_new(target / 'interpretation.txt', b'Observed packets and object bytes:\nComparison:\nLimitations:\n')
    return {'prepared': output, 'next': 'Save prediction.txt, then follow the capture commands in LOCAL-CAPTURE.md.'}


class LocalServer(HTTPServer):
    allow_reuse_address = False

    def server_bind(self):
        # On Windows refuse a second listener on this exact port.
        if hasattr(socket, 'SO_EXCLUSIVEADDRUSE'):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        TCPServer.server_bind(self)
        self.server_name, self.server_port = HOST, PORT

    def get_request(self):
        connection, address = super().get_request()
        connection.settimeout(3)
        return connection, address


def transfer(output):
    target = attempt_path(output)
    setup = read_json(target / 'setup.json')
    require(setup.get('host') == HOST and setup.get('port') == PORT,
            'prepared loopback endpoint required')
    source = target / 'source' / 'dummy.txt'
    payload = read_bytes(source)
    require(payload == BODY and setup.get('source_sha256') == sha_bytes(payload),
            'prepared dummy bytes changed; preserve this attempt and prepare another')
    destination = target / 'output' / 'client-dummy.txt'
    receipt = target / 'transfer-receipt.json'
    require(not safe_path(destination).exists() and not safe_path(receipt).exists(),
            'transfer already attempted; prepare a fresh attempt')
    requests = []

    class Handler(BaseHTTPRequestHandler):
        protocol_version = 'HTTP/1.1'

        def do_GET(self):
            requests.append({'peer': self.client_address[0], 'method': 'GET', 'path': self.path})
            if self.path != '/dummy.txt':
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', str(len(payload)))
            self.send_header('Connection', 'close')
            self.end_headers()
            self.wfile.write(payload)
            self.close_connection = True

        def log_message(self, format, *args):
            pass

    started = datetime.now(timezone.utc).isoformat()
    # No directory handler, proxy lookup, DNS lookup, or caller-selected host.
    server = LocalServer((HOST, PORT), Handler)
    server.timeout = 5
    worker = threading.Thread(target=server.handle_request, daemon=True)
    client = HTTPConnection(HOST, PORT, timeout=5)
    worker.start()
    try:
        client.request('GET', '/dummy.txt', headers={'Connection': 'close'})
        response = client.getresponse()
        received = response.read(len(BODY) + 1)
        require(response.status == 200 and response.getheader('Content-Length') == str(len(BODY)),
                'unexpected local HTTP response')
        require(received == payload, 'received bytes differ; keep the capture for inspection')
        write_new(destination, received)
    finally:
        client.close()
        worker.join(timeout=8)
        server.server_close()
    require(not worker.is_alive(), 'local handler did not stop')
    after = sha_bytes(read_bytes(source))
    save(receipt, {
        'operation': 'actual local plain-HTTP dummy transfer',
        'started_utc': started, 'ended_utc': datetime.now(timezone.utc).isoformat(),
        'host': HOST, 'port': PORT, 'requests': requests,
        'source_sha256_before': sha_bytes(payload), 'source_sha256_after': after,
        'source_bytes_unchanged': after == sha_bytes(payload),
        'received_bytes': len(received), 'received_sha256': sha_bytes(received),
        'server_closed': True, 'capture_performed_by_helper': False,
        'capture_and_export_status': 'Verify the separately acquired capture and exported object.',
        'learner_mastery': 'not assessed'})
    return {'saved': output + '/transfer-receipt.json', 'server_closed': True,
            'next': 'Wait for capture to stop. Inspect the copied capture and export its HTTP object.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for command in ('prepare', 'transfer'):
        part = commands.add_parser(command)
        part.add_argument('--out', required=True)
    args = parser.parse_args()
    try:
        import json
        result = prepare(args.out) if args.command == 'prepare' else transfer(args.out)
        print(json.dumps(result, indent=2))
        return 0
    except (ValueError, OSError, HTTPException) as error:
        print('Loopback input error: ' + str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
