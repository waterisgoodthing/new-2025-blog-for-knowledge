# 2025 Blog

Personal knowledge and blog system built with Next.js and FastAPI.

## Project Lines

- `src/`: Next.js App Router frontend and original static blog workflow.
- `backend/`: FastAPI backend for notes, mistakes, review, auth, AI, music, recommendations, and GitHub sync.

## Local Development

Install frontend dependencies:

```bash
pnpm install
```

Run the frontend:

```bash
pnpm dev
```

Install backend dependencies in a local virtual environment:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the backend:

```bash
uvicorn main:app --reload
```

## Content State

Original author content has been cleared. Static blog indexes, category data, share links, pictures, project entries, snippets, and blogger lists start empty.

Add your own content through the app UI or by editing the matching JSON/static files.

## Configuration

Frontend GitHub App settings use `NEXT_PUBLIC_GITHUB_*` environment variables.

Backend settings live in `backend/.env`; keep secrets out of Git. Use `backend/.env.example` as the template.
