import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Form, Input, Button, Card, Tabs, Typography, Divider } from 'antd';
import { UserOutlined, LockOutlined, WalletOutlined } from '@ant-design/icons';
import { LoginForm, ProFormText, ProFormCheckbox } from '@ant-design/pro-components';
import { useAuth } from '../contexts/AuthContext';
import type { LoginFormValues, WalletLoginFormValues } from '../types/auth';
import { LoginMethod } from '../types/auth';
import { config } from '../utils/config';

const { Title, Text } = Typography;

export default function Login() {
  const { login, connectWallet, loading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [activeTab, setActiveTab] = useState('email');

  // Get the redirect path from location state or default to dashboard
  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || '/dashboard';

  // Handle email/username login
  const handleLogin = async (values: LoginFormValues) => {
    const response = await login({
      identifier: values.identifier,
      password: values.password,
      method: values.method === 'email' ? LoginMethod.EMAIL : LoginMethod.USERNAME,
    });

    if (response.success) {
      navigate(from, { replace: true });
    }
  };

  // Handle wallet login
  const handleWalletLogin = async (values: WalletLoginFormValues) => {
    const response = await connectWallet(
      values.walletAddress,
      values.signature,
      values.message
    );

    if (response.success) {
      navigate(from, { replace: true });
    }
  };

  // Generate message for wallet signing
  const generateSignMessage = () => {
    const timestamp = new Date().toISOString();
    return `Please sign this message to authenticate with ${config.APP_NAME}.\n\nTimestamp: ${timestamp}`;
  };

  return (
    <Card
      style={{
        width: '100%',
        maxWidth: 400,
      }}
      variant="borderless"
    >
      <div style={{ textAlign: 'center', marginBottom: 24 }}>
        <Title level={2} style={{ marginBottom: 8 }}>
          Welcome Back
        </Title>
        <Text type="secondary">
          Sign in to your {config.APP_NAME} account
        </Text>
      </div>

      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        centered
        size="large"
        style={{ marginBottom: 24 }}
        items={[
          {
            key: 'email',
            label: (
              <span>
                <UserOutlined />
                Email/Username
              </span>
            ),
            children: (
              <LoginForm
                onFinish={handleLogin}
                loading={loading}
                submitter={{
                  render: (_props: any, dom: any[]) => dom.pop(),
                  resetButtonProps: {
                    style: {
                      // Hide the reset button
                      display: 'none',
                    },
                  },
                  // submitter: false, // Remove submitter to avoid duplicate buttons
                }}
                style={{ padding: 0 }}
              >
                <ProFormText
                  name="identifier"
                  fieldProps={{
                    size: 'large',
                    prefix: <UserOutlined />,
                    placeholder: 'Email or Username',
                  }}
                  placeholder="Enter your email or username"
                  rules={[
                    { required: true, message: 'Please enter your email or username' },
                  ]}
                />

                <ProFormText.Password
                  name="password"
                  fieldProps={{
                    size: 'large',
                    prefix: <LockOutlined />,
                    placeholder: 'Password',
                  }}
                  placeholder="Enter your password"
                  rules={[
                    { required: true, message: 'Please enter your password' },
                  ]}
                />

                <Form.Item name="method" initialValue="email" hidden>
                  <Input />
                </Form.Item>

                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: 24,
                  }}
                >
                  <ProFormCheckbox name="rememberMe">
                    Remember me
                  </ProFormCheckbox>
                  <Link to="/forgot-password">
                    <Text type="secondary">Forgot password?</Text>
                  </Link>
                </div>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={loading}
                  size="large"
                  style={{ width: '100%' }}
                >
                  Login
                </Button>
              </LoginForm>
            ),
          },
          {
            key: 'wallet',
            label: (
              <span>
                <WalletOutlined />
                Wallet
              </span>
            ),
            children: (
              <Form onFinish={handleWalletLogin} layout="vertical" size="large">
                <Form.Item
                  name="walletAddress"
                  label="Wallet Address"
                  rules={[
                    { required: true, message: 'Please enter wallet address' },
                    {
                      pattern: /^0x[a-fA-F0-9]{40}$/,
                      message: 'Invalid Ethereum address',
                    },
                  ]}
                >
                  <Input prefix={<WalletOutlined />} placeholder="0x..." />
                </Form.Item>

                <Form.Item
                  name="signature"
                  label="Signature"
                  rules={[{ required: true, message: 'Please enter signature' }]}
                >
                  <Input.TextArea rows={3} placeholder="Signature from wallet..." />
                </Form.Item>

                <Form.Item
                  name="message"
                  label="Message"
                  initialValue={generateSignMessage()}
                  rules={[{ required: true, message: 'Please enter message' }]}
                >
                  <Input.TextArea rows={3} placeholder="Message that was signed..." />
                </Form.Item>

                <Button
                  type="primary"
                  htmlType="submit"
                  loading={loading}
                  size="large"
                  style={{ width: '100%' }}
                >
                  Connect Wallet
                </Button>

                <div style={{ textAlign: 'center', marginTop: 16 }}>
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    Sign the message with your wallet to authenticate
                  </Text>
                </div>
              </Form>
            ),
          },
        ]}
      />

      <Divider />

      <div style={{ textAlign: 'center' }}>
        <Text type="secondary">
          Don't have an account?{' '}
          <Link to="/register">
            <Text style={{ color: '#1890ff' }}>Sign up</Text>
          </Link>
        </Text>
      </div>
    </Card>
  );
}