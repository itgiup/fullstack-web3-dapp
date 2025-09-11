import React from 'react';
import { Layout, Menu, Dropdown, Avatar, Space, Button, Switch } from 'antd';
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { UserOutlined, LogoutOutlined, SunOutlined, MoonOutlined, GlobalOutlined, DownOutlined } from '@ant-design/icons';
import type { MenuProps } from 'antd';
import { useTranslation } from 'react-i18next';

const { Header, Content, Footer } = Layout;

interface AppLayoutProps {
    darkTheme: boolean;
    setDarkTheme: (dark: boolean) => void;
}

const AppLayout: React.FC<AppLayoutProps> = ({ darkTheme, setDarkTheme }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { isAuthenticated, user, logout } = useAuth();
  const { t, i18n } = useTranslation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleThemeChange = (checked: boolean) => {
    setDarkTheme(checked);
  };

  const handleLanguageChange: MenuProps['onClick'] = ({ key }) => {
    i18n.changeLanguage(key);
  };

  const languageMenuItems: MenuProps['items'] = [
    { key: 'en', label: 'English' },
    { key: 'vi', label: 'Tiếng Việt' },
  ];

  const userMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      label: <Link to="/profile">Profile</Link>,
      icon: <UserOutlined />,
    },
    {
      key: 'logout',
      label: 'Logout',
      icon: <LogoutOutlined />,
      onClick: handleLogout,
      danger: true,
    },
  ];

  const renderUserControls = () => {
    if (isAuthenticated) {
      return (
        <Dropdown menu={{ items: userMenuItems }} trigger={['click']}>
          <a onClick={(e) => e.preventDefault()}>
            <Space>
              <Avatar icon={<UserOutlined />} />
              <span>{user?.username || user?.email}</span>
            </Space>
          </a>
        </Dropdown>
      );
    }
    return (
      <Link to="/login">
        <Button type="primary">{t('login')}</Button>
      </Link>
    );
  };
  
  const canViewDashboard = user?.role === 'admin' || user?.role === 'moderator';

  const mainMenuItems: MenuProps['items'] = [
    {
      key: '/',
      label: <Link to="/">Home</Link>,
    },
    canViewDashboard && {
      key: '/dashboard',
      label: <Link to="/dashboard">Dashboard</Link>,
    },
  ].filter(Boolean); // Filter out false/null values if canViewDashboard is false

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 24px', background: darkTheme ? '#001529' : '#fff' }}>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <div className="logo" style={{ color: darkTheme ? 'white' : 'black', fontSize: '24px', marginRight: '24px' }}>
            <Link to="/" style={{ color: 'inherit', textDecoration: 'none' }}>Web3 DApp</Link>
          </div>
          <Menu
            theme={darkTheme ? 'dark' : 'light'}
            mode="horizontal"
            selectedKeys={[location.pathname]}
            style={{ flex: 1, borderBottom: 'none', background: 'transparent' }}
            items={mainMenuItems} // Use the items prop
          >
            {/* No children here */}
          </Menu>
        </div>
        <Space size="middle">
          <Switch
            checked={darkTheme}
            checkedChildren={<MoonOutlined />}
            unCheckedChildren={<SunOutlined />}
            onChange={handleThemeChange}
          />
          <Dropdown menu={{ items: languageMenuItems, onClick: handleLanguageChange }}>
            <a onClick={(e) => e.preventDefault()}>
              <Space>
                <GlobalOutlined style={{ color: darkTheme ? 'white' : 'black' }} />
                <span style={{ color: darkTheme ? 'white' : 'black' }}>{t('language')}</span>
                <DownOutlined style={{ color: darkTheme ? 'white' : 'black' }} />
              </Space>
            </a>
          </Dropdown>
          {renderUserControls()}
        </Space>
      </Header>
      <Content style={{ 
        padding: '24px', 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center',
        flexGrow: 1 
      }}>
        <Outlet />
      </Content>
      <Footer style={{ textAlign: 'center' }}>
        Web3 DApp ©2025 @itgiup
      </Footer>
    </Layout>
  );
};

export default AppLayout;
