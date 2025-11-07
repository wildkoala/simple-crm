# Backend Setup Guide

This document explains how to set up and run the FastAPI backend for the Pretorin CRM application.

## Overview

The backend is a FastAPI application with:
- **JWT Authentication** - Secure token-based authentication
- **SQLite Database** - Lightweight database with SQLAlchemy ORM
- **RESTful API** - Full CRUD operations for contacts, communications, and contracts
- **Seed Data** - Pre-populated demo data for testing

## Quick Start

### 1. Navigate to Backend Directory
```bash
cd backend
```

### 2. Create Virtual Environment (if not exists)
```bash
python3 -m venv venv
```

### 3. Activate Virtual Environment
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Start the Server
```bash
python run.py
```

The API will be available at: **http://localhost:8000**

## Default Login Credentials

- **Email**: demo@pretorin.com
- **Password**: demo123

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Database

The application uses SQLite with the database file at `./crm.db`.

### Resetting the Database

To reset and reseed the database:
```bash
rm crm.db
python run.py  # Will recreate and seed automatically
```

## Architecture

### Project Structure
```
backend/
├── app/
│   ├── models/         # SQLAlchemy database models
│   ├── routers/        # API route handlers
│   ├── schemas/        # Pydantic schemas for validation
│   ├── auth.py         # Authentication utilities
│   ├── database.py     # Database configuration
│   ├── main.py         # FastAPI app initialization
│   └── seed_data.py    # Database seeding functions
├── .env                # Environment configuration
├── requirements.txt    # Python dependencies
└── run.py             # Server entry point
```

### Authentication Flow

1. User logs in with email/password
2. Backend validates credentials and returns JWT token
3. Frontend stores token in localStorage
4. All subsequent requests include token in `Authorization: Bearer <token>` header
5. Backend validates token on each request

### API Endpoints

#### Authentication
- `POST /auth/login` - Login and get JWT token
- `POST /auth/register` - Register new user (currently disabled in UI)
- `GET /auth/me` - Get current user info

#### Contacts
- `GET /contacts` - List all contacts
- `GET /contacts/{id}` - Get contact by ID
- `POST /contacts` - Create new contact
- `PUT /contacts/{id}` - Update contact
- `DELETE /contacts/{id}` - Delete contact

#### Communications
- `GET /communications` - List communications (optional: `?contact_id=xxx`)
- `POST /communications` - Create communication
- `DELETE /communications/{id}` - Delete communication

#### Contracts
- `GET /contracts` - List all contracts
- `GET /contracts/{id}` - Get contract by ID
- `POST /contracts` - Create new contract
- `PUT /contracts/{id}` - Update contract
- `DELETE /contracts/{id}` - Delete contract

## Security Considerations

### Current Implementation

1. **JWT Authentication** - Tokens expire after 60 minutes (configurable in `.env`)
2. **Password Hashing** - bcrypt with automatic salt generation
3. **CORS Configuration** - Restricted to frontend URL (configurable in `.env`)
4. **SQL Injection Protection** - SQLAlchemy ORM prevents SQL injection

### Production Recommendations

Before deploying to production, consider:

1. **Environment Variables**
   - Change `SECRET_KEY` in `.env` to a strong random value
   - Use environment-specific configs (dev/staging/prod)

2. **Database**
   - Migrate to PostgreSQL or MySQL for production
   - Implement database backups
   - Use connection pooling

3. **HTTPS**
   - Always use HTTPS in production
   - Enforce secure cookies if using session-based auth

4. **Rate Limiting**
   - Add rate limiting to prevent brute force attacks
   - Consider using Redis for distributed rate limiting

5. **Input Validation**
   - Current Pydantic schemas provide basic validation
   - Add additional business logic validation as needed

6. **Logging & Monitoring**
   - Implement structured logging
   - Add application performance monitoring (APM)
   - Set up error tracking (e.g., Sentry)

7. **API Keys/Secrets**
   - Never commit `.env` files to version control
   - Use secrets management (AWS Secrets Manager, HashiCorp Vault, etc.)

8. **User Management**
   - Implement email verification
   - Add password reset functionality
   - Consider multi-factor authentication (MFA)

## Troubleshooting

### Port Already in Use
If port 8000 is already in use, modify `run.py`:
```python
port = int(os.getenv("PORT", "8001"))  # Change to different port
```

### Database Locked Error
SQLite doesn't handle concurrent writes well. For production with multiple workers, use PostgreSQL.

### CORS Errors
Make sure the frontend URL matches `FRONTEND_URL` in `.env` file.

## Development

The server runs with auto-reload enabled. Any changes to Python files will automatically restart the server.

To install new dependencies:
```bash
pip install <package-name>
pip freeze > requirements.txt  # Update requirements file
```
