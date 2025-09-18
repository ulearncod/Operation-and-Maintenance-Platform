# 多阶段构建 - 构建阶段
FROM python:3.11-slim AS builder

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY backend/requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir --user -r requirements.txt

# 运行阶段
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 创建非root用户
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 从构建阶段复制Python包
COPY --from=builder /root/.local /home/appuser/.local

# 复制应用代码
COPY backend/ .

# 创建日志目录
RUN mkdir -p logs && chown -R appuser:appuser /app

# 切换到非root用户
USER appuser

# 设置环境变量
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 8000

# 健康检查：使用 Python 内置库（一行脚本），避免依赖 curl/wget
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD python -c "import sys,urllib.request;\
import urllib.error;\
import socket;\
url='http://localhost:8000/health';\
\
try:\
    resp=urllib.request.urlopen(url, timeout=5);\
    sys.exit(0 if getattr(resp,'status',resp.getcode())==200 else 1)\
except Exception:\
    sys.exit(1)"

# 启动命令
CMD ["python", "main.py"]