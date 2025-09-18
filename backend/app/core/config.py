"""
应用配置管理
"""

import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基础配置
    APP_NAME: str = "运维平台监控服务"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API配置
    API_V1_STR: str = "/api/v1"
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # 数据库配置
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/monitoring"
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Prometheus配置
    PROMETHEUS_PORT: int = 9090
    METRICS_PATH: str = "/metrics"
    
    # 监控配置
    COLLECTION_INTERVAL: int = 10  # 指标收集间隔（秒）
    RETENTION_DAYS: int = 30  # 数据保留天数
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/monitoring.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()