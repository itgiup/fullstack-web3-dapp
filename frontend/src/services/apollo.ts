import { ApolloClient, InMemoryCache, createHttpLink, from } from '@apollo/client';
import { setContext } from '@apollo/client/link/context';
import { onError } from '@apollo/client/link/error';
import { config } from '../utils/config';

// Create HTTP link
const httpLink = createHttpLink({
  uri: config.GRAPHQL_URL,
});

// Auth link to add JWT token to requests
const authLink = setContext((_, { headers }) => {
  // Get token from localStorage
  const token = localStorage.getItem(config.STORAGE_KEYS.ACCESS_TOKEN);
  
  return {
    headers: {
      ...headers,
      authorization: token ? `Bearer ${token}` : "",
    }
  };
});

// Error link for handling GraphQL and network errors
const errorLink = onError(({ graphQLErrors, networkError }) => {
  if (graphQLErrors) {
    graphQLErrors.forEach(({ message, locations, path, extensions }) => {
      console.error(
        `[GraphQL error]: Message: ${message}, Location: ${locations}, Path: ${path}`
      );
      
      // Handle authentication errors
      if (extensions?.code === 'UNAUTHENTICATED' || message.includes('Not authenticated')) {
        // Clear tokens and redirect to login
        localStorage.removeItem(config.STORAGE_KEYS.ACCESS_TOKEN);
        localStorage.removeItem(config.STORAGE_KEYS.REFRESH_TOKEN);
        localStorage.removeItem(config.STORAGE_KEYS.USER_DATA);
        
        // Only redirect if not already on auth pages
        if (!window.location.pathname.includes('/login') && !window.location.pathname.includes('/register')) {
          window.location.href = '/login';
        }
      }
    });
  }
  
  if (networkError) {
    console.error(`[Network error]: ${networkError}`);
    
    // Handle specific network errors
    if ('statusCode' in networkError && networkError.statusCode === 401) {
      // Token expired or invalid, try to refresh
      handleTokenRefresh();
    }
  }
});

// Handle token refresh
const handleTokenRefresh = async () => {
  const refreshToken = localStorage.getItem(config.STORAGE_KEYS.REFRESH_TOKEN);
  
  if (!refreshToken) {
    // No refresh token, redirect to login
    window.location.href = '/login';
    return;
  }
  
  try {
    // Call refresh token mutation
    const response = await fetch(config.AUTH_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: `
          mutation RefreshToken($input: RefreshTokenInput!) {
            refreshToken(input: $input) {
              success
              message
              tokens {
                accessToken
                refreshToken
                expiresIn
              }
            }
          }
        `,
        variables: {
          input: {
            refreshToken,
          },
        },
      }),
    });
    
    const result = await response.json();
    
    if (result.data?.refreshToken?.success && result.data?.refreshToken?.tokens) {
      const { accessToken, refreshToken: newRefreshToken } = result.data.refreshToken.tokens;
      
      // Update tokens in localStorage
      localStorage.setItem(config.STORAGE_KEYS.ACCESS_TOKEN, accessToken);
      localStorage.setItem(config.STORAGE_KEYS.REFRESH_TOKEN, newRefreshToken);
      
      // Reload the page to retry the failed request
      window.location.reload();
    } else {
      // Refresh failed, redirect to login
      localStorage.clear();
      window.location.href = '/login';
    }
  } catch (error) {
    console.error('Token refresh failed:', error);
    localStorage.clear();
    window.location.href = '/login';
  }
};

// Create Apollo Client instance
export const apolloClient = new ApolloClient({
  link: from([errorLink, authLink, httpLink]),
  cache: new InMemoryCache({
    typePolicies: {
      Query: {
        fields: {
          users: {
            // Enable pagination for users query
            keyArgs: ['status', 'role', 'search'],
            merge(existing = { users: [], totalCount: 0 }, incoming) {
              return {
                ...incoming,
                users: [...(existing.users || []), ...(incoming.users || [])],
              };
            },
          },
        },
      },
    },
  }),
  defaultOptions: {
    watchQuery: {
      errorPolicy: 'all',
    },
    query: {
      errorPolicy: 'all',
    },
    mutate: {
      errorPolicy: 'all',
    },
  },
});

export default apolloClient;
