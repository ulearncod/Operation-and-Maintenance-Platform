"""
Prometheus服务集成
提供与Prometheus API的交互功能
"""

import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

from app.core.config import settings


class PrometheusService:
    """Prometheus服务类"""
    
    def __init__(self):
        self.base_url = "http://prometheus:9090"  # Docker网络中的Prometheus地址
        self.timeout = 10.0
    
    async def query(self, query: str, time: Optional[str] = None) -> Dict[str, Any]:
        """执行Prometheus查询"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {"query": query}
                if time:
                    params["time"] = time
                
                response = await client.get(f"{self.base_url}/api/v1/query", params=params)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"Prometheus query error: {e}")
            return {"status": "error", "data": {"result": []}}
    
    async def query_range(self, query: str, start: str, end: str, step: str = "15s") -> Dict[str, Any]:
        """执行Prometheus范围查询"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {
                    "query": query,
                    "start": start,
                    "end": end,
                    "step": step
                }
                
                response = await client.get(f"{self.base_url}/api/v1/query_range", params=params)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"Prometheus query_range error: {e}")
            return {"status": "error", "data": {"result": []}}
    
    async def get_summary_metrics(self) -> Dict[str, Any]:
        """获取汇总指标"""
        try:
            # 获取节点数量
            node_count_query = "count(kube_node_info)"
            node_count_result = await self.query(node_count_query)
            node_count = 0
            if node_count_result.get("status") == "success" and node_count_result.get("data", {}).get("result"):
                node_count = int(float(node_count_result["data"]["result"][0]["value"][1]))
            
            # 获取Pod数量
            pod_count_query = "count(kube_pod_info)"
            pod_count_result = await self.query(pod_count_query)
            pod_count = 0
            if pod_count_result.get("status") == "success" and pod_count_result.get("data", {}).get("result"):
                pod_count = int(float(pod_count_result["data"]["result"][0]["value"][1]))
            
            # 获取运行中的Pod数量
            running_pods_query = "count(kube_pod_status_phase{phase=\"Running\"})"
            running_pods_result = await self.query(running_pods_query)
            running_pods = 0
            if running_pods_result.get("status") == "success" and running_pods_result.get("data", {}).get("result"):
                running_pods = int(float(running_pods_result["data"]["result"][0]["value"][1]))
            
            # 获取失败的Pod数量
            failed_pods_query = "count(kube_pod_status_phase{phase=\"Failed\"})"
            failed_pods_result = await self.query(failed_pods_query)
            failed_pods = 0
            if failed_pods_result.get("status") == "success" and failed_pods_result.get("data", {}).get("result"):
                failed_pods = int(float(failed_pods_result["data"]["result"][0]["value"][1]))
            
            return {
                "node_count": node_count,
                "pod_count": pod_count,
                "running_pods": running_pods,
                "failed_pods": failed_pods
            }
        except Exception as e:
            print(f"Error getting summary metrics: {e}")
            return {
                "node_count": 0,
                "pod_count": 0,
                "running_pods": 0,
                "failed_pods": 0
            }
    
    async def get_kubernetes_metrics(self) -> Dict[str, Any]:
        """获取Kubernetes指标"""
        try:
            # 获取节点状态
            node_status_query = "kube_node_status_condition{condition=\"Ready\"}"
            node_status_result = await self.query(node_status_query)
            
            nodes = []
            if node_status_result.get("status") == "success":
                for result in node_status_result.get("data", {}).get("result", []):
                    node_name = result["metric"].get("node", "unknown")
                    status = result["metric"].get("status", "Unknown")
                    nodes.append({
                        "name": node_name,
                        "status": status,
                        "ready": status == "True"
                    })
            
            # 获取Pod状态
            pod_status_query = "kube_pod_status_phase"
            pod_status_result = await self.query(pod_status_query)
            
            pods = []
            if pod_status_result.get("status") == "success":
                for result in pod_status_result.get("data", {}).get("result", []):
                    pod_name = result["metric"].get("pod", "unknown")
                    namespace = result["metric"].get("namespace", "default")
                    phase = result["metric"].get("phase", "Unknown")
                    pods.append({
                        "name": pod_name,
                        "namespace": namespace,
                        "phase": phase
                    })
            
            return {
                "nodes": nodes,
                "pods": pods,
                "node_count": len(nodes),
                "pod_count": len(pods),
                "ready_nodes": len([n for n in nodes if n["ready"]]),
                "running_pods": len([p for p in pods if p["phase"] == "Running"])
            }
        except Exception as e:
            print(f"Error getting kubernetes metrics: {e}")
            return {
                "nodes": [],
                "pods": [],
                "node_count": 0,
                "pod_count": 0,
                "ready_nodes": 0,
                "running_pods": 0
            }
    
    async def get_cpu_usage_trend(self, duration: str = "1h") -> List[Dict[str, Any]]:
        """获取CPU使用率趋势"""
        try:
            end_time = datetime.now()
            if duration == "1h":
                start_time = end_time - timedelta(hours=1)
            elif duration == "6h":
                start_time = end_time - timedelta(hours=6)
            elif duration == "24h":
                start_time = end_time - timedelta(hours=24)
            else:
                start_time = end_time - timedelta(hours=1)
            
            query = "100 - (avg(rate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)"
            result = await self.query_range(
                query,
                start_time.isoformat(),
                end_time.isoformat(),
                "1m"
            )
            
            trend_data = []
            if result.get("status") == "success":
                for data_point in result.get("data", {}).get("result", []):
                    if data_point.get("values"):
                        for value in data_point["values"]:
                            trend_data.append({
                                "timestamp": value[0],
                                "value": float(value[1])
                            })
            
            return trend_data
        except Exception as e:
            print(f"Error getting CPU usage trend: {e}")
            return []
    
    async def get_memory_usage_trend(self, duration: str = "1h") -> List[Dict[str, Any]]:
        """获取内存使用率趋势"""
        try:
            end_time = datetime.now()
            if duration == "1h":
                start_time = end_time - timedelta(hours=1)
            elif duration == "6h":
                start_time = end_time - timedelta(hours=6)
            elif duration == "24h":
                start_time = end_time - timedelta(hours=24)
            else:
                start_time = end_time - timedelta(hours=1)
            
            query = "(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100"
            result = await self.query_range(
                query,
                start_time.isoformat(),
                end_time.isoformat(),
                "1m"
            )
            
            trend_data = []
            if result.get("status") == "success":
                for data_point in result.get("data", {}).get("result", []):
                    if data_point.get("values"):
                        for value in data_point["values"]:
                            trend_data.append({
                                "timestamp": value[0],
                                "value": float(value[1])
                            })
            
            return trend_data
        except Exception as e:
            print(f"Error getting memory usage trend: {e}")
            return []