# Turborepo Monorepo Setup Guide

## Overview

EduMind is now configured as a Turborepo monorepo, allowing efficient development and building of multiple applications and packages with intelligent caching and task orchestration.

## Monorepo Structure

```
EduMind/
├── apps/                      # Applications
│   └── web/                  # Frontend React app (@edumind/web)
├── packages/                  # Shared packages
│   ├── tsconfig/             # Shared TypeScript configs (@edumind/tsconfig)
│   └── utils/                # Shared utilities (@edumind/utils)
├── backend/services/         # Backend microservices
│   ├── user-service/         # @edumind/user-service
│   ├── course-service/       # @edumind/course-service
│   ├── assessment-service/   # @edumind/assessment-service
│   ├── service-xai-prediction/   # @edumind/xai-prediction-service
│   ├── service-learning-style/   # @edumind/learning-style-service
│   └── service-engagement-tracker/   # @edumind/engagement-tracker-service
├── package.json              # Root package.json with workspaces
├── pnpm-workspace.yaml       # pnpm workspace configuration
├── turbo.json                # Turborepo pipeline configuration
└── .npmrc                    # npm/pnpm configuration
```

## Key Concepts

### Workspaces

All packages are defined in `pnpm-workspace.yaml`:
- `apps/*` - Frontend and other applications
- `packages/*` - Shared libraries and utilities
- `backend/services/*` - Backend microservices

### Task Pipeline

The `turbo.json` file defines how tasks are orchestrated:

- **build**: Builds packages and apps (with dependency order)
- **dev**: Runs development servers (persistent tasks)
- **test**: Runs tests with caching
- **lint**: Lints code with caching
- **type-check**: TypeScript type checking

### Caching

Turborepo caches task outputs for:
- Faster subsequent builds
- Skipping unchanged packages
- Remote caching support (optional)

## Installation

```bash
# Install pnpm globally
npm install -g pnpm@8.10.0

# Install all dependencies
pnpm install
```

