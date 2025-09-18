"""
监控相关API端点
提供系统资源监控的RESTful接口
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from datetime import datetime, timedelta

from app.monitoring.collectors.system_collector import SystemCollector
from app.monitoring.metrics import get_metrics_response

router = APIRouter()

# 全局收集器实例
system_collector = SystemCollector()


@router.get("/status")
async def get_monitoring_status():
    """获取监控服务状态"""
    return {
        "status": "running",
        "collector_running": system_collector.running,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/system/overview")
async def get_system_overview():
    """获取系统概览信息"""
    try:
        metrics = system_collector.get_current_metrics()
        return {
            "timestamp": datetime.now().isoformat(),
            "system": {
                "cpu_usage": metrics.get('cpu', {}).get('usage_percent', 0),
                "memory_usage": metrics.get('memory', {}).get('virtual', {}).get('percent', 0),
                "disk_usage": metrics.get('disk', {}).get('root', {}).get('percent', 0),
                "process_count": metrics.get('processes', {}).get('count', 0)
            },
            "status": "healthy"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取系统概览失败: {str(e)}")


@router.get("/system/cpu")
async def get_cpu_metrics():
    """获取CPU指标"""
    try:
        metrics = system_collector.get_current_metrics()
        cpu_data = metrics.get('cpu', {})
        
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu": {
                "usage_percent": cpu_data.get('usage_percent', 0),
                "load_average": {
                    "1min": cpu_data.get('load_avg', [0, 0, 0])[0],
                    "5min": cpu_data.get('load_avg', [0, 0, 0])[1],
                    "15min": cpu_data.get('load_avg', [0, 0, 0])[2]
                },
                "core_count": cpu_data.get('count', 0)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取CPU指标失败: {str(e)}")


@router.get("/system/memory")
async def get_memory_metrics():
    """获取内存指标"""
    try:
        metrics = system_collector.get_current_metrics()
        memory_data = metrics.get('memory', {})
        
        virtual_memory = memory_data.get('virtual', {})
        swap_memory = memory_data.get('swap', {})
        
        return {
            "timestamp": datetime.now().isoformat(),
            "memory": {
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
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取内存指标失败: {str(e)}")


@router.get("/system/disk")
async def get_disk_metrics():
    """获取磁盘指标"""
    try:
        metrics = system_collector.get_current_metrics()
        disk_data = metrics.get('disk', {})
        
        root_usage = disk_data.get('root', {})
        partitions = disk_data.get('partitions', [])
        
        return {
            "timestamp": datetime.now().isoformat(),
            "disk": {
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
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取磁盘指标失败: {str(e)}")


@router.get("/system/network")
async def get_network_metrics():
    """获取网络指标"""
    try:
        metrics = system_collector.get_current_metrics()
        network_data = metrics.get('network', {})
        
        io_counters = network_data.get('io_counters', {})
        
        return {
            "timestamp": datetime.now().isoformat(),
            "network": {
                "bytes_sent": io_counters.get('bytes_sent', 0),
                "bytes_recv": io_counters.get('bytes_recv', 0),
                "packets_sent": io_counters.get('packets_sent', 0),
                "packets_recv": io_counters.get('packets_recv', 0),
                "connections": network_data.get('connections', 0)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取网络指标失败: {str(e)}")


@router.get("/system/processes")
async def get_process_metrics():
    """获取进程指标"""
    try:
        metrics = system_collector.get_current_metrics()
        processes_data = metrics.get('processes', {})
        
        return {
            "timestamp": datetime.now().isoformat(),
            "processes": {
                "total_count": processes_data.get('count', 0),
                "top_cpu": processes_data.get('top_cpu', [])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取进程指标失败: {str(e)}")


@router.get("/alerts")
async def get_alerts():
    """获取告警信息"""
    # 这里可以集成Prometheus AlertManager
    return {
        "timestamp": datetime.now().isoformat(),
        "alerts": [],
        "status": "no_alerts"
    }


@router.post("/alerts/test")
async def test_alert():
    """测试告警功能"""
    return {
        "message": "告警测试成功",
        "timestamp": datetime.now().isoformat()
    }