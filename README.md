# BChainCA - Blockchain PKI on Sawtooth

SNE RP1 Blockchain Public Key Infrastructure implementation using Hyperledger Sawtooth.

## Overview

BChainCA is a blockchain-based Public Key Infrastructure (PKI) system built on Hyperledger Sawtooth. This project provides a distributed certificate authority implementation with performance monitoring and benchmarking capabilities.

### ✨ New in Version 2.0.0

- 🔐 **Modern Authentication UI** - Secure login with username/password
- 📊 **Interactive Dashboard** - Real-time blockchain statistics and quick actions
- 🎨 **Beautiful Design** - Material Design with animated gradients
- 👤 **User Management** - Session handling with demo accounts
- 🛡️ **Protected Routes** - Secure navigation with authentication guards
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile

## Architecture

- **Frontend**: Angular 18 web application for blockchain explorer and state monitoring
- **Backend**: Python-based Sawtooth client for transaction processing
- **Blockchain**: Hyperledger Sawtooth distributed ledger
- **Orchestration**: Docker Compose for multi-node network deployment

## Security Updates (August 2026)

This project has been updated to address critical security vulnerabilities:

### Python Dependencies Fixed
- ✅ **PyYAML**: Updated from 3.11 → 6.0.1+ (fixes CVE-2017-18342 - arbitrary code execution)
- ✅ **requests**: Updated from 2.10.0 → 2.32.0+ (multiple security fixes)
- ✅ **urllib3**: Updated from 1.16 → 2.2.2+ (fixes multiple CVEs)
- ✅ **requests-unixsocket**: Updated from 0.1.5 → 0.3.0+
- ✅ **simplejson**: Updated from 3.8.2 → 3.19.2+

### Node.js Dependencies Fixed
- ✅ **Angular**: Updated from 5.0.1 → 18.2.0 (7 years of security patches)
- ✅ **crypto-js**: Updated from 3.1.9-1 → 4.2.0 (cryptographic vulnerabilities)
- ✅ **lodash**: Updated from 4.17.4 → 4.17.21 (prototype pollution fixes)
- ✅ **rxjs**: Updated from 5.5.2 → 7.8.1
- ✅ **core-js**: Updated from 2.5.1 → 3.38.0
- ✅ **TypeScript**: Updated from 2.4.2 → 5.5.4

### Infrastructure Updates
- ✅ **Dockerfile**: Updated from Node 6 (EOL 2019) → Node 20 Alpine (LTS)
- ✅ Improved Dockerfile build process and security practices

## Prerequisites

- **Docker** 20.10+ and **Docker Compose** 2.0+
- **Python** 3.8+ with pip
- **Node.js** 20+ and npm (for local development)
- **Hyperledger Sawtooth** SDK

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd bchainca
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install Node.js Dependencies
```bash
npm install
```

### 4. Build Docker Image
```bash
docker build -t bchainca:latest .
```

## Usage

### 🚀 Quick Start - Web UI

The easiest way to get started is using the web interface:

```bash
# Start the UI (includes dependency installation)
./START_UI.sh

# Or manually
npm install
npm start
```

Then open your browser to **http://localhost:4200**

#### Demo Accounts

| Username | Password | Role |
|----------|----------|------|
| `admin` | `admin123` | Administrator |
| `user` | `user123` | User |
| `operator` | `operator123` | Operator |

**Quick Login:** Click "Use" button on any demo account card on the login page.

For complete UI documentation, see:
- [UI Quick Start Guide](UI_QUICK_START.md) - Get started in 5 minutes
- [UI Documentation](UI_DOCUMENTATION.md) - Complete UI guide
- [UI Implementation Summary](UI_IMPLEMENTATION_SUMMARY.md) - Technical details

### Starting the Network

#### Multi-Node Network with Boot Node
```bash
python main.py \
  --node_count 4 \
  --boot_node docker-compose-boot-node.yaml \
  --node_template docker-compose-node.yaml \
  --benchmark small-bank \
  --load 1000
```

#### Simple Network
```bash
python main.py \
  --node_count 2 \
  --publisher_url tcp://localhost:4004 \
  --server_node_url localhost \
  --load 500 \
  --benchmark do-nothing
```

### Available Benchmarks

- **do-nothing**: Minimal transaction overhead testing
- **cpu-heavy**: CPU-intensive operations
- **io-heavy**: I/O-intensive operations
- **kv-store**: Key-value store operations
- **small-bank**: Banking transaction simulation

### Using the Sawtooth Client Directly

```bash
python sawtooth_client.py \
  --benchmark small-bank \
  --load 100 \
  --publisher localhost \
  --server localhost \
  --verbose
```

### Certificate Authority CLI

`bchainca-cli/cli.py` issues, revokes and verifies X.509 certificates on the
ledger. Commands that change state are signed with a Sawtooth key
(`~/.sawtooth/keys/<username>.priv` by default, see `--username` / `--key-dir`)
and wait for the transaction to commit (`--wait`, default 60s). Read-only
commands only need the REST API (`--url`, default `http://127.0.0.1:8008`).

