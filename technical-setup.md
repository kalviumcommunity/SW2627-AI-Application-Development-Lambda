# Lambda - Technical Setup Guide

This guide provides comprehensive instructions for setting up and deploying the entire Lambda ecosystem for IT incident management with AI assistance.

## Table of Contents

- [Project Overview](#project-overview)
- [Common Prerequisites](#common-prerequisites)
- [Setup Order](#setup-order)
- [1. Supabase Database](#1-supabase-database)
- [2. Lambda Wiki](#2-lambda-wiki)
- [3. Lambda Agent](#3-lambda-agent)
- [4. LambdaITSM Dashboard](#4-lambdaitsm-dashboard)
- [5. Ingestion Service](#5-ingestion-service)
- [Environment Variables Reference](#environment-variables-reference)
- [Common Troubleshooting](#common-troubleshooting)
- [Deployed Services](#deployed-services)

---

## Project Overview

Lambda is an AI-powered Client Support Knowledge Assistant consisting of:

- **Supabase Database** - Data storage with vector similarity search
- **Lambda Wiki** - Flask API serving client context, SLAs, and runbooks
- **Lambda Agent** - FastAPI-based AI agent with LangChain and Google GenAI
- **LambdaITSM Dashboard** - React frontend for incident management
- **Ingestion Service** - Document ingestion and embedding pipeline (development)

**Deployed URLs:**
- Lambda Wiki: https://lambda-wiki.onrender.com
- LambdaITSM Dashboard: https://lambda-itsm.netlify.app

---

## Common Prerequisites

### Required Tools
- **Git** - For cloning the repository
- **Python 3.12** - For backend services (Lambda Agent, Wiki, Ingestion)
- **Node.js 18+** - For frontend dashboard
- **Supabase Account** - Free tier available at [supabase.com](https://supabase.com)
- **Google Cloud Project** - For Gemini API access

### Account Services
- **Supabase project** with pgvector extension enabled
- **Google GenAI API key** (for Lambda Agent)
- **Google Drive API access** (for Ingestion Service, optional)

---

## Setup Order

Follow this order for a complete setup:

1. **Supabase Database** - Set up database schema and sample data
2. **Lambda Wiki** - Deploy Wiki API (or run locally)
3. **Lambda Agent** - Deploy AI agent (or run locally)
4. **LambdaITSM Dashboard** - Deploy frontend (or run locally)
5. **Ingestion Service** - Set up document ingestion (optional, for development)

---

## 1. Supabase Database

Supabase serves as the primary database backend with vector similarity search via pgvector.

### Quick Setup (Dashboard)

1. **Create Project** at [supabase.com](https://supabase.com)
2. **Get Credentials** from Project Settings → API:
   - Copy Project URL
   - Copy service_role key
3. **Run Migrations** via SQL Editor (execute files in order from `sources/supabase/migrations/`):
   - `001_clients.sql` through `018_replace_match_kb_chunks.sql`
4. **Create Storage Bucket** named `runbooks` (private)
5. **Upload Runbooks** from `sources/supabase/runbooks/` to the bucket

### CLI Setup (Recommended for Development)

```bash
# Install CLI
brew install supabase/tap/supabase  # macOS
# or: curl -fsSL https://supabase.com/install/v2/cli | bash  # Linux

# Login and link
supabase login
cd sources/supabase
supabase link --project-ref YOUR_PROJECT_REF

# Apply migrations
supabase db push

# Upload runbooks
python upload_runbook.py
```

### Database Schema

**Core Tables:** clients, services, critical_systems, slas, sla_priorities, contacts, special_instructions, runbook_references

**Knowledge Base:** kb_documents, kb_embeddings (with vector embeddings)

**Extensions:** uuid-ossp, vector (pgvector)

**Storage:** runbooks bucket (45 sample runbook JSON files)

### Verification

```sql
-- Check tables
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';

-- Check extensions
SELECT extname FROM pg_extension;

-- Check client data
SELECT COUNT(*) FROM clients;
```

---

## 2. Lambda Wiki

Flask-based web service providing client context, SLAs, and runbooks via REST API.

### Setup

```bash
cd sources/wiki

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with SUPABASE_URL and SUPABASE_SERVICE_KEY

# Run locally
python app.py
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SUPABASE_URL` | Supabase project URL | Yes |
| `SUPABASE_SERVICE_KEY` | Supabase service role key | Yes |
| `WIKI_PORT` | Server port (default: 5001) | No |

### API Endpoints

- `GET /health` - Health check
- `GET /api/context/client/<client_id>` - Unified client context
- `GET /api/slas/client/<client_id>?priority=P1` - SLAs with priority filter
- `GET /api/runbooks/client/<client_id>` - Client runbooks
- `GET /api/services/client/<client_id>` - Client services
- `GET /api/contacts/client/<client_id>` - Client contacts

### Deployment (Render)

The project includes `render.yml` for deployment to Render:

1. Push code to GitHub
2. Create web service on Render
3. Set environment variables: `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`
4. Deploy

---

## 3. Lambda Agent

FastAPI-based AI agent using LangChain and Google GenAI for intelligent incident support.

### Setup

```bash
cd lambda

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with required variables

# Run locally
python server.py
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `WIKI_API_URL` | Lambda Wiki API URL | Yes |
| `LAMBDA_AGENT_PORT` | Server port (default: 8000) | No |
| `SUPABASE_SERVICE_KEY` | Supabase service role key | Yes |
| `SUPABASE_URL` | Supabase project URL | Yes |
| `GROQ_API_KEY` | Groq API key | Yes |
| `GOOGLE_API_KEY_1` | Google GenAI API key (primary) | Yes |
| `GOOGLE_API_KEY_2` | Google GenAI API key (secondary) | No |

### API Endpoints

- `GET /health` - Health check
- `POST /query` - Process incident queries

**Query Request:**
```json
{
  "query": "How do I handle a P1 database outage?",
  "client_id": "client-uuid",
  "metadata": {
    "priority": "P1",
    "incident_type": "database_outage"
  }
}
```

### Deployment (Render)

The project includes `render.yaml` for deployment:

1. Push code to GitHub
2. Create web service on Render
3. Set environment variables
4. Deploy

---

## 4. LambdaITSM Dashboard

React-based frontend for incident management with integrated AI chat assistant.

### Setup

```bash
cd itsm

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with backend URLs

# Run locally
npm run dev
```

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `VITE_LAMBDA_AGENT_API_URL` | Lambda Agent API URL | Yes | http://localhost:8000 |
| `VITE_CONTEXT_API_URL` | Lambda Wiki API URL | Yes | http://localhost:5001 |

**Production Example:**
```env
VITE_LAMBDA_AGENT_API_URL=https://your-lambda-agent.onrender.com
VITE_CONTEXT_API_URL=https://lambda-wiki.onrender.com
```

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run linter

### Deployment (Netlify)

The project includes `netlify.toml` for deployment:

1. Push code to GitHub
2. Connect repository to Netlify
3. Set environment variables
4. Deploy

---

## 5. Ingestion Service

Python script for ingesting documents from Google Drive and Wiki API, generating embeddings for vector search.

**Status:** Not deployed (development phase)

### Setup

```bash
cd ingestion

# Install dependencies
pip install python-dotenv supabase sentence-transformers pypdf google-api-python-client google-auth-oauthlib google-auth-httplib2

# Configure Google Drive OAuth
# 1. Create OAuth credentials in Google Cloud Console
# 2. Download credentials.json and place in ingestion/ directory

# Configure environment
# Add to .env: SUPABASE_URL, SUPABASE_SERVICE_KEY, DRIVE_COD_FOLDER_ID, WIKI_URL

# Run manually
python main.py
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SUPABASE_URL` | Supabase project URL | Yes |
| `SUPABASE_SERVICE_KEY` | Supabase service role key | Yes |
| `DRIVE_COD_FOLDER_ID` | Google Drive folder ID for CoD PDFs | Yes |
| `WIKI_URL` | Lambda Wiki API URL | Yes |

### Scheduling

Run periodically (e.g., weekly) via cron or GitHub Actions:

```bash
# Cron example
0 2 * * 0 cd /path/to/project && python ingestion/main.py >> /var/log/ingestion.log 2>&1
```

---

## Environment Variables Reference

### Backend Services (Python)

```env
# Supabase (shared by all backend services)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key

# Lambda Agent
WIKI_API_URL=https://lambda-wiki.onrender.com
LAMBDA_AGENT_PORT=8000
GROQ_API_KEY=your_groq_key
GOOGLE_API_KEY_1=your_google_key_1
GOOGLE_API_KEY_2=your_google_key_2

# Lambda Wiki
WIKI_PORT=5001

# Ingestion Service
DRIVE_COD_FOLDER_ID=your-drive-folder-id
WIKI_URL=https://lambda-wiki.onrender.com
```

### Frontend (React/Vite)

```env
VITE_LAMBDA_AGENT_API_URL=http://localhost:8000
VITE_CONTEXT_API_URL=http://localhost:5001
```

---

## Common Troubleshooting

### Python Services

**Import errors:**
```bash
# Ensure using Python 3.12
python --version

# Reinstall dependencies
pip install -r requirements.txt
```

**Supabase connection errors:**
- Verify `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` are correct
- Test connection via Supabase dashboard
- Ensure service role key (not anon key) is used

**Port already in use:**
```bash
# Find process using the port
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process or change the port in .env
```

### Frontend

**Development server won't start:**
```bash
# Check Node.js version
node --version  # Should be 18+

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

**Chat assistant not responding:**
- Verify Lambda Agent is running: `curl http://localhost:8000/health`
- Check `VITE_LAMBDA_AGENT_API_URL` in `.env`
- Check browser console for network errors

**Build fails:**
```bash
# Run linter to identify issues
npm run lint

# Ensure environment variables are set
```

### Database

**Migration fails:**
- Run migrations in numerical order (001 through 018)
- Ensure pgvector extension is enabled (migration 014)
- Check SQL error messages in Supabase dashboard

**Vector search returns no results:**
- Ensure embeddings are populated via ingestion service
- Lower match_threshold in vector search function
- Verify embedding dimension (384 for all-MiniLM-L6-v2)

### Ingestion Service

**Google OAuth fails:**
- Ensure `credentials.json` is in ingestion/ directory
- Verify OAuth consent screen is configured
- Run script once to generate `token.json`

**PDF extraction fails:**
- Ensure PDFs are not password-protected
- Verify PDFs are readable and not corrupted

---

## Deployed Services

| Service | URL | Status |
|---------|-----|--------|
| Lambda Wiki | https://lambda-wiki.onrender.com | Deployed |
| LambdaITSM Dashboard | https://lambda-itsm.netlify.app | Deployed |
| Lambda Agent | - | Not deployed (run locally) |
| Ingestion Service | - | Not deployed (development) |

---

## Additional Resources

- [Main README](../README.md) - Project overview
- [Supabase Documentation](https://supabase.com/docs)
- [LangChain Documentation](https://python.langchain.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
