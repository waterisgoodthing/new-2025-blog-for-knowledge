# 2025 Blog

Personal knowledge and blog system built with Next.js and FastAPI.

## Project Lines

- `src/`: Next.js App Router frontend.
- `backend/`: FastAPI backend for notes, mistakes, review, auth, AI, music, recommendations, and managed content.

## Local Development

### Frontend

Install dependencies:

```bash
npm install
```

Run the dev server:

```bash
npm run dev
```

### Backend

Install backend dependencies in a local virtual environment:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy and edit the environment file:

```bash
cp .env.example .env
```

Run the backend:

```bash
uvicorn main:app --reload
```

## Content Source of Truth

All active content domains are now managed through the backend API and stored in PostgreSQL:

| Domain | Storage | API |
|---|---|---|
| notes, blog, mistakes | PostgreSQL | `/api/notes` |
| about | PostgreSQL | `/api/content/about` |
| share | PostgreSQL | `/api/content/shares` |
| projects | PostgreSQL | `/api/content/projects` |
| pictures | PostgreSQL | `/api/content/pictures` |
| snippets | PostgreSQL | `/api/content/snippets` |
| bloggers | PostgreSQL | `/api/content/bloggers` |
| site settings | PostgreSQL | `/api/content/site-settings` |

Static JSON files under `src/app/*/list.json` and `src/config/` serve only as default seed data for first-time database initialization. Edits are persisted through the backend API.

## Configuration

Backend settings live in `backend/.env`; keep secrets out of Git. Use `backend/.env.example` as the template.

Key settings:

- `DATABASE_URL`: PostgreSQL connection string.
- `JWT_SECRET_KEY`: Session signing key. Must be changed in production.
- `ALLOWED_ORIGINS`: Comma-separated CORS origins.
- `AI_API_KEY` / `AI_BASE_URL` / `AI_MODEL`: Optional AI features.

No GitHub repository write access is required to run or develop this project.
