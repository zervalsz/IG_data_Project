#!/bin/bash
# Backend Docker 构建和部署测试脚本

set -e  # 遇到错误立即退出

echo "=================================="
echo "Backend Docker 部署测试"
echo "=================================="

cd "$(dirname "$0")"

# 1. 检查Docker是否运行
echo ""
echo "📋 步骤1: 检查Docker状态..."
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker未运行，请先启动Docker Desktop"
    exit 1
fi
echo "✅ Docker运行正常"

# 2. 检查必需文件
echo ""
echo "📋 步骤2: 检查必需文件..."
files=("Dockerfile" ".env" "requirements.txt" "api/server.py")
for file in "${files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ 缺少文件: $file"
        exit 1
    fi
    echo "✅ $file"
done

# 3. 构建镜像
echo ""
echo "📋 步骤3: 构建Docker镜像..."
echo "提示: 首次构建可能需要5-10分钟..."
docker build -t xhs-backend:latest .
echo "✅ 镜像构建成功"

# 4. 检查镜像大小
echo ""
echo "📋 步骤4: 检查镜像信息..."
docker images xhs-backend:latest
IMAGE_SIZE=$(docker images xhs-backend:latest --format "{{.Size}}")
echo "镜像大小: $IMAGE_SIZE"

# 5. 测试运行（短暂启动测试）
echo ""
echo "📋 步骤5: 测试容器启动..."
echo "启动测试容器（30秒后自动停止）..."

# 停止可能存在的旧容器
docker rm -f xhs-backend-test 2>/dev/null || true

# 启动测试容器
docker run -d \
  --name xhs-backend-test \
  -p 5002:5001 \
  --env-file .env \
  xhs-backend:latest

echo "等待容器启动..."
sleep 5

# 6. 健康检查
echo ""
echo "📋 步骤6: 健康检查..."
for i in {1..6}; do
    if curl -s http://localhost:5002/api/health > /dev/null; then
        echo "✅ 健康检查通过"
        HEALTH_RESPONSE=$(curl -s http://localhost:5002/api/health)
        echo "$HEALTH_RESPONSE" | python3 -m json.tool
        break
    else
        echo "⏳ 等待服务启动... ($i/6)"
        sleep 5
    fi
    
    if [ $i -eq 6 ]; then
        echo "❌ 健康检查失败，查看日志:"
        docker logs xhs-backend-test
        docker rm -f xhs-backend-test
        exit 1
    fi
done

# 7. 清理测试容器
echo ""
echo "📋 步骤7: 清理测试容器..."
docker stop xhs-backend-test
docker rm xhs-backend-test
echo "✅ 测试容器已清理"

# 8. 总结
echo ""
echo "=================================="
echo "✅ 所有测试通过！"
echo "=================================="
echo ""
echo "📦 镜像已准备好: xhs-backend:latest"
echo ""
echo "🚀 部署命令:"
echo ""
echo "方法1: Docker Compose (推荐)"
echo "  docker-compose up -d"
echo ""
echo "方法2: 直接运行"
echo "  docker run -d \\"
echo "    --name xhs-backend \\"
echo "    -p 5000:5000 \\"
echo "    --env-file .env \\"
echo "    xhs-backend:latest"
echo ""
echo "查看日志:"
echo "  docker logs -f xhs-backend"
echo ""
echo "健康检查:"
echo "  curl http://localhost:5000/api/health"
echo ""
