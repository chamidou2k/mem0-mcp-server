"""Configuration behavior for the hub HTTP/HTTPS endpoints.

Covers the `hub-connection` spec scenarios: legacy HTTP-only configs, endpoint
resolution, `cert_path` validation, and environment-variable overrides.
"""

import json
import ssl

import certifi
import pytest

import mem0_mcp_server as server


def write_config(tmp_path, data):
    path = tmp_path / "config.json"
    path.write_text(json.dumps(data))
    return str(path)


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for key in ("MEM0_HOST", "MEM0_HOST_HTTPS", "MEM0_CERT_PATH", "MEM0_TLS_VERIFY_HOSTNAME"):
        monkeypatch.delenv(key, raising=False)


def test_legacy_config_http_only(tmp_path):
    config = server.load_config(
        write_config(tmp_path, {"mem0_host": "http://192.168.1.100:8001"})
    )
    assert config["mem0_host"] == "http://192.168.1.100:8001"
    assert config["mem0_host_https"] is None
    assert config["cert_path"] is None


def test_scheme_less_host_defaults_to_http(tmp_path):
    config = server.load_config(write_config(tmp_path, {"mem0_host": "192.168.1.100:8001"}))
    assert config["mem0_host"] == "http://192.168.1.100:8001"


def test_no_http_host_has_no_builtin_default(tmp_path):
    # The old hardcoded default is gone: an empty config means "not configured".
    config = server.load_config(write_config(tmp_path, {}))
    assert config["mem0_host"] is None
    assert config["mem0_host_https"] is None


def test_empty_string_hosts_treated_as_unset(tmp_path):
    config = server.load_config(
        write_config(tmp_path, {"mem0_host": "", "mem0_host_https": ""})
    )
    assert config["mem0_host"] is None
    assert config["mem0_host_https"] is None


def test_whitespace_hosts_treated_as_unset(tmp_path):
    config = server.load_config(
        write_config(tmp_path, {"mem0_host": "   ", "mem0_host_https": "\t "})
    )
    assert config["mem0_host"] is None
    assert config["mem0_host_https"] is None


def test_https_only_config_resolves(tmp_path):
    cert = tmp_path / "ca.pem"
    cert.write_text("dummy-ca")
    config = server.load_config(
        write_config(
            tmp_path,
            {"mem0_host": "", "mem0_host_https": "hub:8443", "cert_path": str(cert)},
        )
    )
    assert config["mem0_host"] is None
    assert config["mem0_host_https"] == "https://hub:8443"
    assert config["cert_path"] == str(cert)


def test_env_empty_http_host_treated_as_unset(tmp_path, monkeypatch):
    monkeypatch.setenv("MEM0_HOST", "")
    config = server.load_config(write_config(tmp_path, {"mem0_host": "http://hub:8001"}))
    assert config["mem0_host"] is None


def test_both_endpoints_resolved(tmp_path):
    cert = tmp_path / "ca.pem"
    cert.write_text("dummy-ca")
    config = server.load_config(
        write_config(
            tmp_path,
            {
                "mem0_host": "http://hub:8001",
                "mem0_host_https": "hub:8443",
                "cert_path": str(cert),
            },
        )
    )
    assert config["mem0_host"] == "http://hub:8001"
    assert config["mem0_host_https"] == "https://hub:8443"
    assert config["cert_path"] == str(cert)


def test_https_endpoint_keeps_explicit_scheme(tmp_path):
    cert = tmp_path / "ca.pem"
    cert.write_text("dummy-ca")
    config = server.load_config(
        write_config(
            tmp_path,
            {
                "mem0_host": "http://hub:8001",
                "mem0_host_https": "https://hub:8443/",
                "cert_path": str(cert),
            },
        )
    )
    assert config["mem0_host_https"] == "https://hub:8443"


def test_https_without_cert_path_fails(tmp_path):
    with pytest.raises(ValueError, match="cert_path is required"):
        server.load_config(write_config(tmp_path, {"mem0_host_https": "https://hub:8443"}))


def test_https_with_missing_cert_file_fails(tmp_path):
    missing = tmp_path / "nope.pem"
    with pytest.raises(ValueError, match="does not exist or is not readable"):
        server.load_config(
            write_config(
                tmp_path,
                {"mem0_host_https": "https://hub:8443", "cert_path": str(missing)},
            )
        )


def test_https_with_non_file_cert_path_fails(tmp_path):
    with pytest.raises(ValueError, match="does not exist or is not readable"):
        server.load_config(
            write_config(
                tmp_path,
                {"mem0_host_https": "https://hub:8443", "cert_path": str(tmp_path)},
            )
        )


def test_env_vars_configure_https_endpoint_and_ca(tmp_path, monkeypatch):
    cert = tmp_path / "ca.pem"
    cert.write_text("dummy-ca")
    monkeypatch.setenv("MEM0_HOST_HTTPS", "https://env:8443")
    monkeypatch.setenv("MEM0_CERT_PATH", str(cert))
    config = server.load_config(write_config(tmp_path, {"mem0_host": "http://hub:8001"}))
    assert config["mem0_host"] == "http://hub:8001"
    assert config["mem0_host_https"] == "https://env:8443"
    assert config["cert_path"] == str(cert)


