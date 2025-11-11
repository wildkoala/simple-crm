# Pretorin CRM

A bare bones CRM for startups in the govtech space. This tool allows for tracking contract opportunities and individual contacts.

## About

This is a simple, straightforward CRM designed specifically for government technology startups. It provides an intuitive interface for managing contacts and tracking government contract opportunities. The application comes with example data to help you get started quickly and understand the system's capabilities.

## Technologies

**Frontend:**
- React + TypeScript
- Vite
- shadcn-ui component library
- Tailwind CSS

**Backend:**
- Python FastAPI
- SQLite database with SQLAlchemy ORM
- JWT authentication

## Features

- Contact management with status tracking (hot/warm/cold)
- Contract opportunity tracking with deadlines
- Communication logging
- JWT authentication
- Pre-populated example data

## Getting Started

### Prerequisites

- Node.js & npm - [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating)
- Python 3.8+ for the backend

### Quick Start

The easiest way to run the application is using the included development script:

**Linux/Mac:**
```sh
git clone https://github.com/YOUR-USERNAME/simple-crm.git
cd simple-crm
./dev.sh
```

**Windows:**
```sh
git clone https://github.com/YOUR-USERNAME/simple-crm.git
cd simple-crm
dev.bat
```

The script will:
- Set up Python virtual environment and install backend dependencies
- Install frontend dependencies
- Create environment files from examples (if not present)
- Start both backend and frontend servers

The frontend will be at **http://localhost:5173** and the backend API at **http://localhost:8000**.

Press `Ctrl+C` to stop all services.

### Manual Setup (Alternative)

If you prefer to run services separately:

**1. Set up and run the backend:**
```sh
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

**2. In a new terminal, set up and run the frontend:**
```sh
npm install
cp .env.local.example .env.local
npm run dev
```

### Default Login

The example database includes a demo user:
- **Email**: demo@pretorin.com
- **Password**: demo123

**Note**: Change this password in production!

### API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Development

**Frontend commands:**
- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run build:dev` - Build in development mode
- `npm run lint` - Run ESLint
- `npm run preview` - Preview production build locally

**Backend:**
The backend runs with auto-reload enabled. Changes to Python files automatically restart the server.

To reset the database:
```sh
cd backend
rm crm.db
python run.py  # Will recreate and seed with example data
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
