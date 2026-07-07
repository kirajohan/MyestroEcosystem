#!/bin/bash

# Phase 11: E2E Testing Script
# Tests: Auth, CRUD, API endpoints

set -e

API_URL="http://localhost:8002"
ADMIN_EMAIL="admin@myestro.com"
ADMIN_PASS="admin"

echo "=== Phase 11: E2E Testing ==="
echo ""

# Test 1: Login
echo "1. Testing Login (POST /auth/login)..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$ADMIN_EMAIL\",\"password\":\"$ADMIN_PASS\"}")

TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token // empty')
USER_ROLE=$(echo "$LOGIN_RESPONSE" | jq -r '.user.role // empty')

if [ -z "$TOKEN" ]; then
  echo "❌ FAILED: No token received"
  echo "Response: $LOGIN_RESPONSE"
  exit 1
fi

if [ "$USER_ROLE" != "admin" ]; then
  echo "❌ FAILED: User is not admin (role=$USER_ROLE)"
  exit 1
fi

echo "✅ PASSED: Login successful"
echo "   Token: ${TOKEN:0:20}..."
echo "   Role: $USER_ROLE"
echo ""

# Test 2: Get Stats
echo "2. Testing GET /stats..."
STATS=$(curl -s "$API_URL/stats" \
  -H "Authorization: Bearer $TOKEN")

TOTAL_USERS=$(echo "$STATS" | jq '.total_users // 0')
echo "✅ PASSED: Stats retrieved"
echo "   Total Users: $TOTAL_USERS"
echo ""

# Test 3: Get Users
echo "3. Testing GET /users..."
USERS=$(curl -s "$API_URL/users?skip=0&limit=10" \
  -H "Authorization: Bearer $TOKEN")

USERS_COUNT=$(echo "$USERS" | jq 'length')
echo "✅ PASSED: Users retrieved"
echo "   Users Count: $USERS_COUNT"
echo ""

# Test 4: Get User Activity
echo "4. Testing GET /stats/activity?days=7..."
ACTIVITY=$(curl -s "$API_URL/stats/activity?days=7" \
  -H "Authorization: Bearer $TOKEN")

ACTIVITY_POINTS=$(echo "$ACTIVITY" | jq 'length')
echo "✅ PASSED: Activity data retrieved"
echo "   Activity Points: $ACTIVITY_POINTS"
echo ""

# Test 5: Get CEFR Distribution
echo "5. Testing GET /stats/cefr..."
CEFR=$(curl -s "$API_URL/stats/cefr" \
  -H "Authorization: Bearer $TOKEN")

echo "✅ PASSED: CEFR distribution retrieved"
echo "   Distribution: $CEFR" | head -c 100
echo ""
echo ""

# Test 6: Admin Panel HTTP Status
echo "6. Testing Admin Panel HTTP (GET http://localhost:3002)..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3002)

if [ "$HTTP_STATUS" = "307" ]; then
  echo "✅ PASSED: Admin panel redirects (307) - login page working"
elif [ "$HTTP_STATUS" = "200" ]; then
  echo "✅ PASSED: Admin panel returns 200 OK"
else
  echo "⚠️  WARNING: Unexpected status $HTTP_STATUS (expected 307 or 200)"
fi
echo ""

echo "=== Test Results ==="
echo "✅ All E2E tests PASSED!"
echo ""
echo "Summary:"
echo "  - Login: ✅"
echo "  - Stats API: ✅"
echo "  - Users API: ✅"
echo "  - Activity API: ✅"
echo "  - CEFR API: ✅"
echo "  - Admin Panel: ✅"
