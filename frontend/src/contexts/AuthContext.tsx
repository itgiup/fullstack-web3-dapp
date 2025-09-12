import { createContext, useContext, useReducer, useEffect } from 'react';
import type { ReactNode } from 'react';
import { gql } from '@apollo/client';
import { useMutation } from '@apollo/client/react';
import { message as notification } from 'antd';
import type {
  AuthState,
  AuthContextType,
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  User,
  TokenPair
} from '../types/auth';
import { config } from '../utils/config';

// GraphQL mutations
const LOGIN_MUTATION = gql`
  mutation Login($input: LoginInput!) {
    login(input: $input) {
      success
      message
      tokens {
        accessToken
        refreshToken
        tokenType
        expiresIn
      }
      user {
        id
        username
        email
        role
        status
        firstName
        lastName
      }
    }
  }
`;

const REGISTER_MUTATION = gql`
  mutation Register($input: RegisterInput!) {
    register(input: $input) {
      success
      message
      tokens {
        accessToken
        refreshToken
        tokenType
        expiresIn
      }
      user {
        id
        username
        email
        role
        status
        firstName
        lastName
      }
    }
  }
`;

const WALLET_LOGIN_MUTATION = gql`
  mutation WalletLogin($input: WalletLoginInput!) {
    walletLogin(input: $input) {
      success
      message
      tokens {
        accessToken
        refreshToken
        tokenType
        expiresIn
      }
      user {
        id
        username
        email
        role
        status
        firstName
        lastName
      }
    }
  }
`;

const LOGOUT_MUTATION = gql`
  mutation Logout {
    logout {
      success
      message
    }
  }
`;

const REFRESH_TOKEN_MUTATION = gql`
  mutation RefreshToken($input: RefreshTokenInput!) {
    refreshToken(input: $input) {
      success
      message
      tokens {
        accessToken
        refreshToken
        tokenType
        expiresIn
      }
      user {
        id
        username
        email
        role
        status
        firstName
        lastName
      }
    }
  }
`;

// Auth actions
type AuthAction =
  | { type: 'LOGIN_START' }
  | { type: 'LOGIN_SUCCESS'; payload: { user: User; tokens: TokenPair } }
  | { type: 'LOGIN_ERROR'; payload: string }
  | { type: 'LOGOUT' }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'UPDATE_USER'; payload: User };

// Initial state
const initialState: AuthState = {
  isAuthenticated: false,
  user: null,
  tokens: null,
  loading: false,
  error: null,
};

// Reducer
function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'LOGIN_START':
      return {
        ...state,
        loading: true,
        error: null,
      };
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        loading: false,
        isAuthenticated: true,
        user: action.payload.user,
        tokens: action.payload.tokens,
        error: null,
      };
    case 'LOGIN_ERROR':
      return {
        ...state,
        loading: false,
        isAuthenticated: false,
        user: null,
        tokens: null,
        error: action.payload,
      };
    case 'LOGOUT':
      return {
        ...initialState,
      };
    case 'SET_LOADING':
      return {
        ...state,
        loading: action.payload,
      };
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
      };
    case 'UPDATE_USER':
      return {
        ...state,
        user: action.payload,
      };
    default:
      return state;
  }
}

// Create context
const AuthContext = createContext<AuthContextType | null>(null);

