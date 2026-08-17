#!/bin/bash

echo "=================================================="
echo "🚀 Starting BChainCA Simple Network"
echo "=================================================="
echo ""
echo "This uses a simplified Docker setup with Devmode"
echo "consensus instead of PoET (easier for development)"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running!"
    echo "   Please start Docker Desktop and try again."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Navigate to the project directory
cd "$(dirname "$0")"

echo "📦 Pulling Docker images..."
echo ""

# Pull images first
docker pull hyperledger/sawtooth-validator:chime
docker pull hyperledger/sawtooth-settings-tp:chime
docker pull hyperledger/sawtooth-rest-api:chime
docker pull hyperledger/sawtooth-shell:chime
docker pull hyperledger/sawtooth-devmode-engine-rust:chime

echo ""
echo "📦 Starting services..."
echo ""

# Start the services
docker-compose -f docker-compose-simple.yaml up -d

if [ $? -eq 0 ]; then
    echo ""
    echo "=================================================="
    echo "✅ Simple network started successfully!"
    echo "=================================================="
    echo ""
    echo "📊 Service Status:"
    docker-compose -f docker-compose-simple.yaml ps
    echo ""
    echo "🌐 Endpoints:"
    echo "   REST API:   http://localhost:8008"
    echo "   Validator:  tcp://localhost:4004"
    echo ""
    echo "📝 View Logs:"
    echo "   docker-compose -f docker-compose-simple.yaml logs -f"
    echo ""
    echo "🛑 Stop Network:"
    echo "   docker-compose -f docker-compose-simple.yaml down"
    echo ""
    echo "=================================================="
    echo ""
    echo "⏳ Waiting for services to be ready..."
    echo "   (This may take 30-60 seconds)"
    echo ""

    # Wait for REST API to be ready
    for i in {1..30}; do
        if curl -s http://localhost:8008/blocks > /dev/null 2>&1; then
            echo ""
            echo "✅ REST API is ready!"
            echo ""
            echo "🎉 Blockchain network is running!"
            echo ""
            echo "Next steps:"
            echo "   1. Start the UI: ./START_UI.sh"
            echo "   2. Open http://localhost:4200"
            echo "   3. Login with: admin / admin123"
            echo ""
            break
        fi
        echo -n "."
        sleep 2
    done
    echo ""
else
    echo ""
    echo "❌ Error: Failed to start network"
    echo "   Check Docker logs for details:"
    echo "   docker-compose -f docker-compose-simple.yaml logs"
    echo ""
    echo "   See DOCKER_SETUP_GUIDE.md for troubleshooting"
    exit 1
fi
