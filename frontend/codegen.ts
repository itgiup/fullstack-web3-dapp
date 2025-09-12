import { CodegenConfig } from '@graphql-codegen/cli';

const config: CodegenConfig = {
  schema: 'http://localhost:8000/graphql', // Gateway GraphQL endpoint
  documents: ['src/**/*.{ts,tsx}'],
  generates: {
    './src/types/graphql.ts': {
      plugins: [
        'typescript',
        'typescript-operations',
        'typescript-react-apollo',
      ],
      config: {
        withComponent: false,
        withHooks: true,
        withHOC: false,
        withMutationFn: true,
      },
    },
  },
  ignoreNoDocuments: true,
};

export default config;
