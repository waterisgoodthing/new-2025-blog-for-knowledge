# Contributing

Thank you for considering contributing to this project.

## Getting Started

1. Fork and clone the repository.
2. Follow the setup instructions in `README.md` to run both frontend and backend locally.
3. Create a feature branch from `main`.

## Code Style

- Frontend: TypeScript, Next.js App Router, Tailwind CSS.
- Backend: Python, FastAPI, SQLAlchemy (async), Pydantic, Alembic.
- Follow existing patterns in the codebase. When in doubt, look at neighboring files.

## Architecture Boundaries

- `src/lib/api/`: typed API clients. No React.
- `src/app/<route>/components/`: route-specific UI.
- `src/components/`: shared UI used by more than one route.
- `backend/app/models/`: SQLAlchemy models only.
- `backend/app/schemas/`: Pydantic contracts only.
- `backend/app/routers/`: thin HTTP routing.
- `backend/app/services/`: business logic.

## Submitting Changes

1. Ensure `npx tsc --noEmit` passes for frontend changes.
2. Ensure backend imports cleanly (`python -c "from main import app"` in the backend directory).
3. If you changed database models, add or update Alembic migrations under `backend/alembic/versions/`.
4. Open a pull request against `main` with a clear description of what changed and why.

## Reporting Issues

Open a GitHub issue with steps to reproduce, expected behavior, and actual behavior.
