# AURA Setup Guide

## Complete Installation Instructions

### Prerequisites

Before starting, ensure you have:

- **Python 3.9+** installed
- **Node.js 16+** and npm
- **Git** installed
- **OpenAI API Key** (for LLM features)
- **GitHub Personal Access Token** (optional, for private repos)

### Step 1: Clone the Repository

```bash
git clone <your-repository-url>
cd A.U.R.A
```

### Step 2: Backend Setup

#### 2.1 Create Virtual Environment

```bash
cd backend
python -m venv venv

# Activate virtual environment
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1

# On Windows CMD:
venv\Scripts\activate.bat

# On Linux/Mac:
source venv/bin/activate
```

#### 2.2 Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 2.3 Configure Environment Variables

```bash
# Copy the example environment file
copy .env.example .env  # Windows
# or
cp .env.example .env    # Linux/Mac
```

Edit `.env` file and add your API keys:

```env
# LLM Configuration
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
MODEL_NAME=gpt-4
EMBEDDING_MODEL=text-embedding-3-small

# GitHub Configuration (optional)
GITHUB_TOKEN=ghp_your-github-personal-access-token

# Keep other settings as default for local development
```

#### 2.4 Initialize Database

The database will be automatically created when you first run the application.

#### 2.5 Run Backend Server

```bash
python main.py
```

The backend API will be available at: `http://localhost:8000`

API Documentation (Swagger): `http://localhost:8000/docs`

### Step 3: Frontend Setup

Open a **new terminal window**:

```bash
cd frontend
```

#### 3.1 Install Dependencies

```bash
npm install
```

#### 3.2 Configure Environment (Optional)

Create `.env` file in frontend directory if you need to change the API URL:

```env
VITE_API_URL=http://localhost:8000/api
```

#### 3.3 Run Frontend Development Server

```bash
npm run dev
```

The frontend will be available at: `http://localhost:3000`

### Step 4: Verify Installation

1. **Open your browser** to `http://localhost:3000`
2. You should see the AURA candidate submission form
3. **Test the API** by visiting `http://localhost:8000/docs`

---

## Quick Start Usage

### For Candidates

1. **Navigate to** `http://localhost:3000`
2. **Fill in the form**:
   - Your name and email
   - GitHub repository URL (must be public or you need GitHub token)
   - Select your role type
3. **Click Submit** - Wait while system analyzes your repository (1-3 minutes)
4. **Answer Questions** - You'll be redirected to interview questions
5. **Submit Answers** - Your responses will be evaluated
6. **View Report** - See your comprehensive evaluation report

### For Recruiters

1. **Navigate to** `http://localhost:3000/dashboard`
2. **View all candidates** and their evaluation scores
3. **Filter by role** or sort by score/date
4. **Click "View Report"** to see detailed assessments
5. **Download PDF reports** for offline review

---

## Common Issues & Solutions

### Issue: OpenAI API Key Invalid

**Solution**: Make sure you have a valid OpenAI API key with GPT-4 access. Get one from https://platform.openai.com/

### Issue: GitHub Repository Can't Be Cloned

**Solutions**:
- Ensure the repository is public, or
- Add your GitHub Personal Access Token to `.env` file
- Check the URL format: `https://github.com/username/repo-name`

### Issue: Database Locked Error

**Solution**: 
- Close any other instances of the application
- Delete `aura.db` file and restart (will reset database)

### Issue: Port Already in Use

**Solutions**:
- **Backend (8000)**: Change `PORT` in `.env` file
- **Frontend (3000)**: The terminal will prompt you to use another port

### Issue: Module Import Errors

**Solution**: Make sure you activated the virtual environment and installed all dependencies:
```bash
pip install -r requirements.txt
```

---

## Production Deployment

### Backend Deployment

1. **Set environment variables** on your hosting platform
2. **Update CORS_ORIGINS** to include your frontend URL
3. **Use PostgreSQL** instead of SQLite (update DATABASE_URL)
4. **Set DEBUG=False**
5. **Use a production WSGI server** like gunicorn:

```bash
pip install gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

### Frontend Deployment

1. **Build for production**:
```bash
npm run build
```

2. **Deploy the `dist` folder** to your hosting service (Vercel, Netlify, etc.)

3. **Update environment variables** to point to your production API

---

## Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

---

## Data Management

### Backup Database

```bash
# SQLite database location
backend/aura.db

# Copy to backup
copy backend\aura.db backup\aura.db
```

### Clear All Data

```bash
# Delete database
del backend\aura.db

# Clear cloned repositories
rmdir /s data\repos

# Clear vector database
rmdir /s data\vector_db

# Clear reports
rmdir /s data\reports
```

---

## System Architecture

```
┌─────────────┐      ┌──────────────┐      ┌───────────────┐
│   Frontend  │─────▶│   FastAPI    │─────▶│   OpenAI      │
│   (React)   │      │   Backend    │      │   GPT-4       │
└─────────────┘      └──────────────┘      └───────────────┘
                            │
                            │
                     ┌──────┴──────┐
                     │             │
              ┌──────▼────┐  ┌─────▼──────┐
              │  SQLite   │  │  ChromaDB  │
              │  Database │  │  (Vectors) │
              └───────────┘  └────────────┘
                     │
                     │
              ┌──────▼────────┐
              │  GitHub API   │
              │  Repository   │
              └───────────────┘
```

---

## API Endpoints Summary

### Candidate Endpoints
- `POST /api/candidate/submit` - Submit GitHub URL
- `GET /api/candidate/{id}/status` - Check processing status
- `GET /api/candidate/{id}/questions` - Get interview questions
- `POST /api/candidate/{id}/answers` - Submit answers
- `GET /api/candidate/{id}/report` - Get evaluation report
- `GET /api/candidate/{id}/report/download` - Download PDF

### Recruiter Endpoints
- `GET /api/recruiter/candidates` - List all candidates
- `GET /api/recruiter/candidate/{id}` - Get candidate details

### Role Endpoints
- `GET /api/roles` - List available roles
- `GET /api/roles/{role_type}/skills` - Get role-specific skills

---

## Support & Troubleshooting

For issues:
1. Check the console logs (backend terminal)
2. Check browser console (F12)
3. Review the API documentation at `/docs`
4. Ensure all environment variables are set correctly

---

## License

MIT License - See LICENSE file for details
