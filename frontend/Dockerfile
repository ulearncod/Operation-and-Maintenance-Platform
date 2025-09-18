# 构建阶段
FROM node:16.20.2-alpine AS build

WORKDIR /app

# 复制package文件
COPY package*.json ./

# 配置npm镜像与超时，提升稳定性
RUN npm config set registry https://registry.npmmirror.com \
    && npm config set fetch-timeout 120000 \
    && npm config set fetch-retries 5

# 清理npm缓存并安装依赖
RUN npm cache clean --force \
    && npm install --legacy-peer-deps --no-audit --no-fund --force

# 复制源代码
COPY . .

# 设置环境变量
ENV NODE_OPTIONS="--max-old-space-size=4096"
ENV GENERATE_SOURCEMAP=false
ENV REACT_APP_API_URL=""

# 构建应用
RUN npm run build

# 生产阶段
FROM nginx:1.25.5-alpine

# 复制构建的文件到nginx
COPY --from=build /app/build /usr/share/nginx/html

# 复制nginx配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动nginx
CMD ["nginx", "-g", "daemon off;"]