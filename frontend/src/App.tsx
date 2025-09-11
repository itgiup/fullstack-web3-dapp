import { useEffect, useState } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import AppLayout from './components/AppLayout';
import Dashboard from './pages/Dashboard';
import ProtectedRoute from './components/ProtectedRoute';
import Register from './pages/Register';
import Login from './pages/Login';
import Landing from './pages/Landing';
import apolloClient from './services/apollo';
import { AuthProvider } from './contexts/AuthContext';
import { ConfigProvider, theme } from 'antd';
import { ApolloProvider } from '@apollo/client';
import Profile from './pages/Profile';

function App() {
  const [darkTheme, setDarkTheme] = useState(() => {
    const savedTheme = localStorage.getItem('darkTheme');
    return savedTheme ? JSON.parse(savedTheme) : false;
  });

  useEffect(() => {
    localStorage.setItem('darkTheme', JSON.stringify(darkTheme));
  }, [darkTheme]);

  return (
    <ConfigProvider
      theme={{
        algorithm: darkTheme ? theme.darkAlgorithm : theme.defaultAlgorithm,
        token: {
          colorPrimary: '#667eea',
          borderRadius: 6,
        },
      }}
    >
      <ApolloProvider client={apolloClient}>
        <AuthProvider>
          <Router>
            <Routes>
              <Route element={<AppLayout darkTheme={darkTheme} setDarkTheme={setDarkTheme} />}>
                <Route path="/" element={<Landing />} />
                <Route 
                  path="/login" 
                  element={
                    <ProtectedRoute requireAuth={false}>
                      <Login />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/register" 
                  element={
                    <ProtectedRoute requireAuth={false}>
                      <Register />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/dashboard" 
                  element={
                    <ProtectedRoute requiredRole={['admin', 'moderator']}>
                      <Dashboard />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/profile" 
                  element={
                    <ProtectedRoute> {/* Profile page requires authentication */}
                      <Profile />
                    </ProtectedRoute>
                  } 
                />
                {/* Add other routes here that should use the AppLayout */}
                
                {/* 404 - Not found */}
                <Route 
                  path="*" 
                  element={
                    <div style={{
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'center',
                      minHeight: '100vh',
                      textAlign: 'center'
                    }}>
                      <h1>404 - Page Not Found</h1>
                      <p>The page you are looking for does not exist.</p>
                      <a href="/dashboard">Go to Dashboard</a>
                    </div>
                  } 
                />
              </Route>
            </Routes>
          </Router>
        </AuthProvider>
      </ApolloProvider>
    </ConfigProvider>
  );
}

export default App;
