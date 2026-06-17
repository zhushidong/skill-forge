#!/bin/bash
set -e

echo "=== Skill Forge Smoke Test ==="

echo ""
echo "--- 1. Init ---"
skill-forge init

echo ""
echo "--- 2. Ingest ---"
skill-forge ingest --type case --title "客户嫌贵推进案例" --file samples/case-price.md --note "用于提炼价格异议处理"

echo ""
echo "--- 3. Inspect ---"
skill-forge inspect --file samples/external-agent.md --type auto

echo ""
echo "--- 4. Melt ---"
skill-forge melt --file samples/external-agent.md --type agent --target-scene "客户异议处理"

echo ""
echo "--- 5. Recommend ---"
skill-forge recommend --file samples/current-chat.md --context "产品是999元课程，客户来自小红书私信"

echo ""
echo "=== Smoke Test Complete ==="
