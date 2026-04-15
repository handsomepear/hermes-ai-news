#!/usr/bin/env python3
"""
save_report.py — 将 AI 日报内容写入 hermes_ai_news 项目
用法：python3 save_report.py "报告内容"
或通过 stdin：echo "报告内容" | python3 save_report.py

自动维护 reports/index.json 索引供前端使用。
"""

import json
import os
import sys
import re
from datetime import datetime, timezone, timedelta

# ---- 配置 ----
PROJECT_DIR = os.path.expanduser("~/workspace/hermes_ai_news")
REPORTS_DIR = os.path.join(PROJECT_DIR, "reports")
INDEX_FILE  = os.path.join(REPORTS_DIR, "index.json")

CST = timezone(timedelta(hours=8))


def extract_title(content: str) -> str:
    """从报告内容提取标题（主线那一行）"""
    # 尝试匹配 "📍 今天的主线" 或 "主线" 后的内容
    for pattern in [
        r"📍[^\n]*主线[^\n]*\n([^\n]+)",
        r"主线[：:]\s*([^\n]+)",
        r"🧠 AI 认知日报[^\n]*\n+([^\n]+)",
        r"#{1,2}\s*([^\n]{10,60})",
    ]:
        m = re.search(pattern, content)
        if m:
            title = m.group(1).strip()
            title = re.sub(r"^[#\-\*\s]+", "", title)
            if title:
                return title[:80]
    # fallback：取第一个非空行
    for line in content.split("\n"):
        line = line.strip()
        if len(line) > 8:
            return line[:80]
    return "AI 日报"


def extract_preview(content: str) -> str:
    """提取前150字作为预览"""
    # 跳过标题行
    lines = [l.strip() for l in content.split("\n") if l.strip()]
    text = " ".join(lines[1:4]) if len(lines) > 1 else " ".join(lines)
    text = re.sub(r"[#\*\_\[\]`]+", "", text)
    return text[:150].strip()


def load_index() -> list:
    if os.path.exists(INDEX_FILE):
        try:
            with open(INDEX_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def save_index(reports: list):
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(reports, f, ensure_ascii=False, indent=2)


def main():
    # 读取报告内容（命令行参数 or stdin）
    if len(sys.argv) > 1:
        content = " ".join(sys.argv[1:])
    else:
        content = sys.stdin.read()

    content = content.strip()
    if not content:
        print("ERROR: empty content", file=sys.stderr)
        sys.exit(1)

    os.makedirs(REPORTS_DIR, exist_ok=True)

    now = datetime.now(CST)
    date_str = now.strftime("%Y-%m-%d")
    filename = f"{date_str}.md"
    filepath = os.path.join(REPORTS_DIR, filename)

    # 写入 Markdown 文件
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Saved: {filepath}")

    # 更新 index.json
    reports = load_index()

    # 去重（同一天覆盖）
    reports = [r for r in reports if r.get("date") != date_str]

    entry = {
        "date": date_str,
        "file": filename,
        "title": extract_title(content),
        "preview": extract_preview(content),
        "created_at": now.isoformat(),
    }

    reports.insert(0, entry)   # 最新在前
    save_index(reports)
    print(f"Index updated: {len(reports)} reports total")


if __name__ == "__main__":
    main()
