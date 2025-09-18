"""
系统汇总API端点
提供系统资源的综合概览数据
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime, timedelta
import asyncio

from app.monitoring.collectors.system_collector import SystemCollector
from app.services.prometheus_service import PrometheusService

router = APIRouter()

# 全局服务实例
system_collector = SystemCollector()
prometheus_service = PrometheusService()


@router.get("/summary")
async def get_system_summary():
    """获取系统综合概览"""
    try:
        # 获取系统指标
        system_metrics = system_collector.get_current_metrics()
        
        # 获取Prometheus指标
        prometheus_metrics = await prometheus_service.get_summary_metrics()
        
        # 计算告警状态
        alert_status = await get_alert_status()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "system": {
                "cpu_usage": system_metrics.get('cpu', {}).get('usage_percent', 0),
                "memory_usage": system_metrics.get('memory', {}).get('virtual', {}).get('percent', 0),
                "disk_usage": system_metrics.get('disk', {}).get('root', {}).get('percent', 0),
                "process_count": system_metrics.get('processes', {}).get('count', 0),
                "load_average": system_metrics.get('cpu', {}).get('load_avg', [0, 0, 0])
            },
            "kubernetes": {
                "node_count": prometheus_metrics.get('node_count', 0),
                "pod_count": prometheus_metrics.get('pod_count', 0),
                "running_pods": prometheus_metrics.get('running_pods', 0),
                "failed_pods": prometheus_metrics.get('failed_pods', 0)
            },
            "alerts": alert_status,
            "status": "healthy"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取系统概览失败: {str(e)}")


@router.get("/resources/overview")
async def get_resources_overview():
    """获取资源概览"""
    try:
        # 获取所有资源数据
        cpu_data = await get_cpu_metrics()
        memory_data = await get_memory_metrics()
        disk_data = await get_disk_metrics()
        network_data = await get_network_metrics()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "resources": {
                "cpu": cpu_data,
                "memory": memory_data,
                "disk": disk_data,
                "network": network_data
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取资源概览失败: {str(e)}")


@router.get("/kubernetes/overview")
async def get_kubernetes_overview():
    """获取Kubernetes概览"""
    try:
        # 获取K8s指标
        k8s_metrics = await prometheus_service.get_kubernetes_metrics()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "kubernetes": k8s_metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取Kubernetes概览失败: {str(e)}")


@router.get("/alerts/overview")
async def get_alerts_overview():
    """获取告警概览"""
    try:
        alert_status = await get_alert_status()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "alerts": alert_status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取告警概览失败: {str(e)}")


async def get_alert_status() -> Dict[str, Any]:
    """获取告警状态"""
    try:
        # 这里应该从AlertManager获取，暂时返回模拟数据
        return {
            "active_alerts": 0,
            "critical_alerts": 0,
            "warning_alerts": 0,
            "resolved_alerts": 0,
            "status": "no_alerts"
        }
    except Exception:
        return {
            "active_alerts": 0,
            "critical_alerts": 0,
            "warning_alerts": 0,
            "resolved_alerts": 0,
            "status": "unknown"
        }


async def get_cpu_metrics() -> Dict[str, Any]:
    """获取CPU指标"""
    try:
        metrics = system_collector.get_current_metrics()
        cpu_data = metrics.get('cpu', {})
        
        return {
            "usage_percent": cpu_data.get('usage_percent', 0),
            "load_average": {
                "1min": cpu_data.get('load_avg', [0, 0, 0])[0],
                "5min": cpu_data.get('load_avg', [0, 0, 0])[1],
                "15min": cpu_data.get('load_avg', [0, 0, 0])[2]
            },
            "core_count": cpu_data.get('count', 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取CPU指标失败: {str(e)}")


async def get_memory_metrics() -> Dict[str, Any]:
    """获取内存指标"""
    try:
        metrics = system_collector.get_current_metrics()
        memory_data = metrics.get('memory', {})
        
        virtual_memory = memory_data.get('virtual', {})
        swap_memory = memory_data.get('swap', {})
        
        return {
            "virtual": {
                "total": virtual_memory.get('total', 0),
                "available": virtual_memory.get('available', 0),
                "used": virtual_memory.get('used', 0),
                "free": virtual_memory.get('free', 0),
                "percent": virtual_memory.get('percent', 0)
            },
            "swap": {
                "total": swap_memory.get('total', 0),
                "used": swap_memory.get('used', 0),
                "free": swap_memory.get('free', 0),
                "percent": swap_memory.get('percent', 0)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取内存指标失败: {str(e)}")


async def get_disk_metrics() -> Dict[str, Any]:
    """获取磁盘指标"""
    try:
        metrics = system_collector.get_current_metrics()
        disk_data = metrics.get('disk', {})
        
        root_usage = disk_data.get('root', {})
        partitions = disk_data.get('partitions', [])
        
        return {
            "root": {
                "total": root_usage.get('total', 0),
                "used": root_usage.get('used', 0),
                "free": root_usage.get('free', 0),
                "percent": root_usage.get('percent', 0)
            },
            "partitions": [
                {
                    "device": partition.get('device', ''),
                    "mountpoint": partition.get('mountpoint', ''),
                    "fstype": partition.get('fstype', ''),
                    "total": partition.get('usage', {}).get('total', 0),
                    "used": partition.get('usage', {}).get('used', 0),
                    "free": partition.get('usage', {}).get('free', 0),
                    "percent": partition.get('usage', {}).get('percent', 0)
                }
                for partition in partitions
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取磁盘指标失败: {str(e)}")


async def get_network_metrics() -> Dict[str, Any]:
    """获取网络指标"""
    try:
        metrics = system_collector.get_current_metrics()
        network_data = metrics.get('network', {})
        
        io_counters = network_data.get('io_counters', {})
        
        return {
            "bytes_sent": io_counters.get('bytes_sent', 0),
            "bytes_recv": io_counters.get('bytes_recv', 0),
            "packets_sent": io_counters.get('packets_sent', 0),
            "packets_recv": io_counters.get('packets_recv', 0),
            "connections": network_data.get('connections', 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取网络指标失败: {str(e)}")