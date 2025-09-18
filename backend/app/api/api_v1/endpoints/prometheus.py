"""
Prometheus查询API端点
提供Prometheus查询接口
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, Optional
from pydantic import BaseModel

from app.services.prometheus_service import PrometheusService

router = APIRouter()

# 全局Prometheus服务实例
prometheus_service = PrometheusService()


class PrometheusQuery(BaseModel):
    """Prometheus查询模型"""
    query: str
    start: Optional[str] = None
    end: Optional[str] = None
    step: Optional[str] = "15s"


@router.post("/query")
async def query_prometheus(query_data: PrometheusQuery):
    """执行Prometheus查询"""
    try:
        # 白名单检查（安全考虑）
        allowed_queries = [
            "node_cpu_seconds_total",
            "node_memory_MemTotal_bytes",
            "node_memory_MemAvailable_bytes",
            "node_filesystem_size_bytes",
            "node_filesystem_avail_bytes",
            "node_network_receive_bytes_total",
            "node_network_transmit_bytes_total",
            "kube_node_info",
            "kube_pod_info",
            "kube_pod_status_phase",
            "kube_node_status_condition",
            "up",
            "rate(",
            "avg(",
            "sum(",
            "count("
        ]
        
        # 检查查询是否包含允许的指标
        if not any(allowed in query_data.query for allowed in allowed_queries):
            raise HTTPException(
                status_code=400, 
                detail="查询包含不允许的指标，请使用预定义的查询模板"
            )
        
        if query_data.start and query_data.end:
            # 范围查询
            result = await prometheus_service.query_range(
                query_data.query,
                query_data.start,
                query_data.end,
                query_data.step
            )
        else:
            # 即时查询
            result = await prometheus_service.query(query_data.query)
        
        return {
            "status": "success",
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prometheus查询失败: {str(e)}")


@router.get("/query/cpu-trend")
async def get_cpu_trend(duration: str = "1h"):
    """获取CPU使用率趋势"""
    try:
        if duration not in ["1h", "6h", "24h"]:
            raise HTTPException(status_code=400, detail="duration必须是1h、6h或24h")
        
        trend_data = await prometheus_service.get_cpu_usage_trend(duration)
        
        return {
            "status": "success",
            "data": {
                "duration": duration,
                "trend": trend_data
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取CPU趋势失败: {str(e)}")


@router.get("/query/memory-trend")
async def get_memory_trend(duration: str = "1h"):
    """获取内存使用率趋势"""
    try:
        if duration not in ["1h", "6h", "24h"]:
            raise HTTPException(status_code=400, detail="duration必须是1h、6h或24h")
        
        trend_data = await prometheus_service.get_memory_usage_trend(duration)
        
        return {
            "status": "success",
            "data": {
                "duration": duration,
                "trend": trend_data
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取内存趋势失败: {str(e)}")


@router.get("/query/kubernetes")
async def get_kubernetes_metrics():
    """获取Kubernetes指标"""
    try:
        metrics = await prometheus_service.get_kubernetes_metrics()
        
        return {
            "status": "success",
            "data": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取Kubernetes指标失败: {str(e)}")


@router.get("/query/summary")
async def get_prometheus_summary():
    """获取Prometheus汇总指标"""
    try:
        summary = await prometheus_service.get_summary_metrics()
        
        return {
            "status": "success",
            "data": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取Prometheus汇总失败: {str(e)}")


@router.get("/health")
async def prometheus_health():
    """检查Prometheus健康状态"""
    try:
        # 执行一个简单的查询来检查Prometheus是否可用
        result = await prometheus_service.query("up")
        
        if result.get("status") == "success":
            return {
                "status": "healthy",
                "prometheus": "connected"
            }
        else:
            return {
                "status": "unhealthy",
                "prometheus": "disconnected"
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "prometheus": "error",
            "error": str(e)
        }