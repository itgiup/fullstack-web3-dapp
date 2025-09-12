export const config = {
  // API endpoints
  API_URL: import.meta.env.VITE_API_URL || 'http://localhost:3080',
  GRAPHQL_URL: import.meta.env.VITE_GRAPHQL_URL || 'http://localhost:8000/graphql',
  AUTH_URL: import.meta.env.VITE_AUTH_URL || 'http://localhost:8000/graphql',
  
  // App info
  APP_NAME: 'Web3 DApp',
  APP_VERSION: '1.0.0',
  
  // Web3 config
  SUPPORTED_CHAINS: [1, 5, 137, 80001], // Mainnet, Goerli, Polygon, Mumbai
  DEFAULT_CHAIN_ID: 1,
  
  // Storage keys
  STORAGE_KEYS: {
    ACCESS_TOKEN: 'access_token',
    REFRESH_TOKEN: 'refresh_token',
    USER_DATA: 'user_data',
    WALLET_DATA: 'wallet_data',
  },
  
  // Token expiry buffer (5 minutes in milliseconds)
  TOKEN_REFRESH_BUFFER: 5 * 60 * 1000,
} as const;

export type Config = typeof config;
