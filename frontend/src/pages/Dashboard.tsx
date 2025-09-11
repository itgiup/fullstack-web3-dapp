import { Card, Row, Col, Typography, Space, Button, Statistic } from 'antd';
import { WalletOutlined, CrownOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { useAuth } from '../contexts/AuthContext';

const { Title, Text } = Typography;

export default function Dashboard() {
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
  };

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: '24px' }}>
        <Title level={2}>Dashboard</Title>
        <Text type="secondary">Welcome back, {user?.firstName || user?.username}!</Text>
      </div>

      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Account Status"
              value={user?.status}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: user?.status === 'ACTIVE' ? '#52c41a' : '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Role"
              value={user?.role}
              prefix={<CrownOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Wallet Addresses"
              value={user?.walletAddresses?.length || 0}
              prefix={<WalletOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Button type="primary" danger onClick={handleLogout} style={{ width: '100%' }}>
              Logout
            </Button>
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card title="Profile Information" bordered={false}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text strong>Username: </Text>
                <Text>{user?.username}</Text>
              </div>
              <div>
                <Text strong>Email: </Text>
                <Text>{user?.email}</Text>
              </div>
              <div>
                <Text strong>Full Name: </Text>
                <Text>{user?.firstName && user?.lastName ? `${user.firstName} ${user.lastName}` : 'Not provided'}</Text>
              </div>
              <div>
                <Text strong>Account Status: </Text>
                <Text>{user?.status}</Text>
              </div>
              <div>
                <Text strong>Role: </Text>
                <Text>{user?.role}</Text>
              </div>
            </Space>
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          <Card title="Wallet Information" bordered={false}>
            {user?.walletAddresses && user.walletAddresses.length > 0 ? (
              <Space direction="vertical" style={{ width: '100%' }}>
                {user.walletAddresses.map((wallet, index) => (
                  <div key={index} style={{ padding: '8px', border: '1px solid #f0f0f0', borderRadius: '4px' }}>
                    <div>
                      <Text strong>Address: </Text>
                      <Text code>{wallet.address}</Text>
                    </div>
                    <div>
                      <Text strong>Network: </Text>
                      <Text>{wallet.network}</Text>
                    </div>
                    <div>
                      <Text strong>Verified: </Text>
                      <Text style={{ color: wallet.isVerified ? '#52c41a' : '#faad14' }}>
                        {wallet.isVerified ? 'Yes' : 'No'}
                      </Text>
                    </div>
                    {user.primaryWallet === wallet.address && (
                      <div>
                        <Text type="success" strong>Primary Wallet</Text>
                      </div>
                    )}
                  </div>
                ))}
              </Space>
            ) : (
              <Text type="secondary">No wallet addresses connected</Text>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
}
