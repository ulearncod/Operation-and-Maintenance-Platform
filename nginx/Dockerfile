# ---------------------------------------------
# Stage 1: Build frontend
# ---------------------------------------------
FROM node:16.20.2-alpine AS frontend-build

WORKDIR /app

# Copy package files and install deps
COPY frontend/package*.json ./
RUN npm config set registry https://registry.npmmirror.com \
    && npm config set fetch-timeout 120000 \
    && npm config set fetch-retries 5 \
    && npm cache clean --force \
    && npm install --legacy-peer-deps --no-audit --no-fund --force

# Copy source and build
COPY frontend/ .
ENV NODE_OPTIONS="--max-old-space-size=4096"
ENV GENERATE_SOURCEMAP=false
ENV REACT_APP_API_URL=""
RUN npm run build

# ---------------------------------------------
# Stage 2: Nginx runtime
# ---------------------------------------------
FROM nginx:1.25.5-alpine

# Copy frontend build into nginx html root
COPY --from=frontend-build /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx/nginx.conf /etc/nginx/nginx.conf

# Prepare logs dir
RUN mkdir -p /var/log/nginx

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]