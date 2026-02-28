"""
FastAPI服务 - 提供数据分析API（三层架构版本）
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(Path(__file__).parent.parent / '.env')

# 添加父目录到路径以支持相对导入
sys.path.insert(0, str(Path(__file__).parent.parent))

# 导入新的路由（使用Service层和Database层）
from api.routers import style_router, creator_router, instagram_router, trend_router

app = FastAPI(
    title="XHS Data Analysis API",
    version="2.0.0",
    description="小红书数据分析API - 三层架构版本"
)

# 配置CORS - Allow all origins for Codespaces
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for GitHub Codespaces
    allow_credentials=False,  # Must be False when using wildcard origins
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由（新架构）
app.include_router(style_router, tags=["风格生成"])
app.include_router(creator_router, tags=["创作者数据"])
app.include_router(instagram_router, tags=["instagram"])
app.include_router(trend_router, tags=["趋势生成"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "XHS Data Analysis API v2.0 - 三层架构",
        "architecture": {
            "database": "MongoDB - 数据访问层 (Repository Pattern)",
            "services": "Business Logic - 业务逻辑层",
            "api": "FastAPI - API接口层"
        },
        "endpoints": {
            "creators_network": "/api/creators/network",
            "creators_list": "/api/creators/list",
            "creator_detail": "/api/creators/{creator_name}",
            "style_generate": "/api/style/generate",
            "style_creators": "/api/style/creators",
            "health": "/api/health"
        },
        "docs": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }


@app.get("/api/health")
async def health_check():
    """健康检查"""
    from database.connection import test_connection
    
    # 测试数据库连接
    db_connected = test_connection()
    
    return {
        "status": "ok" if db_connected else "degraded",
        "version": "2.0.0",
        "architecture": "three-tier",
        "database": {
            "connected": db_connected,
            "type": "MongoDB Atlas"
        },
        "services": {
            "style_generation": "active",
            "creator_network": "active"
        }
    }


if __name__ == "__main__":
    import uvicorn
    import os
    
    # Get port from environment variable (for Render deployment) or default to 5000
    port = int(os.environ.get("PORT", 5000))
    
    print("\n" + "="*60)
    print("🚀 XHS Data Analysis API v2.0 - 三层架构")
    print("="*60)
    print("\n📋 架构层次:")
    print("  ├─ 数据库层 (Database Layer): MongoDB + Repository Pattern")
    print("  ├─ 服务层 (Service Layer): 业务逻辑处理")
    print("  └─ API层 (API Layer): FastAPI RESTful接口")
    print(f"\n🌐 服务地址: http://localhost:{port}")
    print(f"\n📚 API文档:")
    print(f"  - Swagger UI: http://localhost:{port}/docs")
    print(f"  - ReDoc: http://localhost:{port}/redoc")
    print(f"\n🔗 主要端点:")
    print(f"  - GET  /api/creators/network - 创作者网络数据")
    print(f"  - GET  /api/creators/list - 所有创作者列表")
    print(f"  - GET  /api/creators/{{name}} - 创作者详情")
    print(f"  - POST /api/style/generate - AI风格生成")
    print(f"  - GET  /api/style/creators - 可用创作者")
    print(f"  - GET  /api/health - 健康检查")
    print("="*60 + "\n")
    
    uvicorn.run(
        "api.server:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
