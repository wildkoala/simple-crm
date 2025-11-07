# Pretorin CRM Backend

FastAPI backend for the Pretorin CRM application with SQLite database.

## Features

- **Authentication**: JWT-based authentication with Bearer tokens
- **RESTful API**: Full CRUD operations for contacts, communications, and contracts
- **SQLite Database**: Lightweight database with SQLAlchemy ORM
- **Seed Data**: Pre-populated demo data for testing
- **CORS Support**: Configured for frontend integration

## Setup

### 1. Create Virtual Environment

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 4. Run the Application

```bash
python run.py
```

The API will be available at: http://localhost:8000

## Default Credentials

- **Email**: demo@pretorin.com
- **Password**: demo123

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /auth/login` - Login and get JWT token
- `POST /auth/register` - Register new user
- `GET /auth/me` - Get current user info

### Contacts
- `GET /contacts` - List all contacts
- `GET /contacts/{id}` - Get contact by ID
- `POST /contacts` - Create new contact
- `PUT /contacts/{id}` - Update contact
- `DELETE /contacts/{id}` - Delete contact

### Communications
- `GET /communications` - List all communications (optional: ?contact_id=xxx)
- `GET /communications/{id}` - Get communication by ID
- `POST /communications` - Create new communication
- `DELETE /communications/{id}` - Delete communication

### Contracts
- `GET /contracts` - List all contracts
- `GET /contracts/{id}` - Get contract by ID
- `POST /contracts` - Create new contract
- `PUT /contracts/{id}` - Update contract
- `DELETE /contracts/{id}` - Delete contract

## Authentication

All endpoints (except `/auth/login` and `/auth/register`) require authentication.

Include the JWT token in the Authorization header:
```
Authorization: Bearer <your_token_here>
```

## Database

The application uses SQLite with the database file stored at `./crm.db` by default.

To reset the database:
```bash
rm crm.db
python run.py  # Will recreate and seed the database
```

## Development

The application runs in development mode with auto-reload enabled. Any changes to Python files will automatically restart the server.
