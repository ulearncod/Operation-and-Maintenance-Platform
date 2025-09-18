import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout, Menu } from 'antd';
import {
  DashboardOutlined,
  MonitorOutlined,
  ClusterOutlined,
  AlertOutlined,
  SettingOutlined
} from '@ant-design/icons';
import Dashboard from './pages/Dashboard';
import Resources from './pages/Resources';
import Kubernetes from './pages/Kubernetes';
import Alerts from './pages/Alerts';
import Settings from './pages/Settings';

const { Header, Sider, Content } = Layout;

const App: React.FC = () => {

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
            <div style={{ color: '#666' }}>
              v1.0.0
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
              <Route path="/" element={<Dashboard />} />
              <Route path="/resources" element={<Resources />} />
              <Route path="/kubernetes" element={<Kubernetes />} />
              <Route path="/alerts" element={<Alerts />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </Content>
        </Layout>
      </Layout>
    </Router>
  );
};

export default App;