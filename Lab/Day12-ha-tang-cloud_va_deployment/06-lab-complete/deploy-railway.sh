#!/bin/sh
# Deploy Task 6 — tạo web service nếu project chỉ có Redis
set -e
cd "$(dirname "$0")"

echo "=== Railway Deploy — Task 6 ==="
echo ""

# Liệt kê services hiện có
echo "Services trong project:"
railway service list 2>/dev/null || true
echo ""

# Tạo web service nếu chưa có (bỏ qua lỗi nếu đã tồn tại)
echo "Tạo web service 'agent' (bỏ qua nếu đã có)..."
railway add --service agent 2>/dev/null || true

echo ""
echo "Link tới service AGENT (chọn 'agent', KHÔNG chọn Redis)..."
railway service link agent

echo ""
echo "Set biến môi trường..."
railway variables set ENVIRONMENT=production 2>/dev/null || true
railway variables delete PORT 2>/dev/null || true

echo ""
echo "Deploy..."
railway up --service agent --detach

echo ""
echo "Xong! Chạy: railway domain"
echo "Test: curl https://YOUR-DOMAIN/health"
