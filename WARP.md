# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is a fullstack Web3 DApp with a microservices architecture featuring:
- **Backend**: 5 FastAPI microservices (gateway, auth, user, file, payment, notification)
- **Frontend**: React + TypeScript with Vite, Ant Design Pro, Apollo Client, and Web3 integration (wagmi/viem)  
- **Infrastructure**: Docker-based deployment with Nginx reverse proxy
- **Data Layer**: MongoDB with Beanie ODM, Redis for caching, MinIO for S3-compatible storage

## Development Commands

### Full Stack Development
```bash
# Start entire stack
docker-compose up --build

# Start stack in detached mode
docker-compose up -d --build

# Stop all services
docker-compose down

# View logs for specific service
docker-compose logs -f [service-name]

# Access URLs after startup:
# - Frontend: http://localhost:3080
# - GraphQL API: http://localhost:8000/graphql
# - MinIO Console: http://localhost:9001
```

### Frontend Development
```bash
# Navigate to frontend directory first
cd frontend

# Install dependencies
npm install

# Start development server (local)
npm run dev

# Build for production
npm run build

# Run linting
npm run lint

# Preview production build
npm run preview
```

### Backend Service Development
Each service (auth-service, user-service, file-service, payment-service, notification-service) follows the same pattern:

```bash
# Install dependencies (from service directory)
pip install -r requirements.txt

# Run service locally
uvicorn app.main:app --reload --port [PORT]
```

Service ports:
- Gateway: 8000 (GraphQL endpoint at /graphql)
- Auth Service: 8001
- User Service: 8002
- File Service: 8003
- Payment Service: 8004
- Notification Service: 8005

## Architecture

### Microservices Communication
The **gateway** service acts as the API gateway using Strawberry GraphQL, forwarding requests to individual microservices. Services communicate via HTTP using environment variables for service discovery:

- `AUTH_SERVICE_URL=http://auth-service:8001`
- `USER_SERVICE_URL=http://user-service:8002`
- `FILE_SERVICE_URL=http://file-service:8003`
- `PAYMENT_SERVICE_URL=http://payment-service:8004`

### Data Architecture
- **MongoDB**: Each service has its own database (`auth_db`, `user_db`, `file_db`, `payment_db`)
- **Redis**: Used by auth-service for session/caching and notification-service for pub/sub
- **MinIO**: S3-compatible object storage for file uploads (accessible at `:9000`, console at `:9001`)

### Frontend Architecture
- **Vite + React 19**: Modern build tooling with TypeScript
- **Ant Design Pro**: Component library for enterprise applications
- **Apollo Client**: GraphQL client for API communication
- **Web3 Integration**: wagmi/viem for blockchain interactions
- **GraphQL Codegen**: Automatic TypeScript generation from GraphQL schema

### Service Dependencies
```
nginx (reverse proxy)
├── gateway (GraphQL API)
│   ├── auth-service
│   ├── user-service
│   ├── file-service (→ MinIO)
│   └── payment-service (→ Web3 provider)
├── frontend (React SPA)
└── minio (object storage)

External Dependencies:
├── mongo (shared by all services)
├── redis (auth + notifications)
└── Web3 provider (Infura)
```

### Web3 Integration
- Payment service integrates with Web3 providers (configured via `WEB3_PROVIDER` env var)
- Frontend uses wagmi/viem for wallet connections and blockchain interactions
- Requires Infura API key configuration for mainnet access

### Development Workflow
1. Backend services use FastAPI + Beanie (async MongoDB ODM)
2. All services expose `/health` endpoints for monitoring
3. Gateway aggregates services through GraphQL schema
4. Frontend communicates with backend exclusively through GraphQL
5. File uploads handled by file-service → MinIO integration
6. Authentication managed by auth-service with JWT tokens

### Environment Configuration
Key environment variables to configure:
- `MONGODB_URL`: MongoDB connection string for each service
- `REDIS_URL`: Redis connection for caching and pub/sub
- `MINIO_URL`: Object storage endpoint
- `WEB3_PROVIDER`: Ethereum RPC endpoint (e.g., Infura)
- Service URLs for inter-service communication

### Testing Strategy
- Backend: FastAPI's built-in TestClient for API testing
- Frontend: Vite's testing setup with React Testing Library (when configured)
- Integration: Docker Compose for full-stack testing environments
