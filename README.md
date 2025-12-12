# AURA - Automated Understanding & Role Assessment

A comprehensive AI-powered skill verification system that analyzes candidate GitHub repositories, generates intelligent interview questions, and provides automated evaluation reports.

## 🎯 Overview

AURA analyzes a candidate's GitHub projects to:
- Extract technical stack and project structure
- Generate contextual interview questions
- Evaluate candidate responses across multiple dimensions
- Provide comprehensive assessment reports
- Detect potential fraud signals

## 🏗️ System Architecture

### Phase 0: Preparation
- Define role-specific skill profiles (Frontend, Backend, ML, DevOps)

### Phase 1: Input Collection
- Candidate provides GitHub URL and basic info
- System validates and clones repository

### Phase 2: Project Understanding
- Parse repository structure using Tree-sitter
- Extract AST, functions, classes, and modules
- Identify core components

### Phase 3: Knowledge Storage (RAG)
- Chunk code and documentation
- Generate vector embeddings
- Store in ChromaDB for semantic retrieval

### Phase 4: LLM Reasoning
- Generate project summary
- Create intelligent interview questions (Why/What/How/Where)

### Phase 5: Candidate Interaction
- Candidate answers generated questions
- Optional time tracking

### Phase 6: Automated Evaluation
- Multi-dimensional scoring (Understanding, Reasoning, Communication, Logic)
- Weighted final score (0-100)

### Phase 7: Report Generation
- Comprehensive PDF/JSON reports
- Strengths, weaknesses, and recommendations

### Phase 8: Recruiter Dashboard
- View and compare candidates
- Skill-specific breakdowns

### Phase 9: Fraud Detection
- Flag inconsistent or suspicious answers

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.9+
Node.js 16+ (for frontend)
Git
```

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd A.U.R.A
```

2. **Backend Setup**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
```

3. **Frontend Setup**
```bash
cd frontend
npm install
```

4. **Run the application**

Backend:
```bash
cd backend
python main.py
```

Frontend:
```bash
cd frontend
npm run dev
```

## 📁 Project Structure

```
A.U.R.A/
├── backend/
│   ├── api/                    # FastAPI endpoints
│   ├── core/                   # Core business logic
│   │   ├── phase0_profiles/    # Role skill definitions
│   │   ├── phase1_github/      # GitHub integration
│   │   ├── phase2_parsing/     # Code parsing & AST
│   │   ├── phase3_rag/         # Vector DB & embeddings
│   │   ├── phase4_llm/         # LLM reasoning
│   │   ├── phase5_interaction/ # Candidate Q&A
│   │   ├── phase6_evaluation/  # Scoring system
│   │   ├── phase7_reporting/   # Report generation
│   │   └── phase9_fraud/       # Fraud detection
│   ├── models/                 # Database models
│   ├── utils/                  # Utilities
│   ├── main.py                 # FastAPI app
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── pages/              # Page components
│   │   ├── services/           # API services
│   │   └── App.jsx
│   └── package.json
├── data/
│   ├── repos/                  # Cloned repositories
│   ├── vector_db/              # ChromaDB storage
│   └── reports/                # Generated reports
└── README.md
```

## 🔑 Environment Variables

Create a `.env` file in the backend directory:

```env
# LLM Configuration
OPENAI_API_KEY=your_openai_key
MODEL_NAME=gpt-4

# GitHub
GITHUB_TOKEN=your_github_token

# Database
CHROMA_DB_PATH=../data/vector_db

# Server
HOST=0.0.0.0
PORT=8000
```

## 📊 API Endpoints

### Candidate Flow
- `POST /api/candidate/submit` - Submit GitHub URL
- `GET /api/candidate/{id}/questions` - Get interview questions
- `POST /api/candidate/{id}/answers` - Submit answers
- `GET /api/candidate/{id}/report` - Get evaluation report

### Recruiter Dashboard
- `GET /api/recruiter/candidates` - List all candidates
- `GET /api/recruiter/candidate/{id}` - Get candidate details
- `GET /api/recruiter/compare` - Compare multiple candidates

## 🎨 Tech Stack

### Backend
- **FastAPI** - High-performance API framework
- **Tree-sitter** - Code parsing and AST extraction
- **ChromaDB** - Vector database for RAG
- **LangChain** - LLM orchestration
- **OpenAI GPT-4** - Language model
- **ReportLab** - PDF generation

### Frontend
- **React** - UI framework
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **Axios** - HTTP client

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 📈 Scoring System

### Evaluation Dimensions
- **Concept Understanding (40%)** - Knowledge of what and why
- **Technical Reasoning (30%)** - Logical and technical depth
- **Communication (20%)** - Clarity of explanation
- **Logic Accuracy (10%)** - Correctness of answers

### Final Score: 0-100

## 🔐 Security & Privacy

- GitHub tokens are encrypted
- Repository data is temporary
- GDPR compliant data handling
- Optional data retention policies

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

MIT License - See LICENSE file for details

## 👥 Authors

AURA Development Team

## 📞 Support

For issues and questions, please open a GitHub issue.

---

Built with ❤️ for better technical hiring
