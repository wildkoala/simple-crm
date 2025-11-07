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

### Installation

**1. Clone and install frontend dependencies:**
```sh
git clone https://github.com/YOUR-USERNAME/simple-crm.git
cd simple-crm
npm install

# Set up environment variables
cp .env.local.example .env.local
# Edit .env.local if needed (default: http://localhost:8000)
```

**2. Set up the backend:**
```sh
cd backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and change SECRET_KEY for production
```

**3. Run the application:**
```sh
# In the backend directory (with venv activated):
python run.py

# In a new terminal, from the project root:
npm run dev
```

The frontend will be at **http://localhost:5173** and the backend API at **http://localhost:8000**.

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
