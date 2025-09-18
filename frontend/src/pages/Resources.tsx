import React, { useState, useEffect } from 'react';
import { Card, Table, Tag, Progress, Row, Col, Statistic } from 'antd';
import { monitoringAPI } from '../services/api';

interface ResourceData {
  key: string;
  name: string;
  cpu: number;
  memory: number;
  disk: number;
  status: 'healthy' | 'warning' | 'critical';
}

const Resources: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [resources, setResources] = useState<ResourceData[]>([]);

  useEffect(() => {
    fetchResources();
    const interval = setInterval(fetchResources, 15000);
    return () => clearInterval(interval);
  }, []);

  const fetchResources = async () => {
    try {
      setLoading(true);
      const [cpuRes, memoryRes, diskRes] = await Promise.all([
        monitoringAPI.getCPU(),
        monitoringAPI.getMemory(),
        monitoringAPI.getDisk()
      ]);

      // 模拟多节点数据
      const mockResources: ResourceData[] = [
        {
          key: 'node-1',
          name: '主节点-1',
          cpu: cpuRes.data.cpu?.usage_percent || 0,
          memory: memoryRes.data.memory?.virtual?.percent || 0,
          disk: diskRes.data.disk?.root?.percent || 0,
          status: getStatus(cpuRes.data.cpu?.usage_percent || 0, memoryRes.data.memory?.virtual?.percent || 0, diskRes.data.disk?.root?.percent || 0)
        },
        {
          key: 'node-2',
          name: '工作节点-1',
          cpu: (cpuRes.data.cpu?.usage_percent || 0) + Math.random() * 20,
          memory: (memoryRes.data.memory?.virtual?.percent || 0) + Math.random() * 15,
          disk: (diskRes.data.disk?.root?.percent || 0) + Math.random() * 10,
          status: getStatus((cpuRes.data.cpu?.usage_percent || 0) + Math.random() * 20, (memoryRes.data.memory?.virtual?.percent || 0) + Math.random() * 15, (diskRes.data.disk?.root?.percent || 0) + Math.random() * 10)
        }
      ];

      setResources(mockResources);
    } catch (error) {
      console.error('Failed to fetch resources:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatus = (cpu: number, memory: number, disk: number): 'healthy' | 'warning' | 'critical' => {
    if (cpu > 90 || memory > 90 || disk > 90) return 'critical';
    if (cpu > 80 || memory > 80 || disk > 80) return 'warning';
    return 'healthy';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'green';
      case 'warning': return 'orange';
      case 'critical': return 'red';
      default: return 'default';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'healthy': return '健康';
      case 'warning': return '警告';
      case 'critical': return '严重';
      default: return '未知';
    }
  };

  const columns = [
    {
      title: '节点名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={getStatusColor(status)}>
          {getStatusText(status)}
        </Tag>
      ),
    },
    {
      title: 'CPU使用率',
      dataIndex: 'cpu',
      key: 'cpu',
      render: (value: number) => (
        <div>
          <Progress 
            percent={value} 
            size="small" 
            status={value > 90 ? 'exception' : value > 80 ? 'active' : 'normal'}
            strokeColor={value > 90 ? '#ff4d4f' : value > 80 ? '#faad14' : '#52c41a'}
          />
          <span style={{ marginLeft: 8 }}>{value.toFixed(1)}%</span>
        </div>
      ),
    },
    {
      title: '内存使用率',
      dataIndex: 'memory',
      key: 'memory',
      render: (value: number) => (
        <div>
          <Progress 
            percent={value} 
            size="small" 
            status={value > 90 ? 'exception' : value > 80 ? 'active' : 'normal'}
            strokeColor={value > 90 ? '#ff4d4f' : value > 80 ? '#faad14' : '#52c41a'}
          />
          <span style={{ marginLeft: 8 }}>{value.toFixed(1)}%</span>
        </div>
      ),
    },
    {
      title: '磁盘使用率',
      dataIndex: 'disk',
      key: 'disk',
      render: (value: number) => (
        <div>
          <Progress 
            percent={value} 
            size="small" 
            status={value > 90 ? 'exception' : value > 80 ? 'active' : 'normal'}
            strokeColor={value > 90 ? '#ff4d4f' : value > 80 ? '#faad14' : '#52c41a'}
          />
          <span style={{ marginLeft: 8 }}>{value.toFixed(1)}%</span>
        </div>
      ),
    },
  ];

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>资源监控</h1>
      
      {/* 资源概览 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="总节点数"
              value={resources.length}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="健康节点"
              value={resources.filter(r => r.status === 'healthy').length}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="异常节点"
              value={resources.filter(r => r.status !== 'healthy').length}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 资源列表 */}
      <Card title="节点资源详情">
        <Table
          columns={columns}
          dataSource={resources}
          loading={loading}
          pagination={false}
          rowKey="key"
        />
      </Card>
    </div>
  );
};

export default Resources;