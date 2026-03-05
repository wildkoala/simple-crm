# Simple CRM

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.12+-green.svg)
![Node](https://img.shields.io/badge/node-18+-green.svg)
![React](https://img.shields.io/badge/react-18-61dafb.svg)
![TypeScript](https://img.shields.io/badge/typescript-5-3178c6.svg)
![FastAPI](https://img.shields.io/badge/fastapi-latest-009688.svg)

A lightweight CRM designed for startups in the govtech space. This tool provides essential functionality for tracking government contract opportunities and managing business contacts.

## About

Simple CRM is a straightforward customer relationship management system built specifically for government technology companies. It offers an intuitive interface for managing contacts, tracking government contract opportunities, and logging communications. The application includes example data to help you understand the system quickly.

## Key Features

- **Contact Management**: Track individual, commercial, and government contacts with status indicators (hot/warm/cold)
- **Contract Opportunity Tracking**: Monitor government contract opportunities with deadlines and submission links
- **Follow-up System**: Flag contacts for follow-up with date tracking
- **Communication Logging**: Record all interactions with contacts (email, phone, meetings)
- **User Management**: Multi-user support with admin controls
- **API Integration**: RESTful API with JWT and API key authentication
- **SAM.gov Integration**: Import contract opportunities from SAM.gov via the govbizops scraper

## Technologies

**Frontend:**
- React with TypeScript
- Vite build tool
- shadcn/ui component library
- Tailwind CSS for styling
- React Router for navigation

**Backend:**
- Python FastAPI framework
- PostgreSQL database with SQLAlchemy ORM
- JWT token authentication
- API key authentication for automation
- Pydantic for data validation

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) (recommended)
- Or for local development: Node.js 18+, Python 3.12+, and a PostgreSQL instance

### Deploy with Docker Compose (Recommended)

The easiest way to run the full stack is with Docker Compose. This starts PostgreSQL, the backend API, and the frontend in one command:

```sh
git clone https://github.com/pretorin-ai/simple-crm.git
cd simple-crm
docker compose up --build
```

Once the containers are healthy:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **PostgreSQL**: `localhost:5432` (user: `crm`, password: `crm`, database: `crm`)

Press `Ctrl+C` to stop all services. Data is persisted in a Docker volume (`pgdata`).

#### Configuration

Environment variables can be overridden in a `.env` file at the project root or passed directly:

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | `change-me-in-production` | JWT signing key |
| `ENV` | `development` | Set to `production` to disable seed data and debug features |
| `LOG_LEVEL` | `info` | Logging level (`debug`, `info`, `warning`, `error`) |
| `VITE_API_BASE_URL` | `http://localhost:8000` | Backend URL used by the frontend at build time |

Example production deployment:

```sh
SECRET_KEY=your-secure-secret ENV=production docker compose up --build -d
```

#### Useful Docker Compose Commands

```sh
docker compose up --build -d   # Start in background (rebuild images)
docker compose logs -f         # Follow all service logs
docker compose logs -f backend # Follow backend logs only
docker compose down            # Stop and remove containers
docker compose down -v         # Stop and remove containers + database volume
```

### Local Development Setup (Alternative)

If you prefer to run services directly for development:

**1. Start PostgreSQL** (or use an existing instance):
```sh
docker compose up db -d
```

**2. Set up and run the backend:**
```sh
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install .
cp .env.example .env      # Edit .env if your database connection differs
python run.py
```

**3. In a new terminal, set up and run the frontend:**
```sh
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

The frontend dev server runs at **http://localhost:5173** and the backend API at **http://localhost:8000**.

### Default Login

The example database includes a demo user:
- **Email**: demo@pretorin.com
- **Password**: demo1234

**Important**: Change this password in production environments.

## API Integration

Simple CRM provides a RESTful API with two authentication methods:

### JWT Token Authentication

Full access to all API endpoints using JWT bearer tokens. Tokens are obtained through the `/auth/login` endpoint.

### API Key Authentication

Limited access designed for automation and integrations. API keys can only access:
- `GET /contracts` - View all contracts (read-only)
- `POST /contracts/import/samgov` - Import contracts from SAM.gov
- `GET /auth/me` - Get authenticated user information

To generate an API key:
1. Log in to the application
2. Navigate to the API settings page
3. Click "Generate API Key"
4. Store the key securely (it will only be shown once)

### API Documentation

Once the backend is running, interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Development

### Frontend Commands

Run these from the `frontend/` directory:

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run build:dev` - Build in development mode
- `npm run lint` - Run ESLint
- `npm run preview` - Preview production build locally

### Backend Development

The backend runs with auto-reload enabled during development. Changes to Python files automatically restart the server.

To reset the database with fresh example data:
```sh
docker compose down -v         # Remove the database volume
docker compose up --build      # Recreate and re-seed
```

### Project Structure

```
simple-crm/
├── docker-compose.yml        # Full-stack deployment
├── backend/
│   ├── Dockerfile            # Backend container image
│   ├── app/
│   │   ├── auth.py           # Authentication logic
│   │   ├── models/           # Database models
│   │   ├── routers/          # API route handlers
│   │   ├── services/         # Shared business logic
│   │   └── seed_data.py      # Example data seeder
│   ├── run.py                # Application entry point
│   └── pyproject.toml        # Python dependencies
├── frontend/
│   ├── Dockerfile            # Frontend container image (multi-stage)
│   ├── nginx.conf            # Production nginx config
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── contexts/         # React context providers
│   │   ├── lib/              # Utility functions and API client
│   │   └── pages/            # Page components
│   ├── package.json          # Frontend dependencies
│   └── vite.config.ts        # Vite configuration
└── scripts/
    ├── dev.sh                # Development launcher (Linux/Mac)
    └── dev.bat               # Development launcher (Windows)
```

## Security Notes

- API keys have limited access by design - they cannot modify or delete data beyond importing contracts
- JWT tokens provide full access and should be kept secure
- Change default passwords in production
- Use environment variables for sensitive configuration
- API keys should be rotated regularly

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Related Projects

- [govbizops](https://github.com/pretorin-ai/govbizops) - SAM.gov scraper for automatically importing government contract opportunities