def test_env_vars_alone_configure_https_without_config_file(tmp_path, monkeypatch):
    cert = tmp_path / "ca.pem"
    cert.write_text("dummy-ca")
    monkeypatch.setenv("MEM0_HOST_HTTPS", "https://env:8443")
    monkeypatch.setenv("MEM0_CERT_PATH", str(cert))
    config = server.load_config(None)
    assert config["mem0_host_https"] == "https://env:8443"
    assert config["cert_path"] == str(cert)


def test_env_https_overrides_config_file(tmp_path, monkeypatch):
    cert = tmp_path / "ca.pem"
    cert.write_text("dummy-ca")
    monkeypatch.setenv("MEM0_HOST_HTTPS", "https://env:8443")
    config = server.load_config(
        write_config(
            tmp_path,
            {"mem0_host_https": "https://file:8443", "cert_path": str(cert)},
        )
    )
    assert config["mem0_host_https"] == "https://env:8443"


def test_unset_https_env_keeps_config_file_value(tmp_path):
    cert = tmp_path / "ca.pem"
    cert.write_text("dummy-ca")
    config = server.load_config(
        write_config(
            tmp_path,
            {"mem0_host_https": "https://file:8443", "cert_path": str(cert)},
        )
    )
    assert config["mem0_host_https"] == "https://file:8443"
    assert config["cert_path"] == str(cert)


def test_https_env_without_cert_path_fails(tmp_path, monkeypatch):
    monkeypatch.setenv("MEM0_HOST_HTTPS", "https://env:8443")
    with pytest.raises(ValueError, match="cert_path is required"):
        server.load_config(write_config(tmp_path, {}))


def test_env_cert_path_satisfies_https_requirement(tmp_path, monkeypatch):
    cert = tmp_path / "ca.pem"
    cert.write_text("dummy-ca")
    monkeypatch.setenv("MEM0_HOST_HTTPS", "https://env:8443")
    monkeypatch.setenv("MEM0_CERT_PATH", str(cert))
    config = server.load_config(write_config(tmp_path, {}))
    assert config["cert_path"] == str(cert)


def test_env_var_still_overrides_http_host(tmp_path, monkeypatch):
    monkeypatch.setenv("MEM0_HOST", "http://env-host:9000")
    config = server.load_config(write_config(tmp_path, {"mem0_host": "http://file-host:8001"}))
    assert config["mem0_host"] == "http://env-host:9000"


def test_tls_verify_hostname_defaults_true(tmp_path):
    config = server.load_config(write_config(tmp_path, {}))
    assert config["tls_verify_hostname"] is True


def test_tls_verify_hostname_explicit_false(tmp_path):
    config = server.load_config(write_config(tmp_path, {"tls_verify_hostname": False}))
    assert config["tls_verify_hostname"] is False


def test_tls_verify_hostname_string_false(tmp_path):
    config = server.load_config(write_config(tmp_path, {"tls_verify_hostname": "false"}))
    assert config["tls_verify_hostname"] is False


def test_env_var_sets_tls_verify_hostname(tmp_path, monkeypatch):
    monkeypatch.setenv("MEM0_TLS_VERIFY_HOSTNAME", "false")
    config = server.load_config(write_config(tmp_path, {}))
    assert config["tls_verify_hostname"] is False


def test_env_var_tls_verify_hostname_is_case_insensitive(tmp_path, monkeypatch):
    monkeypatch.setenv("MEM0_TLS_VERIFY_HOSTNAME", "FALSE")
    config = server.load_config(write_config(tmp_path, {}))
    assert config["tls_verify_hostname"] is False


def test_env_var_tls_verify_hostname_overrides_file_false(tmp_path, monkeypatch):
    monkeypatch.setenv("MEM0_TLS_VERIFY_HOSTNAME", "true")
    config = server.load_config(write_config(tmp_path, {"tls_verify_hostname": False}))
    assert config["tls_verify_hostname"] is True


def test_env_skip_hostname_keeps_chain_verification(monkeypatch):
    monkeypatch.setenv("MEM0_HOST_HTTPS", "https://hub:8443")
    monkeypatch.setenv("MEM0_CERT_PATH", certifi.where())
    monkeypatch.setenv("MEM0_TLS_VERIFY_HOSTNAME", "false")
    config = server.load_config(None)
    client = server.Mem0Client(
        host=None,
        https_host=config["mem0_host_https"],
        cert_path=config["cert_path"],
        tls_verify_hostname=config["tls_verify_hostname"],
    )
    ctx = client.https_client._transport._pool._ssl_context
    assert ctx.check_hostname is False
    assert ctx.verify_mode == ssl.CERT_REQUIRED
