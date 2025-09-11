import React from 'react';
import { Card, Typography, Descriptions, Spin } from 'antd';
import { useAuth } from '../contexts/AuthContext';
import { useTranslation } from 'react-i18next';

const { Title } = Typography;

const Profile: React.FC = () => {
  const { user, loading } = useAuth();
  const { t } = useTranslation();

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 'calc(100vh - 200px)' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!user) {
    return (
      <Card title={t('profile_title')} style={{ maxWidth: 600, margin: 'auto' }}>
        <p>{t('profile_not_logged_in')}</p>
      </Card>
    );
  }

  return (
    <Card title={t('profile_title')} style={{ maxWidth: 600, margin: 'auto' }}>
      <Descriptions bordered column={1}>
        <Descriptions.Item label={t('profile_username')}>{user.username}</Descriptions.Item>
        <Descriptions.Item label={t('profile_email')}>{user.email}</Descriptions.Item>
        <Descriptions.Item label={t('profile_role')}>{user.role}</Descriptions.Item>
        {/* Add more user details here */}
      </Descriptions>
    </Card>
  );
};

export default Profile;
