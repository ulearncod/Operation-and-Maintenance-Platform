"""
Prometheus指标API端点
提供Prometheus格式的指标数据
"""

from fastapi import APIRouter, Response
from app.monitoring.metrics import get_metrics_response

router = APIRouter()


@router.get("/prometheus")
async def get_prometheus_metrics():
    """获取Prometheus格式的指标数据"""
    return get_metrics_response()


@router.get("/health")
async def get_metrics_health():
    """获取指标服务健康状态"""
    return {
        "status": "healthy",
        "service": "metrics-service",
        "endpoints": {
            "prometheus": "/api/v1/metrics/prometheus",
            "health": "/api/v1/metrics/health"
        }
    }