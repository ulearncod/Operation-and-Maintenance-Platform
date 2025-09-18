import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout, Menu, Avatar, Dropdown, Space } from 'antd';
import {
  DashboardOutlined,
  MonitorOutlined,
  ClusterOutlined,
  AlertOutlined,
  SettingOutlined,
  UserOutlined,
  LogoutOutlined
} from '@ant-design/icons';
import Dashboard from './pages/Dashboard';
import Resources from './pages/Resources';
import Kubernetes from './pages/Kubernetes';
import Alerts from './pages/Alerts';
import Settings from './pages/Settings';
import Login from './pages/Login';
import Register from './pages/Register';
import ProtectedRoute from './components/ProtectedRoute';
import { isAuthenticated, removeToken } from './services/auth';
import { useAuth } from './hooks/useAuth';

const { Header, Sider, Content } = Layout;

const App: React.FC = () => {
  const { user, isAdmin } = useAuth();

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: '仪表盘',
    },
    {
      key: '/resources',
      icon: <MonitorOutlined />,
      label: '资源监控',
    },
    {
      key: '/kubernetes',
      icon: <ClusterOutlined />,
      label: 'Kubernetes',
    },
    {
      key: '/alerts',
      icon: <AlertOutlined />,
      label: '告警管理',
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: '系统设置',
    },
  ];

  return (
    <Router>
      <Layout style={{ minHeight: '100vh' }}>
        <Sider
          breakpoint="lg"
          collapsedWidth="0"
          style={{
            background: '#fff',
          }}
        >
          <div style={{ 
            height: 32, 
            margin: 16, 
            background: 'rgba(255, 255, 255, 0.2)',
            borderRadius: 6,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 'bold',
            color: '#1890ff'
          }}>
            运维监控
          </div>
          <Menu
            mode="inline"
            defaultSelectedKeys={['/']}
            items={menuItems}
            onClick={({ key }) => {
              window.location.href = key;
            }}
          />
        </Sider>
        <Layout>
          <Header style={{ 
            padding: 0, 
            background: '#fff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            paddingRight: 24
          }}>
            <div style={{ 
              fontSize: 18, 
              fontWeight: 'bold',
              marginLeft: 24,
              color: '#1890ff'
            }}>
              运维平台监控系统
            </div>
            <div style={{ color: '#666', display: 'flex', gap: 12, alignItems: 'center' }}>
              <span>v1.0.0</span>
              {isAuthenticated() && user ? (
                <Dropdown
                  menu={{
                    items: [
                      {
                        key: 'user-info',
                        label: (
                          <div>
                            <div><strong>{user.username}</strong></div>
                            <div style={{ fontSize: '12px', color: '#999' }}>
                              {user.roles?.join(', ') || 'user'}
                            </div>
                          </div>
                        ),
                        disabled: true,
                      },
                      { type: 'divider' },
                      {
                        key: 'logout',
                        label: '退出登录',
                        icon: <LogoutOutlined />,
                        onClick: () => { removeToken(); window.location.href = '/login'; }
                      }
                    ]
                  }}
                  trigger={['click']}
                >
                  <Space style={{ cursor: 'pointer' }}>
                    <Avatar size="small" icon={<UserOutlined />} />
                    <span>{user.username}</span>
                  </Space>
                </Dropdown>
              ) : null}
            </div>
          </Header>
          <Content
            style={{
              margin: '16px',
              padding: 24,
              minHeight: 280,
              background: '#fff',
              borderRadius: 6,
            }}
          >
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
              <Route path="/resources" element={<ProtectedRoute><Resources /></ProtectedRoute>} />
              <Route path="/kubernetes" element={<ProtectedRoute><Kubernetes /></ProtectedRoute>} />
              <Route path="/alerts" element={<ProtectedRoute><Alerts /></ProtectedRoute>} />
              <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
            </Routes>
          </Content>
        </Layout>
      </Layout>
    </Router>
  );
};

export default App;