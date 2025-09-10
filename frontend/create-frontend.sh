#!/bin/bash
# Tạo frontend bằng Vite + TypeScript
npm create vite@latest . -- --template react-ts

# Cài thư viện
npm install antd @ant-design/pro-components @apollo/client graphql react-router-dom @wagmi/core viem

# Cài dev dependencies
npm install -D @graphql-codegen/cli @graphql-codegen/typescript @graphql-codegen/typescript-react-apollo

echo "✅ Frontend created! Run 'npm run dev' to start."
