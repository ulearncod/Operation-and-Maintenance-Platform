"""
API v1 路由配置
"""

from fastapi import APIRouter
from app.api.api_v1.endpoints import monitoring, metrics, summary, prometheus, auth

api_router = APIRouter()

# 注册监控相关路由
api_router.include_router(
    monitoring.router,
    prefix="/monitoring",
    tags=["监控"]
)

# 注册指标相关路由
api_router.include_router(
    metrics.router,
    prefix="/metrics",
    tags=["指标"]
)

# 注册汇总相关路由
api_router.include_router(
    summary.router,
    prefix="/summary",
    tags=["汇总"]
)

# 注册Prometheus查询路由
api_router.include_router(
    prometheus.router,
    prefix="/prometheus",
    tags=["Prometheus"]
)

# 认证与授权
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["认证"]
)