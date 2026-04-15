#!/usr/bin/env bash
# deploy_report.sh — 推送最新日报到 GitHub 并触发 Vercel 生产部署
# 用法：bash deploy_report.sh
# 成功时 exit 0，失败时 exit 1

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_DIR"

# 加载 Vercel token
ENV_FILE="$HOME/.hermes/.env"
if [ -f "$ENV_FILE" ]; then
  set -a
  # 只导出 VERCEL_TOKEN，避免污染环境
  VERCEL_TOKEN=$(grep "^VERCEL_TOKEN=" "$ENV_FILE" | head -1 | cut -d= -f2 | tr -d '\r\n')
  set +a
fi

if [ -z "${VERCEL_TOKEN:-}" ]; then
  echo "[deploy] ERROR: VERCEL_TOKEN not found in $ENV_FILE" >&2
  exit 1
fi

echo "[deploy] Working in: $REPO_DIR"

# 检查是否有改动
if git diff --quiet && git diff --staged --quiet; then
  echo "[deploy] No changes to commit, skipping git push"
else
  # git commit & push
  TODAY=$(date +%Y-%m-%d)
  git add reports/ 2>/dev/null || true
  git commit -m "日报更新: $TODAY" || echo "[deploy] Nothing new to commit"
  git push origin main
  echo "[deploy] Pushed to GitHub"
fi

# Vercel 生产部署（不依赖 GitHub 集成，直接 CLI 部署）
echo "[deploy] Triggering Vercel production deploy..."
DEPLOY_URL=$(VERCEL_TOKEN="$VERCEL_TOKEN" vercel deploy --prod --yes --token "$VERCEL_TOKEN" 2>&1 | grep -E "^https://" | tail -1)

if [ -n "$DEPLOY_URL" ]; then
  echo "[deploy] Deployed: $DEPLOY_URL"
  echo "[deploy] Production URL: https://hermes-ai-news.vercel.app"
else
  echo "[deploy] WARNING: Could not parse deploy URL, check vercel output above"
fi

echo "[deploy] Done"
