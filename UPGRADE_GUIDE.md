# Upgrade Guide: v1.x to v2.0.0

This guide will help you upgrade from version 1.x to 2.0.0, which includes critical security updates and breaking changes.

## ⚠️ Breaking Changes

### 1. Node.js Version Requirement
- **Old**: Node.js 6.x
- **New**: Node.js 20.x LTS (minimum 18.x)

**Action Required:**
```bash
# Install Node.js 20 LTS
# macOS (using nvm)
nvm install 20
nvm use 20

# Or use official installer from nodejs.org
```

### 2. Angular Version
- **Old**: Angular 5.0.1
- **New**: Angular 18.2.0

**Action Required:**
The Angular upgrade may require code changes if you have custom components:
- Update component decorators
- Update routing if customized
- Update any custom Angular modules

### 3. Serialization Format (CaState.py)
- **Old**: Pickle-based serialization
- **New**: JSON-based serialization

**Action Required:**
⚠️ **IMPORTANT**: Existing blockchain state using pickle format will need migration!

```python
# Migration script (run once)
# If you have existing data, you'll need to:
# 1. Export existing certificates using old code
# 2. Re-import them using new code
# Or reset the blockchain state (only if acceptable)
```

### 4. Docker Compose Command Execution
- **Old**: Uses `os.system()` (insecure)
- **New**: Uses `subprocess.run()` (secure)

**Action Required:**
No changes needed - this is an internal improvement.

## 📋 Upgrade Steps

### Step 1: Backup Current Installation
```bash
# Backup your data
cp -r bchainca bchainca-backup-$(date +%Y%m%d)

# Export any critical blockchain state
# (Custom script may be needed based on your deployment)
```

### Step 2: Update Node.js and Python
```bash
# Verify Node.js version
node --version  # Should be 20.x or higher

# Verify Python version
python --version  # Should be 3.8 or higher
```

### Step 3: Update Dependencies

#### Python Dependencies
```bash
# Install updated Python packages
pip install --upgrade -r requirements.txt

# Verify no vulnerabilities
pip install pip-audit
pip-audit
```

#### Node.js Dependencies
```bash
# Remove old node_modules
rm -rf node_modules package-lock.json

# Install new dependencies
npm install

# Verify no vulnerabilities
npm audit
```

### Step 4: Rebuild Docker Images
```bash
# Remove old images
docker rmi bchainca:latest

# Rebuild with new base image
docker build -t bchainca:latest .

# Verify the image
docker run --rm bchainca:latest node --version  # Should show v20.x
```

### Step 5: Update Configuration Files

No configuration changes are required for most installations. However, review:
- Docker Compose files for any custom modifications
- Environment variables for any deprecated settings

### Step 6: Test the Upgrade

```bash
# Run tests
npm test

# Start a test network
python main.py --node_count 1 --benchmark do-nothing --load 10

# Verify frontend
npm start
# Navigate to http://localhost:4200
```

### Step 7: Deploy to Production

```bash
# Stop current services
docker-compose down

# Pull latest code
git pull origin main

# Start services with new version
docker-compose up -d --build

# Monitor logs
docker-compose logs -f
```

## 🔍 Verification Checklist

After upgrading, verify the following:

- [ ] Node.js version is 20.x or higher: `node --version`
- [ ] Python dependencies updated: `pip list | grep -E "PyYAML|requests|urllib3"`
- [ ] No npm vulnerabilities: `npm audit` shows 0 vulnerabilities
- [ ] No Python vulnerabilities: `pip-audit` shows no issues
- [ ] Docker image uses Node 20: `docker run --rm bchainca:latest node --version`
- [ ] Application starts without errors
- [ ] Can create new certificates
- [ ] Can query certificate status
- [ ] Frontend loads correctly
- [ ] All API endpoints respond correctly
- [ ] Logs show no errors or warnings

## 🐛 Troubleshooting

### Issue: npm install fails
**Solution:**
```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules and try again
rm -rf node_modules package-lock.json
npm install
```

### Issue: Python dependencies conflict
**Solution:**
```bash
# Use a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: Docker build fails
**Solution:**
```bash
# Clear Docker cache
docker system prune -a

# Rebuild without cache
docker build --no-cache -t bchainca:latest .
```

### Issue: Existing blockchain state incompatible
**Solution:**
```bash
# Option 1: Reset blockchain (DESTROYS DATA)
# Only use in development!
docker-compose down -v
docker-compose up -d

# Option 2: Migrate data
# Contact support for migration assistance
```

### Issue: Port conflicts
**Solution:**
```bash
# Check what's using the ports
lsof -i :4004
lsof -i :8008
lsof -i :4200

# Kill processes or change port configuration
```

## 🔐 Security Validation

After upgrading, run these security checks:

```bash
# Check for npm vulnerabilities
npm audit

# Check for Python vulnerabilities
pip install pip-audit
pip-audit

# Scan Docker image
docker scan bchainca:latest

# Or use Trivy
trivy image bchainca:latest
```

## 📚 Additional Resources

- [README.md](README.md) - Updated installation and usage guide
- [SECURITY.md](SECURITY.md) - Security policy and vulnerability details
- [CHANGELOG.md](CHANGELOG.md) - Complete list of changes
- [Sawtooth Documentation](https://sawtooth.hyperledger.org/docs/)

## 🆘 Getting Help

If you encounter issues during the upgrade:

1. Check the troubleshooting section above
2. Review the logs: `docker-compose logs`
3. Search existing issues in the repository
4. Create a new issue with:
   - Your Node.js version
   - Your Python version
   - Error messages
   - Steps to reproduce

## 📅 Rollback Procedure

If you need to rollback to v1.x:

```bash
# Stop current services
docker-compose down

# Restore backup
cd ..
mv bchainca bchainca-v2-failed
mv bchainca-backup-YYYYMMDD bchainca
cd bchainca

# Reinstall old dependencies
npm install
pip install -r requirements.txt

# Restart services
docker-compose up -d
```

**Note:** Rollback may not be possible if you've already created new certificates with v2.0.0 due to serialization format changes.

## ✅ Post-Upgrade Best Practices

1. **Monitor logs** for the first 24-48 hours
2. **Run security scans** regularly
3. **Keep dependencies updated** monthly
4. **Test disaster recovery** procedures
5. **Document any custom changes** you made during upgrade

---

**Need Help?** Open an issue or contact the development team.

**Last Updated:** August 17, 2026
