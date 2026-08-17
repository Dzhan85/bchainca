# Quick Start Guide - BChainCA v2.0.0

## 🚀 Fast Setup (5 minutes)

### Prerequisites Check
```bash
node --version   # Need: 20.x or higher
python --version # Need: 3.8 or higher
docker --version # Need: 20.10 or higher
```

### Installation
```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install Node.js dependencies
npm install

# 3. Build Docker image
docker build -t bchainca:latest .
```

### Run Your First Network
```bash
# Start a simple 2-node network
python main.py \
  --node_count 2 \
  --benchmark do-nothing \
  --load 100
```

### Start the Frontend
```bash
# In a new terminal
npm start

# Open browser to http://localhost:4200
```

## 🔐 Security Verification

```bash
# Check for vulnerabilities (should show 0)
npm audit
pip install pip-audit && pip-audit

# Both should report NO vulnerabilities!
```

## 📚 Available Benchmarks

| Benchmark | Description | Use Case |
|-----------|-------------|----------|
| `do-nothing` | Minimal overhead | Testing infrastructure |
| `cpu-heavy` | CPU intensive | Performance testing |
| `io-heavy` | I/O intensive | Disk performance |
| `kv-store` | Key-value ops | Database simulation |
| `small-bank` | Banking transactions | Real-world simulation |

## 🎯 Common Commands

```bash
# Run with custom load
python main.py --load 1000 --benchmark small-bank

# Run with verbose logging
python main.py -vv --node_count 4

# Build for production
npm run build

# Run tests
npm test

# Clean up Docker
docker-compose down -v
```

## 🆘 Troubleshooting

### Port Already in Use?
```bash
# Check what's using the port
lsof -i :4004
lsof -i :8008
lsof -i :4200

# Kill the process or change port in config
```

### npm install fails?
```bash
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### Docker issues?
```bash
# Reset Docker
docker system prune -a
docker build --no-cache -t bchainca:latest .
```

## 📖 Documentation

- [README.md](README.md) - Full documentation
- [SECURITY.md](SECURITY.md) - Security policy
- [UPGRADE_GUIDE.md](UPGRADE_GUIDE.md) - Upgrade from v1.x
- [SECURITY_FIXES_SUMMARY.md](SECURITY_FIXES_SUMMARY.md) - What we fixed

## ✅ Success Checklist

After installation, you should be able to:
- [ ] Run `npm audit` with 0 vulnerabilities
- [ ] Run `pip-audit` with 0 vulnerabilities
- [ ] Start a blockchain network
- [ ] Access frontend at localhost:4200
- [ ] Create and revoke certificates
- [ ] View transaction logs

## 🎉 What's New in v2.0.0?

- ✅ **0 Known Vulnerabilities** (was 35+)
- ✅ **Modern Stack** (Angular 18, Node 20)
- ✅ **Secure Code** (No command injection, no pickle)
- ✅ **Better Docs** (You're reading them!)

## 🔄 Keeping Secure

```bash
# Run monthly security checks
npm audit
pip-audit

# Update dependencies quarterly
npm update
pip install --upgrade -r requirements.txt
```

## 🎓 Learn More

- **Sawtooth Docs**: https://sawtooth.hyperledger.org/docs/
- **Angular Docs**: https://angular.io/docs
- **Docker Docs**: https://docs.docker.com/

---

**Need help?** Open an issue or check the full [README.md](README.md)