This will install dependencies for:
- Root workspace
- Frontend app (apps/web)
- All packages (packages/*)
- All backend services (backend/services/*)

## Development Commands

### Run Everything

```bash
# Start all development servers
pnpm dev
```

This runs:
- Frontend at http://localhost:5173
- All backend services (8001-8006)

### Run Specific App/Package

```bash
# Frontend only
pnpm --filter @edumind/web dev

# Specific service
pnpm --filter @edumind/user-service dev

# Multiple services
pnpm --filter @edumind/user-service --filter @edumind/course-service dev
```

### Build Commands

```bash
# Build everything
pnpm build

# Build with Turborepo (uses cache)
turbo run build

# Build specific app
pnpm --filter @edumind/web build

# Build with dependencies
turbo run build --filter=@edumind/web...
```

### Testing

```bash
# Run all tests
pnpm test

# Test specific package
pnpm --filter @edumind/web test

# Test with coverage
pnpm test:cov
```

### Linting

```bash
# Lint everything
pnpm lint

# Lint specific package
pnpm --filter @edumind/web lint

# Type checking
pnpm type-check
```

## Turborepo Features

### Task Dependencies

Tasks can depend on other tasks:

```json
{
  "tasks": {
    "build": {
      "dependsOn": ["^build"]  // Build dependencies first
    },
    "test": {
      "dependsOn": ["build"]   // Build before testing
    }
  }
}
```

### Caching

Turborepo caches outputs based on:
- Task inputs (source files)
- Task configuration
- Environment variables
- Dependencies

```bash
# Force skip cache
turbo run build --force

# View cache hits
turbo run build --summarize
```

### Filtering

Run tasks for specific packages:

```bash
# Single package
turbo run build --filter=@edumind/web

# Package and dependencies
turbo run build --filter=@edumind/web...

# Package and dependents
turbo run build --filter=...@edumind/utils
```

### Parallel Execution

Turborepo runs tasks in parallel when possible:

```bash
# Run with limited concurrency
turbo run test --concurrency=2

# Run serially
turbo run build --concurrency=1
```

## Package Scripts

### Root Level (package.json)

```bash
pnpm dev          # Start all dev servers
pnpm build        # Build all packages
pnpm test         # Run all tests
pnpm lint         # Lint all code
pnpm type-check   # Type check all TypeScript
pnpm clean        # Clean all build artifacts
```

### App/Package Level

Each app/package has its own scripts:

```bash
# In apps/web
pnpm dev          # Start Vite dev server
pnpm build        # Build for production
pnpm lint         # Lint React code
pnpm preview      # Preview production build

# In backend services
pnpm dev          # Start FastAPI with hot reload
pnpm start        # Start production server
pnpm test         # Run pytest
pnpm lint         # Run pylint
```

## Adding New Packages

### 1. Create Package Directory

```bash
mkdir -p packages/my-package/src
```

### 2. Add package.json

```json
{
  "name": "@edumind/my-package",
  "version": "0.0.0",
  "private": true,
  "main": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "scripts": {
    "build": "tsup src/index.ts --format cjs,esm --dts",
    "dev": "tsup src/index.ts --format cjs,esm --dts --watch",
    "lint": "eslint src/",
    "type-check": "tsc --noEmit"
  },
  "devDependencies": {
    "@edumind/tsconfig": "workspace:*",
    "tsup": "^8.0.1",
    "typescript": "^5.3.3"
  }
}
```

### 3. Install Dependencies

```bash
pnpm install
```

### 4. Use in Other Packages

```json
{
  "dependencies": {
    "@edumind/my-package": "workspace:*"
  }
}
```

## Environment Variables

### Global Environment

Create `.env` at the root:

```env
NODE_ENV=development
DATABASE_URL=postgresql://localhost:5432/edumind
```

### App-Specific Environment

Create `.env` in each app:

```
apps/web/.env
backend/services/user-service/.env
```

### Turborepo Environment

List required env vars in `turbo.json`:

```json
{
  "tasks": {
    "build": {
      "env": ["NODE_ENV", "DATABASE_URL"]
    }
  }
}
```

## Docker Integration

### Build All Services

```bash
cd backend
docker-compose up -d
```

### Build Specific Service

```bash
docker-compose up -d user-service
```

### Rebuild After Changes

```bash
docker-compose up -d --build
```

## CI/CD Integration

### GitHub Actions

Update workflows to use Turborepo:

```yaml
- name: Install dependencies
  run: pnpm install

- name: Build
  run: turbo run build

- name: Test
  run: turbo run test

- name: Lint
  run: turbo run lint
```

### Cache Configuration

Enable remote caching for CI:

```bash
# Set up Vercel Remote Cache (optional)
turbo login
turbo link
```

## Troubleshooting

### Dependencies Not Resolving

```bash
# Clean and reinstall
rm -rf node_modules
pnpm store prune
pnpm install
```

### Turbo Cache Issues

```bash
# Clear Turbo cache
turbo run clean
rm -rf .turbo
```

### Workspace Issues

```bash
# Verify workspace setup
pnpm list --depth=0

# Check for dependency issues
pnpm why <package-name>
```

### Build Failures

```bash
# Build with verbose output
turbo run build --verbose

# Build without cache
turbo run build --force
```

## Best Practices

### 1. Naming Convention

Use `@edumind/` prefix for all packages:
- `@edumind/web`
- `@edumind/utils`
- `@edumind/user-service`

### 2. Internal Dependencies

Use `workspace:*` for internal dependencies:

```json
{
  "dependencies": {
    "@edumind/utils": "workspace:*"
  }
}
```

### 3. Task Organization

- Use `dev` for development servers (persistent)
- Use `build` for production builds (cached)
- Use `test` for test suites (cached)
- Use `lint` for linting (cached)

### 4. Git Workflow

```bash
# 1. Create feature branch
git checkout -b feature/my-feature

# 2. Make changes and test
pnpm test

# 3. Lint code
pnpm lint

# 4. Build everything
pnpm build

# 5. Commit and push
git add .
git commit -m "feat: add my feature"
git push origin feature/my-feature
```

### 5. Performance Tips

- Use `--filter` to work on specific packages
- Leverage Turborepo's caching
- Run expensive tasks in parallel
- Use `--no-cache` only when necessary

## Resources

- [Turborepo Documentation](https://turbo.build/repo/docs)
- [pnpm Workspaces](https://pnpm.io/workspaces)
- [Project README](./README.md)
- [TODO List](./todo/PROJECT_TODO.md)

## Support

For monorepo-specific questions:
1. Check this guide
2. Review Turborepo documentation
3. Create an issue with the `monorepo` label
