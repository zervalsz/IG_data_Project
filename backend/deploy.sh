#!/bin/bash
# 快速部署脚本 - 使用 Docker Compose

echo "🚀 Backend 快速部署"
echo ""

cd "$(dirname "$0")"

# 检查Docker
if ! docker info > /dev/null 2>&1; then
    echo "❌ 请先启动 Docker Desktop"
    exit 1
fi

# 检查.env文件
if [ ! -f .env ]; then
    echo "❌ 缺少 .env 文件"
    echo ""
    echo "请创建 .env 文件并添加以下内容:"
    echo ""
    echo "MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/database"
    echo "DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxx"
    echo ""
    exit 1
fi

echo "✅ 环境检查通过"
echo ""

# 构建并启动
echo "📦 构建并启动服务..."
docker-compose up -d --build

echo ""
echo "⏳ 等待服务启动..."
sleep 5

# 健康检查
echo ""
echo "🏥 健康检查..."
if curl -s http://localhost:5000/api/health > /dev/null; then
    echo "✅ 服务启动成功！"
    echo ""
    echo "🔗 API端点："
    echo "  - 健康检查: http://localhost:5000/api/health"
    echo "  - 创作者列表: http://localhost:5000/api/style/creators"
    echo "  - API文档: http://localhost:5000/docs"
    echo ""
    echo "📝 查看日志:"
    echo "  docker-compose logs -f"
    echo ""
    echo "🛑 停止服务:"
    echo "  docker-compose down"
else
    echo "⚠️  服务可能还在启动中，请稍后访问"
    echo ""
    echo "查看日志:"
    echo "  docker-compose logs -f"
fi
