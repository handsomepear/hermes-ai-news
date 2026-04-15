#!/usr/bin/env bash
# deploy_report.sh — 推送最新日报到 GitHub
# Vercel 通过 GitHub App 集成自动触发生产部署，无需 token
# 用法：bash deploy_report.sh

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_DIR"

echo "[deploy] Working in: $REPO_DIR"

# 检查是否有改动
if git diff --quiet && git diff --staged --quiet; then
  echo "[deploy] No changes to commit, skipping"
  exit 0
fi

TODAY=$(date +%Y-%m-%d)
git add reports/
git commit -m "日报更新: $TODAY"
git push origin main

echo "[deploy] Pushed to GitHub — Vercel will auto-deploy via GitHub App"
echo "[deploy] Production URL: https://hermes-ai-news.vercel.app"
