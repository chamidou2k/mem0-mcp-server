"""TLS integration test: HTTPS endpoint verification against a CA bundle.

Generates a self-signed CA and a server certificate with openssl, serves TLS
in-process, and asserts that verification against the configured CA succeeds
while wrong/unverified setups fail. Skips cleanly if openssl is unavailable.
"""

import asyncio
import http.server
import shutil
import ssl
import subprocess
import threading

import httpx
import pytest

import mem0_mcp_server as server

OPENSSL = shutil.which("openssl")

pytestmark = pytest.mark.skipif(OPENSSL is None, reason="openssl not available")


def _run(cmd):
    subprocess.run(cmd, check=True, capture_output=True)


@pytest.fixture(scope="module")
def tls_env(tmp_path_factory):
    d = tmp_path_factory.mktemp("tls")
    ca_key, ca = d / "ca.key", d / "ca.pem"
    srv_key, srv_csr, srv = d / "srv.key", d / "srv.csr", d / "srv.pem"
    ext = d / "ext.cnf"
    ext.write_text(
        "subjectAltName=IP:127.0.0.1,DNS:localhost\n"
        "basicConstraints=CA:FALSE\n"
        "keyUsage=critical,digitalSignature,keyEncipherment\n"
        "extendedKeyUsage=serverAuth\n"
    )

    _run([OPENSSL, "req", "-x509", "-newkey", "rsa:2048", "-nodes",
          "-keyout", str(ca_key), "-out", str(ca), "-days", "1", "-subj", "/CN=TestCA",
          "-addext", "basicConstraints=critical,CA:TRUE",
          "-addext", "keyUsage=critical,keyCertSign,cRLSign"])
    _run([OPENSSL, "req", "-newkey", "rsa:2048", "-nodes",
          "-keyout", str(srv_key), "-out", str(srv_csr), "-subj", "/CN=localhost"])
    _run([OPENSSL, "x509", "-req", "-in", str(srv_csr), "-CA", str(ca), "-CAkey", str(ca_key),
          "-CAcreateserial", "-out", str(srv), "-days", "1", "-extfile", str(ext)])

    # A second, unrelated CA to prove verification actually happens.
    other_ca, other_key = d / "other_ca.pem", d / "other_ca.key"
    _run([OPENSSL, "req", "-x509", "-newkey", "rsa:2048", "-nodes",
          "-keyout", str(other_key), "-out", str(other_ca), "-days", "1", "-subj", "/CN=OtherCA",
          "-addext", "basicConstraints=critical,CA:TRUE",
          "-addext", "keyUsage=critical,keyCertSign,cRLSign"])

    return {"ca": str(ca), "other_ca": str(other_ca), "cert": str(srv), "key": str(srv_key)}


@pytest.fixture()
def tls_server(tls_env):
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')

        def log_message(self, *args):
            pass

    httpd = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(tls_env["cert"], tls_env["key"])
    httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)

    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"https://127.0.0.1:{httpd.server_address[1]}"
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_verify_with_correct_ca_succeeds(tls_server, tls_env):
    with httpx.Client(verify=tls_env["ca"]) as client:
        response = client.get(tls_server + "/health")
    assert response.status_code == 200


def test_verify_with_wrong_ca_fails(tls_server, tls_env):
    with httpx.Client(verify=tls_env["other_ca"]) as client:
        with pytest.raises(httpx.ConnectError):
            client.get(tls_server + "/health")


def test_no_unverified_connection(tls_server):
    # Default verification must reject the self-signed server: no unverified TLS.
    with httpx.Client() as client:
        with pytest.raises(httpx.ConnectError):
            client.get(tls_server + "/health")


@pytest.fixture(scope="module")
def mismatch_env(tmp_path_factory):
    """A CA and a server certificate valid only for a name the client won't use.

    The certificate's SAN is ``other.example`` while the client connects to
    ``127.0.0.1``, so hostname verification must fail unless it is skipped.
    """
    d = tmp_path_factory.mktemp("tls-mismatch")
    ca_key, ca = d / "ca.key", d / "ca.pem"
    srv_key, srv_csr, srv = d / "srv.key", d / "srv.csr", d / "srv.pem"
    ext = d / "ext.cnf"
    ext.write_text(
        "subjectAltName=DNS:other.example\n"
        "basicConstraints=CA:FALSE\n"
        "keyUsage=critical,digitalSignature,keyEncipherment\n"
        "extendedKeyUsage=serverAuth\n"
    )

    _run([OPENSSL, "req", "-x509", "-newkey", "rsa:2048", "-nodes",
          "-keyout", str(ca_key), "-out", str(ca), "-days", "1", "-subj", "/CN=TestCA",
          "-addext", "basicConstraints=critical,CA:TRUE",
          "-addext", "keyUsage=critical,keyCertSign,cRLSign"])
    _run([OPENSSL, "req", "-newkey", "rsa:2048", "-nodes",
          "-keyout", str(srv_key), "-out", str(srv_csr), "-subj", "/CN=other.example"])
    _run([OPENSSL, "x509", "-req", "-in", str(srv_csr), "-CA", str(ca), "-CAkey", str(ca_key),
          "-CAcreateserial", "-out", str(srv), "-days", "1", "-extfile", str(ext)])

    return {"ca": str(ca), "cert": str(srv), "key": str(srv_key)}


@pytest.fixture()
def mismatch_server(mismatch_env):
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')

        def log_message(self, *args):
            pass

    httpd = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(mismatch_env["cert"], mismatch_env["key"])
    httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)

    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"https://127.0.0.1:{httpd.server_address[1]}"
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_hostname_mismatch_rejected_by_default(mismatch_server, mismatch_env):
    client = server.Mem0Client(
        host=None, https_host=mismatch_server, cert_path=mismatch_env["ca"]
    )
    with pytest.raises(httpx.ConnectError):
        asyncio.run(client.get_status())


def test_hostname_mismatch_allowed_when_verification_disabled(mismatch_server, mismatch_env):
    client = server.Mem0Client(
        host=None,
        https_host=mismatch_server,
        cert_path=mismatch_env["ca"],
        tls_verify_hostname=False,
    )
    result = asyncio.run(client.get_status())
    assert result["status"] == "ok"
