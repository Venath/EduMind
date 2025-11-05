# EduMind Monorepo - Quick Reference

## Installation
```bash
./setup.sh                    # Run automated setup
pnpm install                  # Install dependencies manually
```

## Development
```bash
pnpm dev                      # Start all services
pnpm --filter @edumind/web dev              # Frontend only
pnpm --filter @edumind/user-service dev     # Backend service
```

## Building
```bash
pnpm build                    # Build everything
turbo run build               # Build with cache
pnpm --filter @edumind/web build           # Build frontend
```

## Testing
```bash
pnpm test                     # All tests
pnpm test:cov                 # With coverage
pnpm --filter @edumind/web test            # Frontend tests
```

## Linting
```bash
pnpm lint                     # Lint all
pnpm type-check               # Type check
```

## Docker
```bash
cd backend && docker-compose up -d         # Start services
docker-compose logs -f                     # View logs
docker-compose down                        # Stop services
```

## Service Ports
- Frontend: 5173
- User Service: 8001
- Course Service: 8002
- Assessment Service: 8003
- XAI Prediction: 8004
- Learning Style: 8005
- Engagement Tracker: 8006

## Packages
- `@edumind/web` - React frontend
- `@edumind/utils` - Shared utilities
- `@edumind/tsconfig` - TS configs
- `@edumind/user-service` - User service
- `@edumind/course-service` - Course service
- `@edumind/assessment-service` - Assessment service
- `@edumind/xai-prediction-service` - XAI service
- `@edumind/learning-style-service` - Learning style service
- `@edumind/engagement-tracker-service` - Engagement service

## Turborepo Commands
```bash
turbo run build --filter=@edumind/web      # Build specific
turbo run test --force                     # Skip cache
turbo run build --summarize                # Show cache hits
```

## Cleanup
```bash
pnpm clean                    # Clean artifacts
rm -rf node_modules .turbo && pnpm install # Full reinstall
```

## Documentation
- README.md - Main docs
- MONOREPO.md - Monorepo guide
- TURBOREPO_SETUP.md - Setup details
- SETUP_COMPLETE.md - Installation status
