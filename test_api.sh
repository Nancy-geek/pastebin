#!/bin/bash

# Test script for Pastebin API

API_URL="http://localhost:8000"

echo "Testing Pastebin API..."
echo ""

# Test health check
echo "1. Testing health check..."
curl -s "${API_URL}/api/healthz" | python3 -m json.tool
echo ""

# Test create paste
echo "2. Creating a paste..."
RESPONSE=$(curl -s -X POST "${API_URL}/api/pastes" \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello World!", "ttl_seconds": 3600, "max_views": 5}')
echo $RESPONSE | python3 -m json.tool
PASTE_ID=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)
echo ""

if [ -n "$PASTE_ID" ]; then
  echo "3. Fetching paste ${PASTE_ID}..."
  curl -s "${API_URL}/api/pastes/${PASTE_ID}" | python3 -m json.tool
  echo ""
  
  echo "4. HTML view available at: ${API_URL}/p/${PASTE_ID}"
fi

echo ""
echo "Tests completed!"
