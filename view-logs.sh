#!/bin/bash

echo "=================================================="
echo "📝 Viewing BChainCA Network Logs"
echo "=================================================="
echo ""
echo "Press Ctrl+C to exit"
echo ""

cd "$(dirname "$0")"

docker-compose -f docker-compose-boot-node.yaml logs -f
