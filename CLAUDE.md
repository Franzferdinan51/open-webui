# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Open WebUI is a self-hosted AI platform that provides a web interface for interacting with various LLM runners like Ollama and OpenAI-compatible APIs. It's built with a **FastAPI backend** and **SvelteKit frontend** architecture.

## Development Commands

### Frontend Development
- `npm run dev` - Start development server with Pyodide setup (default port 5173)
- `npm run dev:5050` - Start development server on port 5050
- `npm run build` - Build production frontend
- `npm run build:watch` - Build with file watching enabled
- `npm run preview` - Preview production build

### Testing & Quality
- `npm run lint` - Run all linting (frontend, types, backend)
- `npm run lint:frontend` - ESLint for frontend code
- `npm run lint:types` - TypeScript type checking via svelte-check
- `npm run lint:backend` - Pylint for Python backend
- `npm run format` - Format frontend code with Prettier
- `npm run format:backend` - Format backend code with Black
- `npm run test:frontend` - Run frontend tests with Vitest
- `npm run check` - Svelte type checking
- `npm run cy:open` - Open Cypress for E2E testing

### Backend Development
- `python -m open_webui` or `open-webui serve` - Start backend server
- Backend runs on port 8080 by default
- Uses FastAPI with Uvicorn server

### Internationalization
- `npm run i18n:parse` - Parse and update translation files

## Architecture Overview

### Backend Structure (`backend/open_webui/`)
- **`main.py`** - FastAPI application entry point
- **`routers/`** - API route handlers organized by feature (auth, chats, models, etc.)
- **`models/`** - Database models using Peewee ORM
- **`utils/`** - Utility functions for auth, chat processing, embeddings, etc.
- **`retrieval/`** - RAG (Retrieval Augmented Generation) implementation
  - Vector databases (Chroma, Qdrant, Milvus, etc.)
  - Web search providers
  - Document loaders
- **`internal/`** - Database migrations and internal utilities
- **`socket/`** - WebSocket handling for real-time features

### Frontend Structure (`src/`)
- **`routes/`** - SvelteKit page routes
  - `(app)/` - Main application pages (chat, admin, workspace)
  - `auth/` - Authentication pages
- **`lib/components/`** - Reusable Svelte components organized by feature
  - `chat/` - Chat interface components
  - `admin/` - Admin panel components
  - `common/` - Shared UI components
  - `workspace/` - Knowledge, models, prompts, tools management
- **`lib/apis/`** - TypeScript API client functions
- **`lib/stores/`** - Svelte stores for state management
- **`lib/types/`** - TypeScript type definitions
- **`lib/i18n/`** - Internationalization setup and translations

### Key Technologies
- **Backend**: FastAPI, Peewee ORM, SQLAlchemy (migrations), Redis, MongoDB
- **Frontend**: SvelteKit, Vite, TypeScript, TailwindCSS
- **AI/ML**: LangChain, ChromaDB, various embedding models, OpenAI/Anthropic APIs
- **Authentication**: JWT, OAuth (Google, Microsoft, LDAP)
- **File Processing**: Supports PDF, DOCX, images, audio via various libraries

## Important Configuration

### Environment Variables
- `OLLAMA_BASE_URL` - URL for Ollama server (default: http://localhost:11434)
- `OPENAI_API_KEY` - OpenAI API key for GPT models
- `DATABASE_URL` - Database connection string
- Various service-specific API keys for web search, cloud storage, etc.

### Docker Architecture
The application supports multiple deployment modes:
- Standalone container with external Ollama
- Bundled container with Ollama included (`:ollama` tag)
- GPU-enabled containers (`:cuda` tag)

## Development Guidelines

### Code Organization
- Follow existing patterns for component organization
- Keep components focused and reusable
- Use TypeScript throughout the frontend
- Follow Python typing conventions in backend

### API Development
- New API endpoints go in appropriate router files
- Follow FastAPI patterns with proper dependencies
- Include proper error handling and validation
- Document endpoints with OpenAPI schemas

### Frontend Development
- Use Svelte/SvelteKit conventions
- Organize components by feature area
- Keep stores minimal and focused
- Follow existing styling patterns with TailwindCSS

### Testing
- Run linting and type checking before commits
- Backend tests use pytest
- Frontend tests use Vitest
- E2E tests use Cypress

## Common Patterns

### API Calls
Frontend API calls are centralized in `lib/apis/` with consistent error handling and typing.

### State Management
Uses Svelte stores for global state, with local component state for UI-specific data.

### Routing
SvelteKit file-based routing with layout inheritance for shared UI elements.

### Authentication
JWT-based with support for multiple OAuth providers and local authentication.

## Security Considerations

- Never commit secrets or API keys
- Use environment variables for configuration
- Follow CORS and security header best practices
- Validate all user inputs on both frontend and backend
- Use proper authentication and authorization checks

## Database

The application uses Peewee ORM with SQLite as default, supporting PostgreSQL and MySQL for production. Migrations are handled through a custom system in `internal/migrations/`.