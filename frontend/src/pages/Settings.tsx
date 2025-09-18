import React, { useState } from 'react';
import { Card, Form, Input, Button, Switch, InputNumber, message, Divider } from 'antd';
import api from '../services/api';
import { useAuth } from '../hooks/useAuth';

const Settings: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const { isAdmin } = useAuth();

  const onFinish = (values: any) => {
    setLoading(true);
    // 模拟保存设置
    setTimeout(() => {
      message.success('设置保存成功');
      setLoading(false);
    }, 1000);
  };

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>系统设置</h1>

      <Card title="监控配置" style={{ marginBottom: 16 }}>
        <Form
          form={form}
          layout="vertical"
          onFinish={onFinish}
          initialValues={{
            refreshInterval: 10,
            prometheusUrl: 'http://localhost:9090',
            grafanaUrl: 'http://localhost:3000',
            alertManagerUrl: 'http://localhost:9093',
            enableAlerts: false,
            emailNotifications: true,
            webhookNotifications: true,
          }}
        >
          <Form.Item
            label="数据刷新间隔（秒）"
            name="refreshInterval"
            rules={[{ required: true, message: '请输入刷新间隔' }]}
          >
            <InputNumber min={5} max={300} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            label="Prometheus地址"
            name="prometheusUrl"
            rules={[{ required: true, message: '请输入Prometheus地址' }]}
          >
            <Input placeholder="http://localhost:9090" />
          </Form.Item>

          <Form.Item
            label="Grafana地址"
            name="grafanaUrl"
            rules={[{ required: true, message: '请输入Grafana地址' }]}
          >
            <Input placeholder="http://localhost:3000" />
          </Form.Item>

          <Form.Item
            label="AlertManager地址"
            name="alertManagerUrl"
          >
            <Input placeholder="http://localhost:9093" />
          </Form.Item>

          <Divider />

          <h3>通知设置</h3>
          
          <Form.Item
            label="启用告警通知"
            name="enableAlerts"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Form.Item
            label="邮件通知"
            name="emailNotifications"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Form.Item
            label="Webhook通知"
            name="webhookNotifications"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading}>
              保存设置
            </Button>
          </Form.Item>
        </Form>
      </Card>

      {isAdmin() && (
        <Card title="用户管理（仅管理员）" style={{ marginBottom: 16 }}>
        <Form
          layout="vertical"
          onFinish={async (values) => {
            try {
              await api.post('/api/v1/auth/users', values);
              message.success('用户创建成功');
            } catch (e: any) {
              const detail = e?.response?.data?.detail || '创建失败';
              if (e?.response?.status === 403) {
                message.error('无权限：需要管理员角色');
              } else {
                message.error(detail);
              }
            }
          }}
        >
          <Form.Item label="用户名" name="username" rules={[{ required: true, message: '请输入用户名' }]}>
            <Input allowClear />
          </Form.Item>
          <Form.Item label="邮箱" name="email" rules={[{ type: 'email', message: '请输入正确的邮箱' }]}>
            <Input allowClear />
          </Form.Item>
          <Form.Item label="初始密码" name="password" rules={[{ required: true, message: '请输入初始密码' }]}>
            <Input.Password />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit">创建用户</Button>
          </Form.Item>
        </Form>
      </Card>
      )}

      <Card title="系统信息">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16 }}>
          <div>
            <strong>系统版本:</strong> v1.0.0
          </div>
          <div>
            <strong>构建时间:</strong> 2025-09-17
          </div>
          <div>
            <strong>运行环境:</strong> Docker
          </div>
          <div>
            <strong>API地址:</strong> {process.env.REACT_APP_API_URL || window.location.origin}/api
          </div>
        </div>
      </Card>
    </div>
  );
};

export default Settings;