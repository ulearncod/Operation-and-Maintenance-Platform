import React, { useState, useEffect } from 'react';
import { Card, Table, Tag, Row, Col, Statistic, Tabs } from 'antd';
import { monitoringAPI } from '../services/api';

interface PodData {
  key: string;
  name: string;
  namespace: string;
  status: string;
  restarts: number;
  age: string;
  cpu: number;
  memory: number;
}

interface NodeData {
  key: string;
  name: string;
  status: string;
  role: string;
  version: string;
  cpu: number;
  memory: number;
  pods: number;
}

const Kubernetes: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [pods, setPods] = useState<PodData[]>([]);
  const [nodes, setNodes] = useState<NodeData[]>([]);

  useEffect(() => {
    fetchK8sData();
    const interval = setInterval(fetchK8sData, 15000);
    return () => clearInterval(interval);
  }, []);

  const fetchK8sData = async () => {
    try {
      setLoading(true);
      
      // 模拟K8s数据（实际应该从kube-state-metrics获取）
      const mockPods: PodData[] = [
        {
          key: 'pod-1',
          name: 'nginx-deployment-7d4f8b8c9c-abc12',
          namespace: 'default',
          status: 'Running',
          restarts: 0,
          age: '2d',
          cpu: 0.1,
          memory: 12.5
        },
        {
          key: 'pod-2',
          name: 'redis-master-0',
          namespace: 'default',
          status: 'Running',
          restarts: 1,
          age: '5d',
          cpu: 0.3,
          memory: 45.2
        },
        {
          key: 'pod-3',
          name: 'monitoring-service-7d4f8b8c9c-def34',
          namespace: 'monitoring',
          status: 'Running',
          restarts: 0,
          age: '1d',
          cpu: 0.2,
          memory: 28.7
        }
      ];

      const mockNodes: NodeData[] = [
        {
          key: 'node-1',
          name: 'master-node-1',
          status: 'Ready',
          role: 'master',
          version: 'v1.28.0',
          cpu: 15.2,
          memory: 45.8,
          pods: 8
        },
        {
          key: 'node-2',
          name: 'worker-node-1',
          status: 'Ready',
          role: 'worker',
          version: 'v1.28.0',
          cpu: 22.1,
          memory: 67.3,
          pods: 12
        }
      ];

      setPods(mockPods);
      setNodes(mockNodes);
    } catch (error) {
      console.error('Failed to fetch K8s data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'running':
      case 'ready':
        return 'green';
      case 'pending':
        return 'orange';
      case 'failed':
      case 'notready':
        return 'red';
      default:
        return 'default';
    }
  };

  const podColumns = [
    {
      title: 'Pod名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '命名空间',
      dataIndex: 'namespace',
      key: 'namespace',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={getStatusColor(status)}>
          {status}
        </Tag>
      ),
    },
    {
      title: '重启次数',
      dataIndex: 'restarts',
      key: 'restarts',
    },
    {
      title: '运行时间',
      dataIndex: 'age',
      key: 'age',
    },
    {
      title: 'CPU使用',
      dataIndex: 'cpu',
      key: 'cpu',
      render: (value: number) => `${value.toFixed(2)} cores`,
    },
    {
      title: '内存使用',
      dataIndex: 'memory',
      key: 'memory',
      render: (value: number) => `${value.toFixed(1)} Mi`,
    },
  ];

  const nodeColumns = [
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
          {status}
        </Tag>
      ),
    },
    {
      title: '角色',
      dataIndex: 'role',
      key: 'role',
      render: (role: string) => (
        <Tag color={role === 'master' ? 'blue' : 'default'}>
          {role}
        </Tag>
      ),
    },
    {
      title: '版本',
      dataIndex: 'version',
      key: 'version',
    },
    {
      title: 'CPU使用率',
      dataIndex: 'cpu',
      key: 'cpu',
      render: (value: number) => `${value.toFixed(1)}%`,
    },
    {
      title: '内存使用率',
      dataIndex: 'memory',
      key: 'memory',
      render: (value: number) => `${value.toFixed(1)}%`,
    },
    {
      title: 'Pod数量',
      dataIndex: 'pods',
      key: 'pods',
    },
  ];

  const tabItems = [
    {
      key: 'pods',
      label: 'Pod管理',
      children: (
        <Table
          columns={podColumns}
          dataSource={pods}
          loading={loading}
          pagination={{ pageSize: 10 }}
          rowKey="key"
        />
      ),
    },
    {
      key: 'nodes',
      label: '节点管理',
      children: (
        <Table
          columns={nodeColumns}
          dataSource={nodes}
          loading={loading}
          pagination={false}
          rowKey="key"
        />
      ),
    },
  ];

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>Kubernetes集群管理</h1>
      
      {/* 集群概览 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="总节点数"
              value={nodes.length}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="总Pod数"
              value={pods.length}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="运行中Pod"
              value={pods.filter(p => p.status === 'Running').length}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="异常Pod"
              value={pods.filter(p => p.status !== 'Running').length}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Pod和节点管理 */}
      <Card>
        <Tabs defaultActiveKey="pods" items={tabItems} />
      </Card>
    </div>
  );
};

export default Kubernetes;