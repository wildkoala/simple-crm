# Simple CRM

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
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
- SQLite database with SQLAlchemy ORM
- JWT token authentication
- API key authentication for automation
- Pydantic for data validation

## Getting Started

### Prerequisites

- Node.js 18+ and npm - [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating)
- Python 3.8+ for the backend

### Quick Start

The easiest way to run the application is using the included development script:

**Linux/Mac:**
```sh
git clone https://github.com/pretorin-ai/simple-crm.git
cd simple-crm
./dev.sh
```

**Windows:**
```sh
git clone https://github.com/pretorin-ai/simple-crm.git
cd simple-crm
dev.bat
```

The script will:
- Set up Python virtual environment and install backend dependencies
- Install frontend dependencies
- Create environment files from examples (if not present)
- Start both backend and frontend servers

The frontend will be available at **http://localhost:5173** and the backend API at **http://localhost:8000**.

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

### SAM.gov Integration

Simple CRM integrates with the [govbizops](https://github.com/pretorin-ai/govbizops) SAM.gov scraper to automatically import government contract opportunities.

**Using govbizops with Simple CRM:**

1. Set up and run govbizops according to its documentation
2. Generate an API key in Simple CRM (see above)
3. Configure govbizops to push opportunities to Simple CRM:

```bash
# Example: Using curl to import SAM.gov opportunities
curl -X POST http://localhost:8000/contracts/import/samgov \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "opportunities": [
      {
        "noticeId": "abc123xyz",
        "title": "IT Services for Federal Agency",
        "solicitationNumber": "RFP-2024-001",
        "description": "Seeking IT support services...",
        "responseDeadLine": "2024-12-31T23:59:59Z",
        "naicsCode": "541512",
        "uiLink": "https://sam.gov/opp/abc123xyz",
        "source": "SAM.gov",
        "pointOfContact": [
          {
            "fullName": "John Smith",
            "email": "john.smith@agency.gov",
            "phone": "555-0100",
            "type": "primary"
          }
        ]
      }
    ],
    "auto_create_contacts": true
  }'
```

The `auto_create_contacts` parameter automatically creates contact records from the point-of-contact information in each opportunity.

### API Documentation

Once the backend is running, interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Development

### Frontend Commands

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run build:dev` - Build in development mode
- `npm run lint` - Run ESLint
- `npm run preview` - Preview production build locally

### Backend Development

The backend runs with auto-reload enabled during development. Changes to Python files automatically restart the server.

To reset the database with fresh example data:
```sh
cd backend
rm crm.db
python run.py  # Will recreate database and seed with example data
```

### Project Structure

```
simple-crm/
├── backend/
│   ├── app/
│   │   ├── auth.py          # Authentication logic
│   │   ├── models/          # Database models
│   │   ├── routers/         # API route handlers
│   │   └── seed_data.py     # Example data seeder
│   ├── run.py               # Application entry point
│   └── requirements.txt     # Python dependencies
├── src/
│   ├── components/          # React components
│   ├── contexts/            # React context providers
│   ├── lib/                 # Utility functions and API client
│   └── pages/               # Page components
└── public/                  # Static assets
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
