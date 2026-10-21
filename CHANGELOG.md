# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- CLI `list`, `status`, `get`, `ca-cert` and `verify` commands. They read global
  state through the REST API, so they no longer send a transaction or need
  access to the validator's ZMQ port.
- `verify` checks a certificate file against the on-chain CA root and record
  (signature, ledger copy, revocation, expiry) and exits with status 1 on failure.
- `create` saves the generated private key (`cert_<serial>.key`, mode 600,
  optionally encrypted with `--encrypt-key`) and accepts subject options
  (`--country`, `--state`, `--locality`, `--org`, `--org-unit`, `--email`).
- Certificate ownership: the transaction processor records the requester's
  public key, and only the owner or the CA admin (the `init` signer) may revoke.
- Certificates report `Expired` once their validity has passed.
- X.509 extensions: BasicConstraints, KeyUsage, Subject/Authority Key Identifier.
- Python test suite in `tests/` (`python -m pytest tests`).

### Changed
- Issued certificates are valid for 365 days (was 1 minute); the CA root for
  3650 days (was 10 days).
- `create`/`revoke`/`init` wait for the commit by default (`--wait 60`) and
  report the validator's reason when a transaction is rejected.
- `init` fails if the CA is already initialized instead of silently doing nothing.
- `create` writes `cert_<serial>.pem` instead of `certificate.pem`.
- Event attribute `serial` is now decimal, matching the certificate and state key.
- `main.py` defaults now produce valid URLs (`localhost` instead of `tcp://...`).

### Removed
- Leftover tic-tac-toe (XO) CLI commands and the `sawtooth_xo` dependency.
- `pathlib` backport from requirements.txt.

### Fixed
- `create` always failed after the pickle-to-JSON change: PEM bytes are not JSON serializable.
- Certificate expiry timestamps depended on the validator's time zone, which
  could make validators compute different state.
- Transaction processor used f-strings, which the container's Python 3.5 cannot parse.
- `get`, `status` and `revoke` of an unknown serial failed with an AttributeError.
- CLI subscribed to events after submitting, so it could miss the event and hang.
- CLI ignored `--key-dir`; HTTP requests had no timeout.
- `main.py` crashed on start: restored the deleted `docker_monitor.py` and
  replaced the non-existent `SawtoothClient.subscribe()` with `SawtoothSubscriber`.
- `sawtooth_client.py` imported the private `_sha512` module, removed in Python 3.12.
- `docker_starter.py` crashed on template paths containing extra dots.
- Monitoring CSVs failed when the `logs/` folder did not exist.

## [2.0.0] - 2026-08-17

### Security
- **CRITICAL**: Fixed arbitrary code execution vulnerability in PyYAML (CVE-2017-18342)
- **CRITICAL**: Fixed command injection vulnerability in docker_starter.py
- **CRITICAL**: Replaced insecure pickle serialization with JSON in CaState.py
- **HIGH**: Fixed multiple urllib3 CVEs (CVE-2018-20060, CVE-2019-11324, CVE-2020-26137)
- **HIGH**: Fixed lodash prototype pollution vulnerabilities (CVE-2019-10744, CVE-2020-8203)
- Updated all Python dependencies to secure versions
- Updated all Node.js dependencies to secure versions
- Upgraded base Docker image from Node 6 (EOL) to Node 20 LTS Alpine

### Changed
- Updated Angular from 5.0.1 to 18.2.0 (7 years of updates)
- Updated TypeScript from 2.4.2 to 5.5.4
- Updated crypto-js from 3.1.9-1 to 4.2.0
- Updated lodash from 4.17.4 to 4.17.21
- Updated rxjs from 5.5.2 to 7.8.1
- Updated core-js from 2.5.1 to 3.38.0
- Updated PyYAML from 3.11 to 6.0.1+
- Updated requests from 2.10.0 to 2.32.0+
- Updated urllib3 from 1.16 to 2.2.2+
- Updated simplejson from 3.8.2 to 3.19.2+
- Updated requests-unixsocket from 0.1.5 to 0.3.0+
- Replaced `os.system()` with `subprocess.run()` for safer command execution
- Replaced `pickle` with `json` for secure serialization
- Improved Dockerfile with multi-stage awareness and security best practices

### Added
- Comprehensive README.md with installation and usage instructions
- SECURITY.md with vulnerability details and security guidelines
- CHANGELOG.md for tracking project changes
- .dockerignore file to prevent sensitive data in Docker images
- Detailed security documentation and best practices
- Security checklist for production deployment
- Documentation of all fixed CVEs and their impact

### Removed
- Dependency on deprecated Angular packages
- Insecure pickle-based serialization
- Unsafe os.system() calls

## [1.0.0] - 2017-XX-XX

### Added
- Initial release
- Blockchain PKI on Sawtooth implementation
- Angular frontend for blockchain explorer
- Python backend for Sawtooth integration
- Docker orchestration for multi-node networks
- Performance benchmarking capabilities
- Certificate authority functionality

[2.0.0]: https://github.com/yourrepo/bchainca/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/yourrepo/bchainca/releases/tag/v1.0.0
