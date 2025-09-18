import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Statistic, Spin, Alert } from 'antd';
import { 
  DesktopOutlined,
  HddOutlined,
  DatabaseOutlined, 
  GlobalOutlined,
  ClusterOutlined,
  AlertOutlined
} from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import { monitoringAPI } from '../services/api';

interface SystemSummary {
  timestamp: string;
  system: {
    cpu_usage: number;
    memory_usage: number;
    disk_usage: number;
    process_count: number;
  };
  status: string;
}

const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [summary, setSummary] = useState<SystemSummary | null>(null);
  const [cpuData, setCpuData] = useState<any[]>([]);
  const [memoryData, setMemoryData] = useState<any[]>([]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [summaryRes, cpuRes, memoryRes] = await Promise.all([
        monitoringAPI.getSummary(),
        monitoringAPI.getCPU(),
        monitoringAPI.getMemory()
      ]);
      
      setSummary(summaryRes.data);
      
      // 模拟时间序列数据（实际应该从Prometheus获取）
      const now = new Date();
      setCpuData([
        { time: new Date(now.getTime() - 300000).toISOString(), value: cpuRes.data.cpu?.usage_percent || 0 },
        { time: new Date(now.getTime() - 240000).toISOString(), value: (cpuRes.data.cpu?.usage_percent || 0) + Math.random() * 10 },
        { time: new Date(now.getTime() - 180000).toISOString(), value: (cpuRes.data.cpu?.usage_percent || 0) + Math.random() * 10 },
        { time: new Date(now.getTime() - 120000).toISOString(), value: (cpuRes.data.cpu?.usage_percent || 0) + Math.random() * 10 },
        { time: new Date(now.getTime() - 60000).toISOString(), value: (cpuRes.data.cpu?.usage_percent || 0) + Math.random() * 10 },
        { time: now.toISOString(), value: cpuRes.data.cpu?.usage_percent || 0 }
      ]);
      
      setMemoryData([
        { time: new Date(now.getTime() - 300000).toISOString(), value: memoryRes.data.memory?.virtual?.percent || 0 },
        { time: new Date(now.getTime() - 240000).toISOString(), value: (memoryRes.data.memory?.virtual?.percent || 0) + Math.random() * 5 },
        { time: new Date(now.getTime() - 180000).toISOString(), value: (memoryRes.data.memory?.virtual?.percent || 0) + Math.random() * 5 },
        { time: new Date(now.getTime() - 120000).toISOString(), value: (memoryRes.data.memory?.virtual?.percent || 0) + Math.random() * 5 },
        { time: new Date(now.getTime() - 60000).toISOString(), value: (memoryRes.data.memory?.virtual?.percent || 0) + Math.random() * 5 },
        { time: now.toISOString(), value: memoryRes.data.memory?.virtual?.percent || 0 }
      ]);
      
    } catch (err) {
      setError('获取监控数据失败');
      console.error('Dashboard fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000); // 每10秒刷新
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (value: number, type: string) => {
    if (type === 'cpu' || type === 'memory' || type === 'disk') {
      if (value > 90) return '#ff4d4f';
      if (value > 80) return '#faad14';
      return '#52c41a';
    }
    return '#1890ff';
  };

  const chartOption = (data: any[], title: string, color: string) => ({
    title: {
      text: title,
      left: 'center',
      textStyle: { fontSize: 14 }
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const point = params[0];
        return `${point.axisValue}<br/>${point.seriesName}: ${point.value.toFixed(2)}%`;
      }
    },
    xAxis: {
      type: 'category',
      data: data.map(item => new Date(item.time).toLocaleTimeString()),
      axisLabel: { fontSize: 10 }
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100,
      axisLabel: { formatter: '{value}%' }
    },
    series: [{
      name: title,
      type: 'line',
      data: data.map(item => item.value),
      smooth: true,
      lineStyle: { color },
      areaStyle: { 
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: color + '40' },
            { offset: 1, color: color + '10' }
          ]
        }
      }
    }],
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    }
  });

  if (loading && !summary) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <div style={{ marginTop: 16 }}>加载监控数据中...</div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert
        message="数据加载失败"
        description={error}
        type="error"
        showIcon
        action={
          <button onClick={fetchData} style={{ marginLeft: 16 }}>
            重试
          </button>
        }
      />
    );
  }

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>系统监控仪表盘</h1>
      
      {/* 概览卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="CPU使用率"
              value={summary?.system.cpu_usage || 0}
              precision={1}
              suffix="%"
              valueStyle={{ color: getStatusColor(summary?.system.cpu_usage || 0, 'cpu') }}
              prefix={<DesktopOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="内存使用率"
              value={summary?.system.memory_usage || 0}
              precision={1}
              suffix="%"
              valueStyle={{ color: getStatusColor(summary?.system.memory_usage || 0, 'memory') }}
              prefix={<HddOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="磁盘使用率"
              value={summary?.system.disk_usage || 0}
              precision={1}
              suffix="%"
              valueStyle={{ color: getStatusColor(summary?.system.disk_usage || 0, 'disk') }}
              prefix={<DatabaseOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="进程数量"
              value={summary?.system.process_count || 0}
              valueStyle={{ color: '#1890ff' }}
              prefix={<ClusterOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* 趋势图表 */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card title="CPU使用率趋势" className="chart-container">
            <ReactECharts
              option={chartOption(cpuData, 'CPU使用率', '#1890ff')}
              style={{ height: '300px' }}
            />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="内存使用率趋势" className="chart-container">
            <ReactECharts
              option={chartOption(memoryData, '内存使用率', '#52c41a')}
              style={{ height: '300px' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 系统状态 */}
      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col span={24}>
          <Card title="系统状态">
            <Row gutter={[16, 16]}>
              <Col xs={24} sm={8}>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 24, color: '#52c41a' }}>
                    <GlobalOutlined />
                  </div>
                  <div style={{ marginTop: 8 }}>网络状态</div>
                  <div style={{ color: '#52c41a', fontWeight: 'bold' }}>正常</div>
                </div>
              </Col>
              <Col xs={24} sm={8}>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 24, color: '#52c41a' }}>
                    <DatabaseOutlined />
                  </div>
                  <div style={{ marginTop: 8 }}>存储状态</div>
                  <div style={{ color: '#52c41a', fontWeight: 'bold' }}>正常</div>
                </div>
              </Col>
              <Col xs={24} sm={8}>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 24, color: '#52c41a' }}>
                    <AlertOutlined />
                  </div>
                  <div style={{ marginTop: 8 }}>告警状态</div>
                  <div style={{ color: '#52c41a', fontWeight: 'bold' }}>无告警</div>
                </div>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;