```bash
cd bchainca-cli

# One-time: create the CA root certificate. The signer becomes the CA admin.
python cli.py init --username admin

# Request a certificate. Saves cert_<serial>.pem and cert_<serial>.key (mode 600).
python cli.py create alice@example.com --org-unit Research --out-dir ./certs
python cli.py create web01 --country DE --org ACME --encrypt-key

python cli.py list                          # all certificates
python cli.py status <serial>               # Valid / Revoked / Expired, owner, dates
python cli.py get <serial> -o alice.pem     # download a certificate
python cli.py ca-cert -o ca.pem             # download the CA root certificate
python cli.py verify ./certs/cert_<serial>.pem   # exit code 1 if not trustworthy

# Only the certificate owner (the key that requested it) or the CA admin may revoke.
python cli.py revoke <serial>
```

`verify` checks that the certificate is signed by the on-chain CA root,
is byte-identical to the copy on the ledger, and is neither revoked nor
expired. Issued certificates are valid for 365 days, the CA root for 10 years.

### Frontend Development

```bash
# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test

# Run end-to-end tests
npm run e2e

# Lint code
npm run lint
```

The Angular application will be available at `http://localhost:4200`

### Docker Compose

```bash
# Start boot node
docker-compose -f docker-compose-boot-node.yaml up -d

# Start additional nodes
docker-compose -f docker-compose-node.yaml up -d
```

## Command Line Arguments

### main.py Options

| Argument | Description | Default |
|----------|-------------|---------|
| `--node_count` | Number of nodes in the network | 4 |
| `--node_template` | Docker compose template for standard nodes | docker-compose-node.yaml |
| `--boot_node` | Docker compose file for boot node | None |
| `--publisher_url` | Host of the validator to subscribe to events on (port 4004) | localhost |
| `--server_node_url` | Host of the REST API to send transactions to (port 8008) | localhost |
| `--load` | Number of transactions sent to the network | 0 |
| `--benchmark` | Name of the benchmark to run | do-nothing |
| `--event_timeout` | Seconds to wait for all events after sending the load | 60 |
| `-v, --verbose` | Increase output verbosity | 0 |

## Project Structure

```
bchainca/
├── src/                      # Angular frontend source
├── bchainca-cli/            # Command-line interface tools
│   ├── cli.py              # CLI entry point
│   ├── client.py           # Client implementation
│   └── CaException.py      # Custom exceptions
├── docker/bchainca-tp/      # CA transaction processor (runs in the validator network)
├── tests/                   # Python tests (pytest)
├── lib/                     # Shared libraries
│   ├── common.py           # Common utilities
│   └── __init__.py
├── docker/                  # Docker configurations
├── e2e/                     # End-to-end tests
├── keys/                    # Cryptographic keys
├── main.py                 # Main application entry point
├── sawtooth_client.py      # Sawtooth blockchain client
├── sawtooth_subscriber.py  # Event subscriber
├── docker_starter.py       # Docker orchestration
├── docker_monitor.py       # Container CPU / memory monitoring
├── requirements.txt        # Python dependencies
├── package.json           # Node.js dependencies
└── Dockerfile             # Container build configuration
```

## Performance Monitoring

Transaction logs are automatically saved to timestamped CSV files in the monitoring folder:
- Format: `YYYY-MM-DD-{benchmark}-benchmark-requests.csv`
- Contains: timestamp and transaction status for each request

## Development

### Running Tests

```bash
# Python tests: CA transaction processor, CLI and benchmark tooling.
# They run without the Sawtooth SDK installed (it is stubbed when missing).
pip install cryptography requests requests-unixsocket colorlog python-dateutil pytest
python -m pytest tests

# Angular tests
npm test

# E2E tests
npm run e2e
```

### Code Style

```bash
# Lint Angular code
npm run lint

# Python code style (if configured)
pylint *.py
```

## Troubleshooting

### Common Issues

1. **Docker connection errors**: Ensure Docker daemon is running
2. **Port conflicts**: Check that ports 4004, 8008, and 4200 are available
3. **Dependency installation fails**: Clear npm cache with `npm cache clean --force`
4. **Permission errors**: Ensure proper file permissions on keys directory

### Logs

Check logs in the monitoring folder or use Docker logs:
```bash
docker-compose logs -f
```

## License

Apache License 2.0

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Acknowledgments

- Built on [Hyperledger Sawtooth](https://sawtooth.hyperledger.org/)
- Originally developed for SNE RP1
- Security updates performed August 2026

## Support

For issues and questions:
- Create an issue in the repository
- Check existing documentation in `/docs` (if available)
- Review Sawtooth documentation: https://sawtooth.hyperledger.org/docs/

---

**Last Updated**: August 2026  
**Version**: 2.0.0 (Security Update)
