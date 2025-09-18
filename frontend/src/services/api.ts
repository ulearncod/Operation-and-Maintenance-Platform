import axios from 'axios';
import { getToken, removeToken } from './auth';

const API_BASE_URL = process.env.REACT_APP_API_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers = config.headers || {};
      (config.headers as any)['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    // 保持与页面中 res.data.xxx 的访问方式一致，返回完整响应对象
    return response;
  },
  (error) => {
    if (error?.response?.status === 401) {
      removeToken();
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// API接口定义
export const monitoringAPI = {
  // 获取系统概览
  getSummary: () => api.get('/api/v1/monitoring/system/overview'),
  
  // 获取CPU指标
  getCPU: () => api.get('/api/v1/monitoring/system/cpu'),
  
  // 获取内存指标
  getMemory: () => api.get('/api/v1/monitoring/system/memory'),
  
  // 获取磁盘指标
  getDisk: () => api.get('/api/v1/monitoring/system/disk'),
  
  // 获取网络指标
  getNetwork: () => api.get('/api/v1/monitoring/system/network'),
  
  // 获取进程指标
  getProcesses: () => api.get('/api/v1/monitoring/system/processes'),
  
  // 获取告警信息
  getAlerts: () => api.get('/api/v1/monitoring/alerts'),
  
  // Prometheus查询
  queryPrometheus: (query: string, start?: string, end?: string, step?: string) => 
    api.post('/api/v1/prometheus/query', { query, start, end, step }),
};

export default api;