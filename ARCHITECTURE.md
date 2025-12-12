# AURA System Architecture Diagrams

## 1. High-Level System Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         AURA SYSTEM FLOW                             │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────┐
│  Candidate  │
│  Submits    │
│  GitHub URL │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 0: Role Selection                                              │
│ • Select Role Type (Frontend/Backend/ML/DevOps/FullStack)           │
│ • Load Role-Specific Skills Matrix                                   │
└──────┬────────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 1: GitHub Repository Collection                                │
│ • Validate GitHub URL                                                 │
│ • Clone Repository Locally                                            │
│ • Extract Repository Metadata (stars, forks, languages)              │
└──────┬────────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 2: Project Understanding (Static Analysis)                     │
│ • Parse Code with Tree-sitter (AST)                                  │
│ • Extract Functions, Classes, Modules                                 │
│ • Identify Entry Points & Core Components                            │
│ • Detect Tech Stack & Frameworks                                      │
└──────┬────────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 3: Knowledge Storage (RAG Preparation)                         │
│ • Chunk Code by Functions/Classes                                    │
│ • Chunk README by Sections                                            │
│ • Generate Vector Embeddings                                          │
│ • Store in ChromaDB Vector Database                                   │
└──────┬────────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 4: LLM Reasoning & Question Generation                         │
│ • Generate Project Summary (GPT-4)                                    │
│ • Retrieve Relevant Code Context (RAG)                               │
│ • Generate 6-10 Interview Questions                                   │
│   - WHY questions (reasoning)                                         │
│   - WHAT questions (understanding)                                    │
│   - HOW questions (implementation)                                    │
│   - WHERE questions (architecture)                                    │
└──────┬────────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 5: Candidate Interaction                                       │
│ • Present Questions to Candidate                                      │
│ • Collect Answers with Time Tracking                                  │
│ • Store Answers in Database                                           │
└──────┬────────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 6: Automated Evaluation                                        │
│ • For Each Answer:                                                    │
│   ├─ Retrieve Relevant Code Context (RAG)                            │
│   ├─ LLM Evaluation (GPT-4)                                          │
│   ├─ Score Across 5 Dimensions:                                      │
│   │   • Concept Understanding (0-10)                                  │
│   │   • Technical Depth (0-10)                                        │
│   │   • Accuracy (0-10)                                               │
│   │   • Communication (0-10)                                          │
│   │   • Relevance (0-10)                                              │
│   ├─ Calculate Weighted Score                                         │
│   └─ Generate Feedback                                                │
│ • Calculate Overall Score (0-100)                                     │
│ • Generate Hire Recommendation                                        │
└──────┬────────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 9: Fraud Detection (Parallel)                                  │
│ • Detect Generic/Copy-Paste Answers                                  │
│ • Flag Short/Incomplete Answers                                       │
│ • Check Code-Answer Consistency                                       │
│ • LLM-Based Fraud Analysis                                            │
└──────┬────────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 7: Report Generation                                           │
│ • Compile Evaluation Results                                          │
│ • Generate Comprehensive PDF Report:                                  │
│   ├─ Candidate Information                                            │
│   ├─ Project Summary                                                  │
│   ├─ Overall Score with Breakdown                                     │
│   ├─ Strengths & Weaknesses                                           │
│   ├─ Hiring Recommendation                                            │
│   ├─ Question-by-Question Analysis                                    │
│   └─ Fraud Detection Results                                          │
│ • Generate JSON Export                                                │
└──────┬────────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 8: Recruiter Dashboard                                         │
│ • View All Candidates                                                 │
│ • Filter by Role Type                                                 │
│ • Sort by Score/Date/Name                                             │
│ • Compare Multiple Candidates                                         │
│ • Download Reports                                                    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Technical Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      FRONTEND (React + Vite)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │   Candidate  │  │  Questions   │  │    Report    │             │
│  │    Submit    │  │     Page     │  │     Page     │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
│  ┌────────────────────────────────────────────────────┐             │
│  │          Recruiter Dashboard                        │             │
│  └────────────────────────────────────────────────────┘             │
│                          │                                           │
│                    HTTP/REST API                                     │
└─────────────────────────┼───────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI + Python)                        │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                      API Endpoints                             │  │
│  │  /candidate/submit  •  /questions  •  /answers  •  /report    │  │
│  │  /recruiter/candidates  •  /roles  •  /status                 │  │
│  └─────────────┬─────────────────────────────────────────────────┘  │
│                │                                                      │
│  ┌─────────────▼─────────────────────────────────────────────────┐  │
│  │                   Business Logic Layer                         │  │
│  │                                                                 │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │  │
│  │  │  Phase 0 │  │  Phase 1 │  │  Phase 2 │  │  Phase 3 │      │  │
│  │  │  Roles   │  │  GitHub  │  │  Parser  │  │   RAG    │      │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │  │
│  │                                                                 │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │  │
│  │  │  Phase 4 │  │  Phase 6 │  │  Phase 7 │  │  Phase 9 │      │  │
│  │  │   LLM    │  │   Eval   │  │  Report  │  │  Fraud   │      │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                          │                                           │
└──────────────────────────┼───────────────────────────────────────────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
            ▼              ▼              ▼
    ┌──────────────┐ ┌──────────┐ ┌──────────────┐
    │   SQLite     │ │ ChromaDB │ │  OpenAI API  │
    │   Database   │ │ (Vectors)│ │   (GPT-4)    │
    └──────────────┘ └──────────┘ └──────────────┘
            │
            ▼
    ┌──────────────┐
    │  File System │
    │  • Repos     │
    │  • Reports   │
    └──────────────┘
