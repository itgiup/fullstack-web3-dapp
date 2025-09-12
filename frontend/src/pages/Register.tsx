import { Link, useNavigate } from 'react-router-dom';
import { Form, Input, Button, Card, Checkbox, Typography, Divider, Row, Col } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons';
import { useAuth } from '../contexts/AuthContext';
import type { RegisterFormValues } from '../types/auth';
import { config } from '../utils/config';

const { Title, Text } = Typography;

export default function Register() {
  const { register, loading } = useAuth();
  const navigate = useNavigate();
  const [form] = Form.useForm();

  const handleRegister = async (values: RegisterFormValues) => {
    const { agreeToTerms, ...registerData } = values;
    const response = await register(registerData);

    if (response.success) {
      if (response.tokens) {
        navigate('/dashboard');
      } else {
        navigate('/login', {
          state: { message: 'Registration successful! Please check your email to verify your account.' }
        });
      }
    }
  };

  const validatePassword = (_: unknown, value: string) => {
    if (!value) return Promise.reject('Please enter your password');
    if (value.length < 8) return Promise.reject('Password must be at least 8 characters');
    if (!/(?=.*[a-z])/.test(value)) return Promise.reject('Password must contain at least one lowercase letter');
    if (!/(?=.*[A-Z])/.test(value)) return Promise.reject('Password must contain at least one uppercase letter');
    if (!/(?=.*\d)/.test(value)) return Promise.reject('Password must contain at least one number');
    if (!/(?=.*[!@#$%^&*(),.?":{}|<>])/.test(value)) return Promise.reject('Password must contain at least one special character');
    return Promise.resolve();
  };

  const validateConfirmPassword = (_: unknown, value: string) => {
    if (!value) return Promise.reject('Please confirm your password');
    if (value !== form.getFieldValue('password')) return Promise.reject('Passwords do not match');
    return Promise.resolve();
  };

  return (
    <Card
      style={{ 
        width: '100%', 
        maxWidth: 500,
        margin: 'auto',
      }}
      variant="borderless"
    >
      <div style={{ textAlign: 'center', marginBottom: 24 }}>
        <Title level={2} style={{ marginBottom: 8 }}>
          Create Account
        </Title>
        <Text type="secondary">
          Join {config.APP_NAME} and start your Web3 journey
        </Text>
      </div>

      <Form
        form={form}
        name="register"
        onFinish={handleRegister}
        layout="vertical"
        size="large"
        scrollToFirstError
      >
        <Row gutter={16}>
          <Col xs={24} sm={12}>
            <Form.Item name="firstName" label="First Name">
              <Input prefix={<UserOutlined />} placeholder="First name" />
            </Form.Item>
          </Col>
          <Col xs={24} sm={12}>
            <Form.Item name="lastName" label="Last Name">
              <Input prefix={<UserOutlined />} placeholder="Last name" />
            </Form.Item>
          </Col>
        </Row>

        <Form.Item
          name="username"
          label="Username"
          rules={[
            { required: true, message: 'Please enter a username' },
            { min: 3, max: 30, message: 'Username must be 3-30 characters' },
            { pattern: /^[a-zA-Z0-9_]+$/, message: 'Username can only contain letters, numbers, and underscores' },
          ]}
        >
          <Input prefix={<UserOutlined />} placeholder="Choose a username" />
        </Form.Item>

        <Form.Item
          name="email"
          label="Email"
          rules={[
            { required: true, message: 'Please enter your email' },
            { type: 'email', message: 'Please enter a valid email' },
          ]}
        >
          <Input prefix={<MailOutlined />} placeholder="your@email.com" />
        </Form.Item>

        <Form.Item
          name="password"
          label="Password"
          rules={[{ validator: validatePassword }]}
          hasFeedback
        >
          <Input.Password prefix={<LockOutlined />} placeholder="Create a strong password" />
        </Form.Item>

        <Form.Item
          name="confirmPassword"
          label="Confirm Password"
          dependencies={['password']}
          rules={[{ validator: validateConfirmPassword }]}
          hasFeedback
        >
          <Input.Password prefix={<LockOutlined />} placeholder="Confirm your password" />
        </Form.Item>

        <Form.Item
          name="agreeToTerms"
          valuePropName="checked"
          rules={[
            { validator: (_, value) => value ? Promise.resolve() : Promise.reject('Please agree to the terms') }
          ]}
        >
          <Checkbox>
            I agree to the <Link to="/terms" target="_blank">Terms of Service</Link> and <Link to="/privacy" target="_blank">Privacy Policy</Link>
          </Checkbox>
        </Form.Item>

        <Button type="primary" htmlType="submit" loading={loading} size="large" style={{ width: '100%' }}>
          Create Account
        </Button>
      </Form>

      <Divider />

      <div style={{ textAlign: 'center' }}>
        <Text type="secondary">
          Already have an account? <Link to="/login"><Text style={{ color: '#1890ff' }}>Sign in</Text></Link>
        </Text>
      </div>
    </Card>
  );
}