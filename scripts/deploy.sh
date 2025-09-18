#!/bin/bash

# 运维平台监控系统部署脚本
# 支持Docker Compose和Kubernetes两种部署方式

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "$1 命令未找到，请先安装 $1"
        exit 1
    fi
}

# 检查Docker环境
check_docker() {
    log_info "检查Docker环境..."
    check_command docker
    
    # 检查docker compose命令（新版本）
    if command -v docker &> /dev/null && docker compose version &> /dev/null; then
        DOCKER_COMPOSE_CMD="docker compose"
        log_info "使用新的 docker compose 命令"
    elif command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE_CMD="docker-compose"
        log_info "使用传统的 docker-compose 命令"
    else
        log_error "未找到 docker compose 或 docker-compose 命令，请先安装 Docker Compose"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker守护进程未运行，请启动Docker"
        exit 1
    fi
    
    log_success "Docker环境检查通过"
}

# 检查Kubernetes环境
check_kubernetes() {
    log_info "检查Kubernetes环境..."
    check_command kubectl
    check_command helm
    
    if ! kubectl cluster-info &> /dev/null; then
        log_error "无法连接到Kubernetes集群，请检查kubeconfig配置"
        exit 1
    fi
    
    log_success "Kubernetes环境检查通过"
}

# Docker Compose部署
deploy_docker() {
    log_info "开始Docker Compose部署..."
    
    # 创建必要的目录
    mkdir -p logs
    mkdir -p data/{postgres,redis,prometheus,grafana,alertmanager}
    
    # 构建镜像
    log_info "构建监控服务镜像..."
    docker build -t devops-platform/monitoring-service:latest -f docker/Dockerfile .
    
    # 启动服务
    log_info "启动所有服务..."
    $DOCKER_COMPOSE_CMD -f docker/docker-compose.yml up -d
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 30
    
    # 检查服务状态
    if $DOCKER_COMPOSE_CMD -f docker/docker-compose.yml ps | grep -q "Up"; then
        log_success "Docker Compose部署完成"
        log_info "服务访问地址："
        log_info "  - 前端界面: http://localhost"
        log_info "  - 监控API: http://localhost:8000"
        log_info "  - Grafana: http://localhost:3000 (admin/admin123)"
        log_info "  - Prometheus: http://localhost:9090"
        log_info "  - Nginx代理: http://localhost"
    else
        log_error "服务启动失败，请检查日志"
        $DOCKER_COMPOSE_CMD -f docker/docker-compose.yml logs
        exit 1
    fi
}

# Kubernetes部署
deploy_kubernetes() {
    log_info "开始Kubernetes部署..."
    
    # 创建命名空间
    log_info "创建monitoring命名空间..."
    kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -
    
    # 安装Prometheus Operator
    log_info "安装Prometheus Operator..."
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo add grafana https://grafana.github.io/helm-charts
    helm repo update
    
    # 安装Prometheus
    helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
        --namespace monitoring \
        --set prometheus.prometheusSpec.retention=30d \
        --set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage=50Gi \
        --set grafana.adminPassword=prom-operator \
        --set grafana.persistence.enabled=true \
        --set grafana.persistence.size=10Gi
    
    # 部署监控服务
    log_info "部署监控服务..."
    kubectl apply -f k8s/monitoring-service.yaml
    
    # 部署Node Exporter
    log_info "部署Node Exporter..."
    kubectl apply -f k8s/node-exporter.yaml
    
    # 部署kube-state-metrics
    log_info "部署kube-state-metrics..."
    kubectl apply -f k8s/kube-state-metrics.yaml
    
    # 部署Grafana配置
    log_info "部署Grafana配置..."
    kubectl apply -f k8s/grafana/
    
    # 等待Pod就绪
    log_info "等待Pod就绪..."
    kubectl wait --for=condition=ready pod -l app=monitoring-service -n monitoring --timeout=300s
    
    log_success "Kubernetes部署完成"
    log_info "获取服务访问地址："
    kubectl get svc -n monitoring
}

# 停止服务
stop_services() {
    log_info "停止服务..."
    
    if [ "$DEPLOY_MODE" = "docker" ]; then
        $DOCKER_COMPOSE_CMD -f docker/docker-compose.yml down
        log_success "Docker服务已停止"
    elif [ "$DEPLOY_MODE" = "kubernetes" ]; then
        kubectl delete -f k8s/ --ignore-not-found=true
        helm uninstall prometheus -n monitoring --ignore-not-found
        log_success "Kubernetes服务已停止"
    fi
}

# 清理数据
clean_data() {
    log_warning "这将删除所有数据，包括数据库和配置文件"
    read -p "确定要继续吗？(y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ "$DEPLOY_MODE" = "docker" ]; then
            $DOCKER_COMPOSE_CMD -f docker/docker-compose.yml down -v
            docker system prune -f
        elif [ "$DEPLOY_MODE" = "kubernetes" ]; then
            kubectl delete pvc --all -n monitoring
            kubectl delete namespace monitoring
        fi
        log_success "数据清理完成"
    else
        log_info "取消清理操作"
    fi
}

# 显示帮助信息
show_help() {
    echo "运维平台监控系统部署脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -m, --mode MODE     部署模式 (docker|kubernetes)"
    echo "  -d, --deploy        部署服务"
    echo "  -s, --stop          停止服务"
    echo "  -c, --clean         清理数据"
    echo "  -h, --help          显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 -m docker -d     # 使用Docker Compose部署"
    echo "  $0 -m kubernetes -d # 使用Kubernetes部署"
    echo "  $0 -m docker -s     # 停止Docker服务"
    echo "  $0 -m docker -c     # 清理Docker数据"
}

# 主函数
main() {
    DEPLOY_MODE=""
    ACTION=""
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -m|--mode)
                DEPLOY_MODE="$2"
                shift 2
                ;;
            -d|--deploy)
                ACTION="deploy"
                shift
                ;;
            -s|--stop)
                ACTION="stop"
                shift
                ;;
            -c|--clean)
                ACTION="clean"
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 检查参数
    if [ -z "$DEPLOY_MODE" ] || [ -z "$ACTION" ]; then
        log_error "缺少必要参数"
        show_help
        exit 1
    fi
    
    if [ "$DEPLOY_MODE" != "docker" ] && [ "$DEPLOY_MODE" != "kubernetes" ]; then
        log_error "不支持的部署模式: $DEPLOY_MODE"
        exit 1
    fi
    
    # 执行操作
    case $ACTION in
        deploy)
            if [ "$DEPLOY_MODE" = "docker" ]; then
                check_docker
                deploy_docker
            elif [ "$DEPLOY_MODE" = "kubernetes" ]; then
                check_kubernetes
                deploy_kubernetes
            fi
            ;;
        stop)
            stop_services
            ;;
        clean)
            clean_data
            ;;
        *)
            log_error "未知操作: $ACTION"
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"