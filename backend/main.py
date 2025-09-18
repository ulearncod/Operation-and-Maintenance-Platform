"""
运维平台监控服务主入口
基于FastAPI + Prometheus的服务器资源监控系统
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db
from app.api.api_v1.api import api_router
from app.monitoring.metrics import setup_metrics
from app.monitoring.collectors import SystemCollector


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print("🚀 启动监控服务...")
    await init_db()
    setup_metrics()
    
    # 启动系统指标收集器
    collector = SystemCollector()
    collector.start()
    
    yield
    
    # 关闭时执行
    print("🛑 关闭监控服务...")
    collector.stop()


# 创建FastAPI应用
app = FastAPI(
    title="运维平台监控服务",
    description="基于Prometheus的服务器资源监控系统",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    """根路径健康检查"""
    return {
        "message": "运维平台监控服务",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "monitoring-service"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )