import React, { useState } from 'react';
import { Layout, Menu, Dropdown, Avatar, Space, Button, Switch, Typography, Grid, Drawer } from 'antd';
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { UserRole } from '../types/auth';
import { UserOutlined, LogoutOutlined, SunOutlined, MoonOutlined, GlobalOutlined, DownOutlined, MenuOutlined } from '@ant-design/icons';
import type { MenuProps } from 'antd';
import { useTranslation } from 'react-i18next';
import { config } from '../utils/config';

const { Header, Content, Footer } = Layout;
const { Text } = Typography;

interface AppLayoutProps {
  darkTheme: boolean;
  setDarkTheme: (dark: boolean) => void;
}

const AppLayout: React.FC<AppLayoutProps> = ({ darkTheme, setDarkTheme }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { isAuthenticated, user, logout } = useAuth();
  const { t, i18n } = useTranslation();
  const [drawerVisible, setDrawerVisible] = useState(false);

  const { useBreakpoint } = Grid;
  const screens = useBreakpoint();
  const isMobile = !screens.md;

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

  const showDrawer = () => {
    setDrawerVisible(true);
  };

  const closeDrawer = () => {
    setDrawerVisible(false);
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

  const canViewDashboard = user?.role === UserRole.ADMIN || user?.role === UserRole.MODERATOR;

  const mainMenuItems: MenuProps['items'] = [
    {
      key: '/',
      label: <Link to="/">Home</Link>,
    },
    ...(canViewDashboard
      ? [
        {
          key: '/dashboard',
          label: <Link to="/dashboard">Dashboard</Link>,
        },
      ]
      : []),
  ];

  const menuInDrawer = (
    <Menu
      theme={darkTheme ? 'dark' : 'light'}
      mode="inline"
      selectedKeys={[location.pathname]}
      items={mainMenuItems}
      onClick={closeDrawer} // Close drawer when a menu item is clicked
    />
  );

  const menuInHeader = (
    <Menu
      theme={darkTheme ? 'dark' : 'light'}
      mode="horizontal"
      selectedKeys={[location.pathname]}
      style={{ flex: 1, borderBottom: 'none', background: 'transparent' }}
      items={mainMenuItems}
    />
  );

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 24px', background: darkTheme ? '#001529' : '#fff' }}>
        <div style={{ display: 'flex', alignItems: 'center', flex: 1, minWidth: 0 }}>
          {isMobile && (
            <Button
              type="text"
              icon={<MenuOutlined style={{ color: darkTheme ? 'white' : 'black' }} />}
              onClick={showDrawer}
              style={{ marginRight: '16px' }}
            />
          )}
          <div className="logo" style={{ color: darkTheme ? 'white' : 'black', fontSize: '24px', marginRight: '24px' }}>
            <Link to="/" style={{ color: 'inherit', textDecoration: 'none' }}><Text>{config.APP_NAME}</Text></Link>
          </div>
          {!isMobile && menuInHeader}
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
                <DownOutlined style={{ color: darkTheme ? 'white' : 'black' }} />
              </Space>
            </a>
          </Dropdown>
          {renderUserControls()}
        </Space>
      </Header>

      <Drawer
        title={config.APP_NAME}
        placement="left"
        onClose={closeDrawer}
        open={drawerVisible}
        styles={{ body: { padding: 0 } }}
      >
        {menuInDrawer}
      </Drawer>

      <Content style={{ verticalAlign: 'middle' }}>
        <Outlet />
      </Content>

      <Footer style={{ textAlign: 'center' }}>
        Web3 DApp ©2025 @itgiup
      </Footer>
    </Layout>
  );
};

export default AppLayout;
