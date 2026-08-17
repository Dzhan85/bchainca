# Docker Setup Guide - BChainCA

## ⚠️ Docker Compose Startup Issues

The Docker Compose setup encountered an error pulling Hyperledger Sawtooth images. Here's how to resolve it:

## 🔧 Solutions

### Option 1: Retry with Better Network Connection

```bash
# Retry pulling images with more attempts
./start-network.sh
```

If you see network errors (EOF), this could be:
- Docker Hub rate limiting
- Temporary network issues
- Firewall blocking Docker Hub

**Solution:**
1. Wait a few minutes and retry
2. Check your internet connection
3. Restart Docker Desktop
4. Try again: `./start-network.sh`

### Option 2: Pull Images Manually

```bash
# Pull required Sawtooth images manually
docker pull hyperledger/sawtooth-validator:1.1
docker pull hyperledger/sawtooth-rest-api:1.1
docker pull hyperledger/sawtooth-settings-tp:1.1
docker pull hyperledger/sawtooth-identity-tp:latest
docker pull hyperledger/sawtooth-poet-engine:1.1
docker pull hyperledger/sawtooth-poet-validator-registry-tp:1.1
docker pull hyperledger/sawtooth-all:1.1
docker pull ubuntu:16.04

# Then start the network
./start-network.sh
```

### Option 3: Use Newer Sawtooth Version

The current setup uses Sawtooth 1.1 (from 2018). Consider updating to a newer version:

```bash
# Check available Sawtooth versions
docker search hyperledger/sawtooth
```

### Option 4: Run Without Docker (Development Mode)

For development and testing the UI, you can:

1. **Start just the UI** (works without blockchain):
   ```bash
   ./START_UI.sh
   ```

2. **Use Mock Data**: The UI will show "Offline" status but you can still test the login and interface

3. **Connect to Remote Sawtooth**: If you have a Sawtooth instance running elsewhere, update the API URL in:
   ```
   src/environments/environment.ts
   ```

### Option 5: Simplified Docker Setup

Create a minimal setup for testing:

```yaml
# docker-compose-simple.yaml
version: "3"

services:
  rest-api:
    image: hyperledger/sawtooth-rest-api:latest
    container_name: sawtooth-rest-api
    ports:
      - "8008:8008"
    command: sawtooth-rest-api -v --connect tcp://validator:4004 --bind rest-api:8008
    depends_on:
      - validator

  validator:
    image: hyperledger/sawtooth-validator:latest
    container_name: sawtooth-validator
    ports:
      - "4004:4004"
    command: |
      bash -c "
        if [ ! -f /etc/sawtooth/keys/validator.priv ]; then
          sawadm keygen &&
          sawtooth keygen my_key &&
          sawset genesis -k /root/.sawtooth/keys/my_key.priv &&
          sawset proposal create \
            -k /root/.sawtooth/keys/my_key.priv \
            sawtooth.consensus.algorithm.name=Devmode \
            sawtooth.consensus.algorithm.version=0.1 \
            -o config.batch &&
          sawadm genesis config-genesis.batch config.batch
        fi;
        sawtooth-validator -v \
          --endpoint tcp://validator:8800 \
          --bind component:tcp://eth0:4004 \
          --bind network:tcp://eth0:8800 \
          --bind consensus:tcp://eth0:5050
      "

  settings-tp:
    image: hyperledger/sawtooth-settings-tp:latest
    container_name: sawtooth-settings-tp
    depends_on:
      - validator
    command: settings-tp -v -C tcp://validator:4004

  devmode-engine:
    image: hyperledger/sawtooth-devmode-engine-rust:latest
    container_name: sawtooth-devmode-engine
    depends_on:
      - validator
    command: devmode-engine-rust -C tcp://validator:5050
```

Then start with:
```bash
docker-compose -f docker-compose-simple.yaml up -d
```

## 🐛 Troubleshooting

### Check Docker Status

```bash
# Check if Docker is running
docker info

# Check Docker Hub connectivity
docker pull hello-world

# View Docker logs
docker-compose -f docker-compose-boot-node.yaml logs
```

### Network Issues

```bash
# Restart Docker Desktop
# (via Docker Desktop menu)

# Clear Docker cache
docker system prune -a

# Check DNS
ping registry-1.docker.io
```

### Image Not Found

If images are not found, they may have been:
- Deprecated (Sawtooth 1.1 is from 2018)
- Moved to a different registry
- Renamed

**Solution**: Update to latest Sawtooth images or use alternative consensus (Devmode instead of PoET).

## 🚀 Quick Start (UI Only)

If you just want to test the UI without the blockchain:

```bash
# Start only the UI
./START_UI.sh

# Open browser
open http://localhost:4200

# Login with demo account
# Username: admin
# Password: admin123
```

The dashboard will show "Offline" for network status, but you can still:
- ✅ Test login functionality
- ✅ Navigate the interface
- ✅ View the dashboard layout
- ✅ Test responsive design

## 📚 Additional Resources

- **Hyperledger Sawtooth Docs**: https://sawtooth.hyperledger.org/docs/
- **Docker Documentation**: https://docs.docker.com/
- **Sawtooth Docker Images**: https://hub.docker.com/u/hyperledger

## 🔄 Alternative: Python Client Only

You can also run just the Python client without Docker:

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run the Python client (if you have a Sawtooth instance)
python sawtooth_client.py --help
```

## ✅ Next Steps

Once Docker is working:

1. ✅ Pull Docker images successfully
2. ✅ Start the blockchain network
3. ✅ Start the UI: `./START_UI.sh`
4. ✅ Access at http://localhost:4200
5. ✅ Login and explore!

---

**Need Help?**
- Check network connectivity to Docker Hub
- Try simplified Docker setup (Option 5)
- Run UI only without blockchain (Option 4)
- Check Docker Desktop logs
