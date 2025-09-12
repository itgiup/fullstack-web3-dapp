// Authentication types
export interface User {
  id: string;
  username: string;
  email: string;
  role: UserRole;
  status: UserStatus;
  firstName?: string;
  lastName?: string;
  avatar?: string;
  walletAddresses?: WalletAddress[];
  primaryWallet?: string;
}

export interface WalletAddress {
  address: string;
  network: string;
  isVerified: boolean;
  createdAt: string;
}

export const UserRole = {
  USER: 'USER',
  ADMIN: 'ADMIN',
  MODERATOR: 'MODERATOR',
} as const;
export type UserRole = (typeof UserRole)[keyof typeof UserRole];

export const UserStatus = {
  ACTIVE: 'ACTIVE',
  INACTIVE: 'INACTIVE',
  BANNED: 'BANNED',
  PENDING: 'PENDING',
} as const;
export type UserStatus = (typeof UserStatus)[keyof typeof UserStatus];

export const LoginMethod = {
  EMAIL: 'EMAIL',
  USERNAME: 'USERNAME',
  WALLET: 'WALLET',
} as const;
export type LoginMethod = (typeof LoginMethod)[keyof typeof LoginMethod];

export interface TokenPair {
  accessToken: string;
  refreshToken: string;
  tokenType: string;
  expiresIn: number;
}

export interface LoginRequest {
  identifier: string;
  password?: string;
  signature?: string;
  message?: string;
  method: LoginMethod;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
  firstName?: string;
  lastName?: string;
  walletAddress?: string;
}

export interface AuthResponse {
  success: boolean;
  message: string;
  tokens?: TokenPair;
  user?: User;
}

export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  tokens: TokenPair | null;
  loading: boolean;
  error: string | null;
}

export interface AuthContextType extends AuthState {
  login: (request: LoginRequest) => Promise<AuthResponse>;
  register: (request: RegisterRequest) => Promise<AuthResponse>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<boolean>;
  connectWallet: (address: string, signature: string, message: string) => Promise<AuthResponse>;
}

// Form types
export interface LoginFormValues {
  identifier: string;
  password: string;
  method: 'email' | 'username';
  rememberMe?: boolean;
}

export interface RegisterFormValues {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
  firstName?: string;
  lastName?: string;
  agreeToTerms: boolean;
}

export interface WalletLoginFormValues {
  walletAddress: string;
  signature: string;
  message: string;
}
