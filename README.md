# 运维平台 - 服务器资源监控系统

基于Prometheus + Grafana的现代化服务器资源监控平台，提供CPU、内存、磁盘、网络等核心指标的实时监控和可视化展示。

## 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Grafana       │    │   Prometheus    │    │   Node Exporter │
│   (可视化)       │◄──►│   (指标收集)     │◄──►│   (指标暴露)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Python API    │    │   kube-state-   │    │   Kubernetes    │
│   (数据接口)     │    │   metrics       │    │   (集群监控)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 技术栈

### 后端监控
- **Python FastAPI**: 提供RESTful API接口
- **Prometheus Client**: 暴露自定义指标
- **psutil**: 系统资源监控
- **Redis**: 缓存和消息队列

### 监控组件
- **Prometheus Operator**: Kubernetes原生监控
- **Grafana Operator**: 仪表板管理
- **Node Exporter**: 节点指标收集
- **kube-state-metrics**: Kubernetes状态指标

### 部署环境
- **Kubernetes**: 容器编排
- **Helm**: 包管理
- **Docker**: 容器化

## 监控指标

### 系统资源指标
- **CPU**: 使用率、负载、核心数
- **内存**: 使用率、可用内存、交换分区
- **磁盘**: 使用率、IOPS、读写速度
- **网络**: 带宽、连接数、丢包率

### Kubernetes指标
- **Pod状态**: 运行状态、重启次数
- **节点状态**: 就绪状态、资源使用
- **服务状态**: 健康检查、端点状态

## 快速开始

### 环境要求
- Python 3.9+
- Kubernetes 1.20+
- Helm 3.0+
- Docker 20.0+

### 安装步骤

1. 克隆项目
```bash
git clone <repository-url>
cd test_devops
```

2. 安装Prometheus Operator
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack
```

3. 启动Python监控服务
```bash
cd backend
pip install -r requirements.txt
python main.py
```

4. 访问监控界面
- Grafana: http://localhost:3000 (admin/prom-operator)
- Prometheus: http://localhost:9090
- API文档: http://localhost:8000/docs

## 项目结构

```
test_devops/
├── backend/                    # Python后端服务
│   ├── app/
│   │   ├── api/               # API路由
│   │   ├── core/              # 核心配置
│   │   ├── models/            # 数据模型
│   │   ├── services/          # 业务逻辑
│   │   └── utils/             # 工具函数
│   ├── monitoring/            # 监控相关
│   │   ├── exporters/         # 指标导出器
│   │   ├── collectors/        # 数据收集器
│   │   └── metrics/           # 自定义指标
│   └── requirements.txt
├── k8s/                       # Kubernetes配置
│   ├── prometheus/            # Prometheus配置
│   ├── grafana/               # Grafana配置
│   └── monitoring/            # 监控规则
├── helm/                      # Helm Charts
└── docker/                    # Docker配置
```

## 功能特性

### 实时监控
- 秒级数据采集
- 多维度指标展示
- 自定义告警规则

### 可视化展示
- 丰富的图表类型
- 自定义仪表板
- 移动端适配

### 告警管理
- 多渠道告警通知
- 告警规则管理
- 告警历史查询

### 数据存储
- 时序数据存储
- 数据压缩和清理
- 历史数据查询

## 开发指南

### 添加自定义指标
```python
from prometheus_client import Counter, Histogram, Gauge

# 定义指标
cpu_usage = Gauge('system_cpu_usage_percent', 'CPU usage percentage')
memory_usage = Gauge('system_memory_usage_bytes', 'Memory usage in bytes')

# 更新指标值
cpu_usage.set(psutil.cpu_percent())
memory_usage.set(psutil.virtual_memory().used)
```

### 创建Grafana仪表板
```json
{
  "dashboard": {
    "title": "服务器监控",
    "panels": [
      {
        "title": "CPU使用率",
        "type": "graph",
        "targets": [
          {
            "expr": "100 - (avg(rate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)"
          }
        ]
      }
    ]
  }
}
```

## 部署说明

详见 [部署文档](docs/deployment.md)

## 许可证

MIT License