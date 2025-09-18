"""
Prometheus指标定义和配置
"""

from prometheus_client import (
    Counter, Histogram, Gauge, Info,
    generate_latest, CONTENT_TYPE_LATEST
)
from fastapi import Response
from fastapi.responses import PlainTextResponse


# 系统资源指标
class SystemMetrics:
    """系统资源监控指标"""
    
    # CPU指标
    cpu_usage_percent = Gauge(
        'system_cpu_usage_percent',
        'CPU使用率百分比',
        ['cpu', 'mode']
    )
    
    cpu_load_avg = Gauge(
        'system_cpu_load_average',
        'CPU负载平均值',
        ['period']
    )
    
    # 内存指标
    memory_usage_bytes = Gauge(
        'system_memory_usage_bytes',
        '内存使用量（字节）',
        ['type']
    )
    
    memory_usage_percent = Gauge(
        'system_memory_usage_percent',
        '内存使用率百分比',
        ['type']
    )
    
    # 磁盘指标
    disk_usage_bytes = Gauge(
        'system_disk_usage_bytes',
        '磁盘使用量（字节）',
        ['device', 'mountpoint', 'type']
    )
    
    disk_usage_percent = Gauge(
        'system_disk_usage_percent',
        '磁盘使用率百分比',
        ['device', 'mountpoint']
    )
    
    disk_io_total = Counter(
        'system_disk_io_total',
        '磁盘IO总次数',
        ['device', 'operation']
    )
    
    # 网络指标
    network_bytes_total = Counter(
        'system_network_bytes_total',
        '网络传输总字节数',
        ['interface', 'direction']
    )
    
    network_packets_total = Counter(
        'system_network_packets_total',
        '网络传输总包数',
        ['interface', 'direction']
    )
    
    # 进程指标
    process_count = Gauge(
        'system_process_count',
        '系统进程数量',
        ['state']
    )
    
    # 系统信息
    system_info = Info(
        'system_info',
        '系统信息'
    )


# 应用指标
class ApplicationMetrics:
    """应用监控指标"""
    
    # HTTP请求指标
    http_requests_total = Counter(
        'http_requests_total',
        'HTTP请求总数',
        ['method', 'endpoint', 'status_code']
    )
    
    http_request_duration_seconds = Histogram(
        'http_request_duration_seconds',
        'HTTP请求处理时间（秒）',
        ['method', 'endpoint']
    )
    
    # 数据库指标
    database_connections = Gauge(
        'database_connections',
        '数据库连接数',
        ['state']
    )
    
    database_query_duration_seconds = Histogram(
        'database_query_duration_seconds',
        '数据库查询时间（秒）',
        ['operation']
    )
    
    # 缓存指标
    cache_hits_total = Counter(
        'cache_hits_total',
        '缓存命中总数',
        ['cache_type']
    )
    
    cache_misses_total = Counter(
        'cache_misses_total',
        '缓存未命中总数',
        ['cache_type']
    )


# 创建指标实例
system_metrics = SystemMetrics()
app_metrics = ApplicationMetrics()


def setup_metrics():
    """设置Prometheus指标"""
    print("📊 初始化Prometheus指标...")


def get_metrics_response() -> Response:
    """获取Prometheus指标响应"""
    metrics_data = generate_latest()
    return PlainTextResponse(
        content=metrics_data,
        media_type=CONTENT_TYPE_LATEST
    )