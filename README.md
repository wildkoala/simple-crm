# Pretorin CRM

A modern, AI-first CRM for managing sales contacts and government contract opportunities.

## About

This CRM is designed to simplify government security compliance workflows while providing an intuitive interface for managing contacts and contracts. The application comes with example data to help you get started quickly and understand the system's capabilities.

## Technologies

This project is built with:

- **Vite** - Fast build tool and development server
- **TypeScript** - Type-safe JavaScript
- **React** - UI library
- **shadcn-ui** - Component library
- **Tailwind CSS** - Utility-first CSS framework

## Getting Started

### Prerequisites

- Node.js & npm - [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating)

### Installation

```sh
# Clone the repository
git clone <YOUR_GIT_URL>

# Navigate to the project directory
cd star-sales-flow

# Install dependencies
npm i

# Set up environment variables
cp .env.local.example .env.local
# Edit .env.local with your configuration

# Set up the backend (see BACKEND_SETUP.md for details)
cd backend
cp .env.example .env
# Edit backend/.env with your configuration

# Start the development server
npm run dev
```

### Default Login

The example database includes a demo user:
- **Email**: demo@pretorin.com
- **Password**: demo123

**Note**: Change this password in production!

## Development

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run build:dev` - Build in development mode
- `npm run lint` - Run ESLint
- `npm run preview` - Preview production build locally

## Design System

This application follows the Pretorin brand guidelines. See `DESIGN_GUIDE.md` for details on:

- Color palette (Warm Orange, Gold, Light Turquoise, Gray Brown)
- Typography (Lora for headings, Work Sans for body)
- Design principles (Warm, Clear, Trustworthy)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
