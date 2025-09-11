import React from 'react';
import { Card, Form, Input, Button, Typography } from 'antd';
import { MailOutlined } from '@ant-design/icons';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

const { Title, Text } = Typography;

const ForgotPassword: React.FC = () => {
  const { t } = useTranslation();

  const onFinish = (values: { email: string }) => {
    console.log('Received values of form: ', values);
    // Here you would typically send a request to your backend
    // to initiate the password reset process.
  };

  return (
    <Card
      style={{
        width: '100%',
        maxWidth: 400,
      }}
      bordered={false}
    >
      <div style={{ textAlign: 'center', marginBottom: 24 }}>
        <Title level={2} style={{ marginBottom: 8 }}>
          {t('forgot_password_title')}
        </Title>
        <Text type="secondary">
          {t('forgot_password_subtitle')}
        </Text>
      </div>

      <Form
        name="forgot_password"
        initialValues={{ remember: true }}
        onFinish={onFinish}
        layout="vertical"
        size="large"
      >
        <Form.Item
          name="email"
          rules={[
            { required: true, message: t('forgot_password_email_required') },
            { type: 'email', message: t('forgot_password_email_invalid') },
          ]}
        >
          <Input prefix={<MailOutlined />} placeholder={t('forgot_password_email_placeholder')} />
        </Form.Item>

        <Form.Item>
          <Button type="primary" htmlType="submit" style={{ width: '100%' }} size="large">
            {t('forgot_password_submit')}
          </Button>
        </Form.Item>

        <div style={{ textAlign: 'center' }}>
          <Link to="/login">
            <Text type="secondary">{t('forgot_password_back_to_login')}</Text>
          </Link>
        </div>
      </Form>
    </Card>
  );
};

export default ForgotPassword;
