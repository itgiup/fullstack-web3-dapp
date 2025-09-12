import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Form, Input, Button, Card, Typography, Divider } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { LoginForm, ProFormText, ProFormCheckbox } from '@ant-design/pro-components';
import { useAuth } from '../contexts/AuthContext';
import type { LoginFormValues } from '../types/auth';
import { LoginMethod } from '../types/auth';
import { config } from '../utils/config';

const { Title, Text } = Typography;

export default function Login() {
  const { login, loading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

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


  return (
    <Card
      style={{
        width: 'auto',
        maxWidth: 400,
        margin: 'auto',
      }}
      variant="borderless"
      styles={{
        body: {
          padding: 0
        }
      }}
    >
      <div style={{ textAlign: 'center', marginBottom: 24 }}>
        <Title level={2} style={{ marginBottom: 8 }}>
          Welcome Back
        </Title>
        <Text type="secondary">
          Sign in to your {config.APP_NAME} account
        </Text>
      </div>

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