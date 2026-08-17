# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
