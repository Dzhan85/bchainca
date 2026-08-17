#!/bin/bash

echo "=================================================="
echo "🚀 Starting BChainCA UI"
echo "=================================================="
echo ""

echo "📦 Checking dependencies..."
if [ ! -d "node_modules" ]; then
    echo "⚠️  Node modules not found. Installing..."
    npm install
else
    echo "✅ Dependencies already installed"
fi

echo ""
echo "🌐 Starting Angular development server..."
echo ""
echo "📌 Application will be available at:"
echo "   http://localhost:4200"
echo ""
echo "🔐 Demo Accounts:"
echo "   Admin:    admin / admin123"
echo "   User:     user / user123"
echo "   Operator: operator / operator123"
echo ""
echo "=================================================="
echo ""

npm start
