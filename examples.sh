#!/bin/bash
# Example API requests for CCPA Compliance Detection System

echo "CCPA Compliance Detection System - Example Requests"
echo "===================================================="
echo ""

# Health check
echo "1. Health Check:"
curl -s http://localhost:8000/health | jq .
echo ""
echo ""

# Example 1: No violation
echo "2. No Violation:"
curl -s -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "We provide clear privacy notices and honor all user requests"}' | jq .
echo ""
echo ""

# Example 2: Notice violation
echo "3. Notice Violation (1798.100):"
curl -s -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "We collect user data without informing them"}' | jq .
echo ""
echo ""

# Example 3: Deletion violation
echo "4. Deletion Violation (1798.105):"
curl -s -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "We refuse to delete user data when requested"}' | jq .
echo ""
echo ""

# Example 4: Discrimination violation
echo "5. Discrimination Violation (1798.125):"
curl -s -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "We charge higher prices to users who opt out"}' | jq .
echo ""
echo ""

# Example 5: Multiple violations
echo "6. Multiple Violations:"
curl -s -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "We sell user data without notice and ignore deletion requests"}' | jq .
echo ""
echo ""

# Example 6: Minor protection
echo "7. Minor Protection (1798.121):"
curl -s -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "We sell personal data of users under 16 years old"}' | jq .
echo ""
echo ""

# Example 7: Do Not Sell link
echo "8. Do Not Sell Link (1798.135):"
curl -s -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Our website has no Do Not Sell link"}' | jq .
echo ""
echo ""

echo "===================================================="
echo "All examples completed!"
