import React from 'react';
import { Button } from 'antd';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

const Landing: React.FC = () => {
  const { t } = useTranslation();

  return (
    <div style={{ textAlign: 'center', maxWidth: '800px', padding: '1em', margin: 'auto' }}>
      <h1>{t('landing_title')}</h1>
      <p style={{ fontSize: '18px' }}>
        {t('landing_subtitle')}
      </p>
      <Button type="primary" size="large" style={{ marginTop: '20px' }}>
        <Link to="/register">{t('get_started')}</Link>
      </Button>
    </div>
  );
};

export default Landing;