// Auth provider component
interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [state, dispatch] = useReducer(authReducer, initialState);
  const [loginMutation] = useMutation(LOGIN_MUTATION);
  const [registerMutation] = useMutation(REGISTER_MUTATION);
  const [walletLoginMutation] = useMutation(WALLET_LOGIN_MUTATION);
  const [logoutMutation] = useMutation(LOGOUT_MUTATION);
  const [refreshTokenMutation] = useMutation(REFRESH_TOKEN_MUTATION);

  // Check for existing auth on app load
  useEffect(() => {
    const checkAuth = async () => {
      dispatch({ type: 'SET_LOADING', payload: true });

      const accessToken = localStorage.getItem(config.STORAGE_KEYS.ACCESS_TOKEN);
      const refreshToken = localStorage.getItem(config.STORAGE_KEYS.REFRESH_TOKEN);
      const userData = localStorage.getItem(config.STORAGE_KEYS.USER_DATA);

      if (accessToken && refreshToken && userData) {
        try {
          const user = JSON.parse(userData);
          const tokens = {
            accessToken,
            refreshToken,
            tokenType: 'bearer',
            expiresIn: 30 * 60 // Default 30 minutes
          };

          // Verify token is still valid by trying to refresh
          const refreshSuccess = await refreshTokens();
          if (refreshSuccess) {
            dispatch({
              type: 'LOGIN_SUCCESS',
              payload: { user, tokens }
            });
          } else {
            // Token refresh failed, clear auth
            clearAuth();
          }
        } catch (error) {
          console.error('Error parsing stored user data:', error);
          clearAuth();
        }
      }

      dispatch({ type: 'SET_LOADING', payload: false });
    };

    checkAuth();
  }, []);

  // Clear authentication data
  const clearAuth = () => {
    localStorage.removeItem(config.STORAGE_KEYS.ACCESS_TOKEN);
    localStorage.removeItem(config.STORAGE_KEYS.REFRESH_TOKEN);
    localStorage.removeItem(config.STORAGE_KEYS.USER_DATA);
    dispatch({ type: 'LOGOUT' });
  };

  // Store authentication data
  const storeAuth = (user: User, tokens: TokenPair) => {
    localStorage.setItem(config.STORAGE_KEYS.ACCESS_TOKEN, tokens.accessToken);
    localStorage.setItem(config.STORAGE_KEYS.REFRESH_TOKEN, tokens.refreshToken);
    localStorage.setItem(config.STORAGE_KEYS.USER_DATA, JSON.stringify(user));

    dispatch({
      type: 'LOGIN_SUCCESS',
      payload: { user, tokens }
    });
  };

  // Login function
  const login = async (request: LoginRequest): Promise<AuthResponse> => {
    dispatch({ type: 'LOGIN_START' });

    try {
      const { data } = await loginMutation({
        variables: {
          input: {
            identifier: request.identifier,
            password: request.password,
            signature: request.signature,
            message: request.message,
            method: request.method,
          },
        },
      });

      const result = (data as { login: AuthResponse }).login;

      if (result.success && result.tokens && result.user) {
        storeAuth(result.user, result.tokens);
        notification.success(result.message);
        return result;
      } else {
        dispatch({ type: 'LOGIN_ERROR', payload: result.message });
        notification.error(result.message);
        return result;
      }
    } catch {
      const errorMessage = 'Login failed. Please try again.';
      dispatch({ type: 'LOGIN_ERROR', payload: errorMessage });
      notification.error(errorMessage);
      return { success: false, message: errorMessage };
    }
  };

  // Register function
  const register = async (request: RegisterRequest): Promise<AuthResponse> => {
    dispatch({ type: 'LOGIN_START' });

    try {
      const { data } = await registerMutation({
        variables: {
          input: {
            username: request.username,
            email: request.email,
            password: request.password,
            confirmPassword: request.confirmPassword,
            firstName: request.firstName,
            lastName: request.lastName,
            walletAddress: request.walletAddress,
          },
        },
      });

      const result = data.register;

      if (result.success && result.user) {
        // Note: Registration might not return tokens if email verification is required
        if (result.tokens) {
          storeAuth(result.user, result.tokens);
        } else {
          dispatch({ type: 'SET_LOADING', payload: false });
        }
        notification.success(result.message);
        return result;
      } else {
        dispatch({ type: 'LOGIN_ERROR', payload: result.message });
        notification.error(result.message);
        return result;
      }
    } catch {
      const errorMessage = 'Registration failed. Please try again.';
      dispatch({ type: 'LOGIN_ERROR', payload: errorMessage });
      notification.error(errorMessage);
      return { success: false, message: errorMessage };
    }
  };

  // Wallet login function
  const connectWallet = async (address: string, signature: string, message: string): Promise<AuthResponse> => {
    dispatch({ type: 'LOGIN_START' });

    try {
      const { data } = await walletLoginMutation({
        variables: {
          input: {
            walletAddress: address,
            signature,
            message,
          },
        },
      });

      const result = data.walletLogin;

      if (result.success && result.tokens && result.user) {
        storeAuth(result.user, result.tokens);
        notification.success(result.message);
        return result;
      } else {
        dispatch({ type: 'LOGIN_ERROR', payload: result.message });
        notification.error(result.message);
        return result;
      }
    } catch {
      const errorMessage = 'Wallet login failed. Please try again.';
      dispatch({ type: 'LOGIN_ERROR', payload: errorMessage });
      notification.error(errorMessage);
      return { success: false, message: errorMessage };
    }
  };

  // Logout function
  const logout = async (): Promise<void> => {
    try {
      await logoutMutation();
    } catch (error) {
      console.error('Logout mutation failed:', error);
    } finally {
      clearAuth();
      notification.success('Logged out successfully');
    }
  };

  // Refresh token function
  const refreshTokens = async (): Promise<boolean> => {
    const refreshToken = localStorage.getItem(config.STORAGE_KEYS.REFRESH_TOKEN);

    if (!refreshToken) {
      return false;
    }

    try {
      const { data } = await refreshTokenMutation({
        variables: {
          input: {
            refreshToken,
          },
        },
      });

      const result = data.refreshToken;

      if (result.success && result.tokens && result.user) {
        storeAuth(result.user, result.tokens);
        return true;
      } else {
        clearAuth();
        return false;
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
      clearAuth();
      return false;
    }
  };

  const value: AuthContextType = {
    ...state,
    login,
    register,
    logout,
    refreshToken: refreshTokens,
    connectWallet,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// Hook to use auth context
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
