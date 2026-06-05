#!/bin/bash

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASSED=0
FAILED=0

echo -e "${YELLOW}🧪 Cripta Backend Tests${NC}\n"

# Test 1: Health
echo -e "${YELLOW}1. Health Check${NC}"
if curl -s http://localhost:8000/health | grep -q '"status":"ok"'; then
  echo -e "${GREEN}✅ Backend healthy${NC}"
  ((PASSED++))
else
  echo -e "${RED}❌ Failed${NC}"
  ((FAILED++))
  exit 1
fi

# Test 2: Dice
echo -e "\n${YELLOW}2. Dice Roll${NC}"
DICE=$(curl -s "http://localhost:8000/dice/roll?notation=1d20+5")
if echo "$DICE" | grep -q '"result"'; then
  echo -e "${GREEN}✅ Dice working${NC}"
  ((PASSED++))
else
  echo -e "${RED}❌ Failed${NC}"
  ((FAILED++))
fi

# Test 3: Combat
echo -e "\n${YELLOW}3. Combat Action${NC}"
COMBAT=$(curl -s -X POST http://localhost:8000/action \
  -H "Content-Type: application/json" \
  -d '{"action_type":"combat","description":"Attack","character_id":"hero"}')

if echo "$COMBAT" | grep -q '"success":true'; then
  echo -e "${GREEN}✅ Combat working${NC}"
  ((PASSED++))
else
  echo -e "${RED}❌ Failed${NC}"
  ((FAILED++))
fi

# Summary
echo -e "\n${YELLOW}═══════════════════════════${NC}"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo -e "${YELLOW}═══════════════════════════${NC}"

[ $FAILED -eq 0 ] && echo -e "${GREEN}✅ All tests passed!${NC}" || echo -e "${RED}❌ Some tests failed${NC}"
