# 运维平台监控系统 - 快速启动指南

## 🚀 快速开始

### 方式一：Docker Compose 部署（推荐用于开发测试）

1. **克隆项目并进入目录**
```bash
cd /home/asn/test_devops
```

2. **配置环境变量**
```bash
cp env.example .env
# 编辑 .env 文件，修改数据库密码等配置
```

3. **一键部署**
```bash
./scripts/deploy.sh -m docker -d
```

4. **访问服务**
- 监控API: http://localhost:8000
- Grafana仪表板: http://localhost:3000 (admin/admin123)
- Prometheus: http://localhost:9090
- API文档: http://localhost:8000/docs

### 方式二：Kubernetes 部署（推荐用于生产环境）

1. **确保Kubernetes环境就绪**
```bash
kubectl cluster-info
helm version
```

2. **一键部署**
```bash
./scripts/deploy.sh -m kubernetes -d
```

3. **获取访问地址**
```bash
kubectl get svc -n monitoring
kubectl get ingress -n monitoring
```

## 📊 监控功能

### 系统资源监控
- **CPU监控**: 使用率、负载平均值、核心数
- **内存监控**: 使用率、可用内存、交换分区
- **磁盘监控**: 使用率、IOPS、读写速度
- **网络监控**: 带宽、连接数、丢包率

### Kubernetes集群监控
- **Pod状态**: 运行状态、重启次数、资源使用
- **节点状态**: 就绪状态、资源使用、健康检查
- **服务状态**: 端点状态、负载均衡

### 告警功能
- **实时告警**: CPU、内存、磁盘使用率告警
- **多渠道通知**: 邮件、Webhook、钉钉等
- **告警规则**: 可自定义告警阈值和规则

## 🔧 常用操作

### 查看服务状态
```bash
# Docker方式
docker-compose -f docker/docker-compose.yml ps

# Kubernetes方式
kubectl get pods -n monitoring
```

### 查看日志
```bash
# Docker方式
docker-compose -f docker/docker-compose.yml logs -f monitoring-service

# Kubernetes方式
kubectl logs -f deployment/monitoring-service -n monitoring
```

### 停止服务
```bash
# Docker方式
./scripts/deploy.sh -m docker -s

# Kubernetes方式
./scripts/deploy.sh -m kubernetes -s
```

### 清理数据
```bash
# 注意：这将删除所有数据
./scripts/deploy.sh -m docker -c
```

## 📈 监控指标说明

### 系统指标
- `system_cpu_usage_percent`: CPU使用率百分比
- `system_memory_usage_bytes`: 内存使用量（字节）
- `system_disk_usage_percent`: 磁盘使用率百分比
- `system_network_bytes_total`: 网络传输总字节数

### Kubernetes指标
- `kube_pod_status_phase`: Pod状态阶段
- `kube_node_status_condition`: 节点状态条件
- `kube_pod_container_status_restarts_total`: Pod容器重启次数

### 应用指标
- `http_requests_total`: HTTP请求总数
- `http_request_duration_seconds`: HTTP请求处理时间
- `database_connections`: 数据库连接数

## 🛠️ 开发指南

### 添加自定义指标
```python
from app.monitoring.metrics import system_metrics

# 更新CPU使用率
system_metrics.cpu_usage_percent.labels(cpu='cpu0', mode='total').set(85.5)
```

### 创建Grafana仪表板
1. 访问 http://localhost:3000
2. 使用 admin/admin123 登录
3. 点击 "+" -> "Dashboard"
4. 添加Panel并配置Prometheus查询

### 配置告警规则
编辑 `k8s/prometheus/prometheus-rules.yaml` 文件，添加自定义告警规则。

## 🔍 故障排查

### 常见问题

1. **服务无法启动**
   - 检查端口是否被占用
   - 查看Docker/Kubernetes日志
   - 确认环境变量配置正确

2. **指标数据不显示**
   - 检查Prometheus配置
   - 确认Node Exporter正常运行
   - 查看监控服务日志

3. **Grafana无法访问**
   - 检查服务状态
   - 确认端口映射正确
   - 查看Ingress配置

### 日志位置
- 应用日志: `logs/monitoring.log`
- Docker日志: `docker-compose logs`
- Kubernetes日志: `kubectl logs`

## 📚 更多文档

- [API文档](http://localhost:8000/docs)
- [Prometheus查询语言](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Grafana仪表板配置](https://grafana.com/docs/grafana/latest/dashboards/)

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 📄 许可证

MIT License