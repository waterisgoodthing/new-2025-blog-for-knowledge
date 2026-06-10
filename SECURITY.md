# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly.

**Do not open a public GitHub issue for security vulnerabilities.**

Instead, email the maintainer directly or use GitHub's private vulnerability reporting feature if available.

## Scope

This project is a personal knowledge and blog system. The following are considered in scope:

- Authentication or authorization bypass.
- Exposure of private note or mistake content to unauthorized users.
- SQL injection, remote code execution, or path traversal.
- Exposure of secrets or credentials.

## Environment Security

- Never commit `.env` files, private keys, tokens, or database credentials.
- The backend enforces JWT secret validation and CORS checks in production mode.
- `JWT_SECRET_KEY` must be changed from the default before deploying to production.
- `ALLOWED_ORIGINS` must not contain wildcards in production.
