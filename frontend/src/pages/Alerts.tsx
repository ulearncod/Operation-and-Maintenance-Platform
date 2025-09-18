import React, { useState, useEffect } from 'react';
import { Card, Table, Tag, Button, Space, Alert } from 'antd';
import { monitoringAPI } from '../services/api';

interface AlertData {
  key: string;
  name: string;
  severity: 'critical' | 'warning' | 'info';
  status: 'firing' | 'resolved';
  description: string;
  instance: string;
  startTime: string;
  endTime?: string;
}

const Alerts: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [alerts, setAlerts] = useState<AlertData[]>([]);

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const response = await monitoringAPI.getAlerts();
      
      // 模拟告警数据（AlertManager暂时禁用）
      const mockAlerts: AlertData[] = [
        {
          key: 'alert-1',
          name: 'HighCPUUsage',
          severity: 'warning',
          status: 'firing',
          description: 'CPU使用率超过80%',
          instance: 'node-1',
          startTime: new Date(Date.now() - 300000).toISOString(),
        },
        {
          key: 'alert-2',
          name: 'HighMemoryUsage',
          severity: 'critical',
          status: 'firing',
          description: '内存使用率超过95%',
          instance: 'node-2',
          startTime: new Date(Date.now() - 600000).toISOString(),
        },
        {
          key: 'alert-3',
          name: 'PodCrashLooping',
          severity: 'warning',
          status: 'resolved',
          description: 'Pod重启循环',
          instance: 'pod-nginx-abc123',
          startTime: new Date(Date.now() - 1800000).toISOString(),
          endTime: new Date(Date.now() - 900000).toISOString(),
        }
      ];

      setAlerts(mockAlerts);
    } catch (error) {
      console.error('Failed to fetch alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'red';
      case 'warning': return 'orange';
      case 'info': return 'blue';
      default: return 'default';
    }
  };

  const getStatusColor = (status: string) => {
    return status === 'firing' ? 'red' : 'green';
  };

  const getStatusText = (status: string) => {
    return status === 'firing' ? '告警中' : '已解决';
  };

  const columns = [
    {
      title: '告警名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '严重程度',
      dataIndex: 'severity',
      key: 'severity',
      render: (severity: string) => (
        <Tag color={getSeverityColor(severity)}>
          {severity.toUpperCase()}
        </Tag>
      ),
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
      title: '描述',
      dataIndex: 'description',
      key: 'description',
    },
    {
      title: '实例',
      dataIndex: 'instance',
      key: 'instance',
    },
    {
      title: '开始时间',
      dataIndex: 'startTime',
      key: 'startTime',
      render: (time: string) => new Date(time).toLocaleString(),
    },
    {
      title: '结束时间',
      dataIndex: 'endTime',
      key: 'endTime',
      render: (time: string) => time ? new Date(time).toLocaleString() : '-',
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: AlertData) => (
        <Space size="middle">
          <Button type="link" size="small">
            查看详情
          </Button>
          {record.status === 'firing' && (
            <Button type="link" size="small" danger>
              静默
            </Button>
          )}
        </Space>
      ),
    },
  ];

  const activeAlerts = alerts.filter(alert => alert.status === 'firing');
  const resolvedAlerts = alerts.filter(alert => alert.status === 'resolved');

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>告警管理</h1>
      
      {/* 告警概览 */}
      <div style={{ marginBottom: 24 }}>
        <Alert
          message="AlertManager服务暂时禁用"
          description="当前告警数据为模拟数据，实际告警功能需要启用AlertManager服务。"
          type="warning"
          showIcon
          style={{ marginBottom: 16 }}
        />
      </div>

      {/* 告警统计 */}
      <div style={{ marginBottom: 24 }}>
        <Space size="large">
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: 24, color: '#ff4d4f', fontWeight: 'bold' }}>
              {activeAlerts.length}
            </div>
            <div>活跃告警</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: 24, color: '#faad14', fontWeight: 'bold' }}>
              {activeAlerts.filter(a => a.severity === 'warning').length}
            </div>
            <div>警告级别</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: 24, color: '#ff4d4f', fontWeight: 'bold' }}>
              {activeAlerts.filter(a => a.severity === 'critical').length}
            </div>
            <div>严重级别</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: 24, color: '#52c41a', fontWeight: 'bold' }}>
              {resolvedAlerts.length}
            </div>
            <div>已解决</div>
          </div>
        </Space>
      </div>

      {/* 告警列表 */}
      <Card title="告警列表">
        <Table
          columns={columns}
          dataSource={alerts}
          loading={loading}
          pagination={{ pageSize: 10 }}
          rowKey="key"
        />
      </Card>
    </div>
  );
};

export default Alerts;