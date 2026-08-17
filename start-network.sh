#!/bin/bash

echo "=================================================="
echo "🚀 Starting BChainCA Blockchain Network"
echo "=================================================="
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

echo "📦 Building and starting boot node..."
echo ""

# Start the boot node
docker-compose -f docker-compose-boot-node.yaml up -d --build

if [ $? -eq 0 ]; then
    echo ""
    echo "=================================================="
    echo "✅ Boot node started successfully!"
    echo "=================================================="
    echo ""
    echo "📊 Service Status:"
    docker-compose -f docker-compose-boot-node.yaml ps
    echo ""
    echo "🌐 Endpoints:"
    echo "   REST API:   http://localhost:8008"
    echo "   Validator:  tcp://localhost:4004"
    echo ""
    echo "📝 View Logs:"
    echo "   docker-compose -f docker-compose-boot-node.yaml logs -f"
    echo ""
    echo "🛑 Stop Network:"
    echo "   docker-compose -f docker-compose-boot-node.yaml down"
    echo ""
    echo "=================================================="
    echo ""
    echo "⏳ Waiting for services to be ready..."
    echo "   (This may take 30-60 seconds)"
    echo ""

    # Wait for REST API to be ready
    for i in {1..30}; do
        if curl -s http://localhost:8008/blocks > /dev/null 2>&1; then
            echo "✅ REST API is ready!"
            echo ""
            echo "🎉 Blockchain network is running!"
            echo ""
            echo "Next steps:"
            echo "   1. Start the UI: ./START_UI.sh"
            echo "   2. Open http://localhost:4200"
            echo "   3. Login with: admin / admin123"
            break
        fi
        echo -n "."
        sleep 2
    done
    echo ""
else
    echo ""
    echo "❌ Error: Failed to start boot node"
    echo "   Check Docker logs for details:"
    echo "   docker-compose -f docker-compose-boot-node.yaml logs"
    exit 1
fi
