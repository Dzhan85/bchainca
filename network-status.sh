#!/bin/bash

echo "=================================================="
echo "📊 BChainCA Network Status"
echo "=================================================="
echo ""

cd "$(dirname "$0")"

echo "🐳 Docker Containers:"
echo "---"
docker-compose -f docker-compose-boot-node.yaml ps
echo ""

echo "🌐 Network Connectivity:"
echo "---"
if curl -s http://localhost:8008/blocks > /dev/null 2>&1; then
    echo "✅ REST API (port 8008): ONLINE"

    # Get block count
    BLOCK_COUNT=$(curl -s http://localhost:8008/blocks | grep -o '"block_num":"[^"]*"' | wc -l)
    echo "📦 Blocks: $BLOCK_COUNT"
else
    echo "❌ REST API (port 8008): OFFLINE"
fi

if nc -z localhost 4004 2>/dev/null; then
    echo "✅ Validator (port 4004): ONLINE"
else
    echo "❌ Validator (port 4004): OFFLINE"
fi

echo ""
echo "=================================================="
echo ""
echo "Commands:"
echo "  View logs:   ./view-logs.sh"
echo "  Stop network: ./stop-network.sh"
echo "  Start UI:     ./START_UI.sh"
echo ""
