# Tasks

## 1. Environment-variable mapping

- [x] 1.1 In `load_config`, add `MEM0_HOST_HTTPS` → `mem0_host_https`, `MEM0_CERT_PATH` → `cert_path`, and `MEM0_TLS_VERIFY_HOSTNAME` → `tls_verify_hostname` to the environment mapping. Verify with a `tests/test_config.py` case that sets only these env vars (no config file) and asserts the HTTPS endpoint and CA path are configured.
- [x] 1.2 Ensure `MEM0_TLS_VERIFY_HOSTNAME` is parsed with the existing boolean normalizer so `false`/`true` (case-insensitive) behave like the config-file value. Verify a test asserts `MEM0_TLS_VERIFY_HOSTNAME=false` yields hostname verification disabled while chain verification remains required.
- [x] 1.3 Confirm precedence: an environment value overrides the config file, and an unset variable leaves the file/default value in place. Verify a test covering both directions.

## 2. HTTPS validation and user documentation

- [x] 2.1 Confirm startup validation still fires when `MEM0_HOST_HTTPS` is set but no `cert_path` is supplied by the file or `MEM0_CERT_PATH`. Verify a test asserts the clear error is raised.
- [x] 2.2 Update `README.md` to document `MEM0_HOST_HTTPS`, `MEM0_CERT_PATH`, and `MEM0_TLS_VERIFY_HOSTNAME`, state that environment variables override the configuration file, and remove the note that these options are configuration-file only. Verify the documented names and precedence match the code and the `hub-connection` spec.

## 3. Integration checks

- [x] 3.1 Run `python3 -m pytest tests/ -q` and `openspec validate "pass-all-hub-options-via-env"`; both must pass.
- [x] 3.2 Env-only real-hub smoke test: with no `--config` file, set `MEM0_HOST_HTTPS`, `MEM0_CERT_PATH`, `MEM0_TLS_VERIFY_HOSTNAME=false`, and `MEM0_API_KEY`, then confirm add/search/list/get/delete all succeed (no 401). Verify the observed behavior.

## Workflow follow-up

- Archive the change with `/opsx-archive` after review so the `hub-connection` delta merges into `openspec/specs/`.
- Verify the archived spec at `openspec/specs/hub-connection/spec.md` no longer contains the "configuration-file only" requirement.
- This change is the prerequisite for `package-server-and-opencode-adapter`; complete it first.
