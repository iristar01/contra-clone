#!/bin/bash
set -e

echo "================================"
echo "  Contra Clone 自动部署脚本"
echo "================================"
echo ""

# 获取 GitHub 用户名
read -p "请输入你的 GitHub 用户名: " GH_USER
if [ -z "$GH_USER" ]; then
    echo "错误: 用户名不能为空"
    exit 1
fi

# 获取 Personal Access Token
read -s -p "请输入 GitHub Personal Access Token (不会显示): " GH_TOKEN
echo ""
if [ -z "$GH_TOKEN" ]; then
    echo "错误: Token 不能为空"
    exit 1
fi

REPO_NAME="contra-clone"
REPO_URL="https://${GH_USER}:${GH_TOKEN}@github.com/${GH_USER}/${REPO_NAME}.git"

echo ""
echo "步骤 1/4: 创建 GitHub 仓库..."
curl -s -o /tmp/gh_create_repo.json -w "%{http_code}" \
  -X POST \
  -H "Authorization: token ${GH_TOKEN}" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d "{\"name\":\"${REPO_NAME}\",\"private\":false}" > /tmp/gh_status_code

STATUS=$(cat /tmp/gh_status_code)
if [ "$STATUS" = "201" ]; then
    echo "✅ 仓库创建成功"
elif [ "$STATUS" = "422" ]; then
    echo "⚠️  仓库已存在，跳过创建"
else
    echo "❌ 创建仓库失败 (HTTP $STATUS)"
    cat /tmp/gh_create_repo.json
    exit 1
fi

echo ""
echo "步骤 2/4: 推送代码..."
git remote remove origin 2>/dev/null || true
git remote add origin "$REPO_URL"
git branch -M main
git push -u origin main --force

echo ""
echo "步骤 3/4: 开启 GitHub Pages..."
curl -s -o /tmp/gh_pages.json -w "%{http_code}" \
  -X POST \
  -H "Authorization: token ${GH_TOKEN}" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/${GH_USER}/${REPO_NAME}/pages \
  -d "{\"source\":{\"branch\":\"main\",\"path\":\"/docs\"}}" > /tmp/gh_pages_status

PAGE_STATUS=$(cat /tmp/gh_pages_status)
if [ "$PAGE_STATUS" = "201" ] || [ "$PAGE_STATUS" = "204" ]; then
    echo "✅ GitHub Pages 已开启"
else
    # 可能是已经开启过了，尝试更新
    curl -s -o /dev/null \
      -X PUT \
      -H "Authorization: token ${GH_TOKEN}" \
      -H "Accept: application/vnd.github.v3+json" \
      https://api.github.com/repos/${GH_USER}/${REPO_NAME}/pages \
      -d "{\"source\":{\"branch\":\"main\",\"path\":\"/docs\"}}"
    echo "✅ GitHub Pages 设置已更新"
fi

echo ""
echo "================================"
echo "  部署完成！"
echo "================================"
echo ""
echo "你的游戏将在 1-2 分钟后可访问:"
echo ""
echo "  🎮 https://${GH_USER}.github.io/${REPO_NAME}/"
echo ""
echo "如果还看不到，去 GitHub 仓库 Settings -> Pages 确认设置。"
echo ""