```

---

## 3. Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA FLOW                                    │
└─────────────────────────────────────────────────────────────────────┘

Candidate Input → Validation → Database
       │
       └──────────────┐
                      ▼
              GitHub API → Clone Repo → Local Storage
                      │
                      ▼
              Code Parser → Extract AST → Code Chunks
                      │
                      ▼
              Embedding Model → Vectors → ChromaDB
                      │
                      ▼
              LLM (GPT-4) → Project Summary
                      │
                      ▼
         RAG Retrieval + LLM → Interview Questions → Database
                      │
                      ▼
              User Answers → Database
                      │
                      ▼
         RAG Context + LLM → Evaluation Scores → Database
                      │
                      ▼
              Report Generator → PDF + JSON → File System
                      │
                      ▼
              Recruiter Dashboard → Display Results
```

---

## 4. Database Schema

```
┌─────────────────────────────────────────────────────────────────────┐
│                        DATABASE SCHEMA                               │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│  Candidates  │◄───────│ Repositories │         │ RoleProfiles │
├──────────────┤         ├──────────────┤         ├──────────────┤
│ id (PK)      │         │ id (PK)      │         │ id (PK)      │
│ name         │         │ candidate_id │         │ role_type    │
│ email        │         │ repo_name    │         │ req_skills   │
│ github_url   │         │ tech_stack   │         │ opt_skills   │
│ role_type    │         │ summary      │         │ weights      │
│ created_at   │         │ languages    │         └──────────────┘
└──────┬───────┘         └──────┬───────┘
       │                        │
       │         ┌──────────────┘
       │         │
       ▼         ▼
┌──────────────────┐         ┌──────────────┐
│   Questions      │         │ CodeModules  │
├──────────────────┤         ├──────────────┤
│ id (PK)          │         │ id (PK)      │
│ candidate_id (FK)│         │ repo_id (FK) │
│ question_text    │         │ file_path    │
│ question_type    │         │ functions    │
│ difficulty       │         │ classes      │
│ answer_text      │         │ code_content │
│ time_taken       │         └──────────────┘
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ QuestionScores   │         ┌──────────────┐
├──────────────────┤         │ Evaluations  │
│ id (PK)          │         ├──────────────┤
│ question_id (FK) │◄────────│ id (PK)      │
│ understanding    │         │ candidate_id │
│ technical_depth  │         │ overall_score│
│ accuracy         │         │ strengths    │
│ communication    │         │ weaknesses   │
│ relevance        │         │ hire_rec     │
│ weighted_score   │         │ report_path  │
│ feedback         │         │ fraud_det    │
└──────────────────┘         └──────────────┘
```

---

## 5. Evaluation Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                      EVALUATION PIPELINE                             │
└─────────────────────────────────────────────────────────────────────┘

