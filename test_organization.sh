#!/bin/bash

# Define the API endpoint
API_URL="http://localhost:8000/api/meetings/organizations"

# Make the curl request
echo "Fetching organizations from $API_URL..."
curl -X GET "$API_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -v 2>&1 | grep "^<\|^*\|^}\|^{\|error\|Error"

echo -e "\nRequest completed."
