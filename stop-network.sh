#!/bin/bash

echo "=================================================="
echo "🛑 Stopping BChainCA Blockchain Network"
echo "=================================================="
echo ""

cd "$(dirname "$0")"

echo "Stopping boot node services..."
docker-compose -f docker-compose-boot-node.yaml down

echo ""
echo "✅ Network stopped successfully!"
echo ""
echo "To start again: ./start-network.sh"
echo ""