For Each Question:
    │
    ├─ Step 1: Retrieve Context
    │  │
    │  └─► RAG System → ChromaDB
    │       │
    │       └─► Top 3-5 Relevant Code Chunks
    │
    ├─ Step 2: LLM Evaluation
    │  │
    │  └─► GPT-4 Prompt:
    │       • Question
    │       • Candidate Answer
    │       • Code Context
    │       • Expected Keywords
    │       │
    │       └─► Dimensional Scores (0-10):
    │            • Concept Understanding
    │            • Technical Depth
    │            • Accuracy
    │            • Communication
    │            • Relevance
    │
    ├─ Step 3: Fraud Detection
    │  │
    │  └─► Check for:
    │       • Generic responses
    │       • Short answers (< 20 chars)
    │       • Code inconsistencies
    │       • LLM fraud analysis
    │       │
    │       └─► Fraud Flag (True/False)
    │
    ├─ Step 4: Calculate Weighted Score
    │  │
    │  └─► Formula:
    │       (Understanding × 4 +
    │        Technical × 3 +
    │        Communication × 2 +
    │        Accuracy × 1) / 10 × 10
    │       │
    │       └─► Score (0-100)
    │
    └─ Step 5: Generate Feedback
       │
       └─► LLM generates:
            • Overall feedback text
            • Strengths (2-3 points)
            • Weaknesses (2-3 points)

Aggregate All Questions:
    │
    ├─ Calculate Overall Score (weighted average)
    │
    ├─ Identify Top Strengths & Weaknesses
    │
    ├─ Generate Hire Recommendation:
    │   • Strong Yes (≥85)
    │   • Yes (≥75)
    │   • Maybe (≥60)
    │   • No (≥40)
    │   • Strong No (<40)
    │
    └─ Compile Final Report
```

---

## 6. Scoring Weights

```
Overall Score Calculation:

┌────────────────────────────────────────────┐
│  Concept Understanding     40% │████████│  │
├────────────────────────────────────────────┤
│  Technical Reasoning       30% │██████  │  │
├────────────────────────────────────────────┤
│  Communication             20% │████    │  │
├────────────────────────────────────────────┤
│  Logic & Accuracy          10% │██      │  │
└────────────────────────────────────────────┘

Formula:
Overall = (Understanding × 0.4 +
           Reasoning × 0.3 +
           Communication × 0.2 +
           Logic × 0.1) × 10
```

---

## 7. Question Type Distribution

```
Question Types (6-10 total):

WHY Questions (2-3)          │ Why did you choose X?
  Focus: Reasoning          │ Why this architecture?
  Evaluates: Decision-making │ Why not Y approach?

WHAT Questions (2-3)         │ What does this module do?
  Focus: Understanding       │ What is the purpose of X?
  Evaluates: Knowledge       │ What are the key features?

HOW Questions (2-3)          │ How does X work?
  Focus: Implementation      │ How did you handle Y?
  Evaluates: Technical depth │ How would you improve Z?

WHERE Questions (1-2)        │ Where is X implemented?
  Focus: Architecture        │ Where would you add Y?
  Evaluates: Code organization │ Where is the main logic?

Difficulty Distribution:
├── Easy   (30-40%): Basic understanding
├── Medium (40-50%): Technical details
└── Hard   (20-30%): Advanced concepts
```

---

## 8. Technology Stack Layers

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PRESENTATION LAYER                           │
│  React 18 • Vite • TailwindCSS • React Router • Axios              │
└─────────────────────────────────────────────────────────────────────┘
                                 ▲
                                 │ HTTP/REST
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          API LAYER                                   │
│  FastAPI • Pydantic • CORS Middleware • Background Tasks            │
└─────────────────────────────────────────────────────────────────────┘
                                 ▲
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       BUSINESS LOGIC LAYER                           │
│  Phase Services • LLM Integration • RAG System • Evaluation Engine  │
└─────────────────────────────────────────────────────────────────────┘
                                 ▲
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        DATA ACCESS LAYER                             │
│  SQLAlchemy ORM • ChromaDB Client • GitHub API Client              │
└─────────────────────────────────────────────────────────────────────┘
                                 ▲
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA STORAGE LAYER                           │
│  SQLite • ChromaDB • File System • OpenAI API                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

**End of Architecture Diagrams**
