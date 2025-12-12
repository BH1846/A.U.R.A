# AURA API Documentation

## Base URL
```
http://localhost:8000/api
```

## Authentication
Currently no authentication required for local development. In production, implement JWT/OAuth.

---

## Endpoints

### 1. Root Endpoint

#### `GET /`
Get API status and version.

**Response:**
```json
{
  "message": "AURA - Automated Understanding & Role Assessment API",
  "version": "1.0.0",
  "status": "active"
}
```

---

### 2. Role Management

#### `GET /api/roles`
Get all available role types.

**Response:**
```json
{
  "roles": ["Frontend", "Backend", "ML", "DevOps", "FullStack"],
  "message": "Available role types for evaluation"
}
```

#### `GET /api/roles/{role_type}/skills`
Get required and optional skills for a specific role.

**Parameters:**
- `role_type` (path): Role type (Frontend, Backend, ML, DevOps, FullStack)

**Response:**
```json
{
  "role_type": "Frontend",
  "description": "Frontend Development Internship...",
  "required_skills": ["React", "JavaScript/TypeScript", "HTML/CSS", "State Management", "API Integration"],
  "optional_skills": ["Next.js", "Testing", "UI Frameworks"]
}
```

---

### 3. Candidate Submission

#### `POST /api/candidate/submit`
Submit candidate information and GitHub repository for analysis.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "github_url": "https://github.com/username/repository",
  "role_type": "Frontend"
}
```

**Validation:**
- `email`: Must be valid email format
- `github_url`: Must be valid GitHub repository URL
- `role_type`: Must be one of available roles

**Response:**
```json
{
  "candidate_id": 1,
  "message": "Candidate submitted successfully. Repository analysis in progress.",
  "status": "processing"
}
```

**Process:**
1. Validates GitHub repository accessibility
2. Creates candidate record in database
3. Starts background processing:
   - Clones repository
   - Analyzes project structure
   - Generates questions

**Errors:**
- `400`: Invalid GitHub repository
- `500`: Processing error

---

### 4. Status Check

#### `GET /api/candidate/{candidate_id}/status`
Check the processing status of a candidate's submission.

**Parameters:**
- `candidate_id` (path): Candidate ID

**Response (Processing):**
```json
{
  "status": "processing",
  "message": "Analysis in progress"
}
```

**Response (Ready):**
```json
{
  "status": "ready",
  "total_questions": 8,
  "answered_questions": 0
}
```

**Response (Completed):**
```json
{
  "status": "completed",
  "total_questions": 8,
  "answered_questions": 8
}
```

---

### 5. Get Questions

#### `GET /api/candidate/{candidate_id}/questions`
Retrieve interview questions generated for the candidate.

**Parameters:**
- `candidate_id` (path): Candidate ID

**Response:**
```json
[
  {
    "question_id": 1,
    "question_text": "What is the main purpose of your project?",
    "question_type": "what",
    "difficulty": "easy",
    "context": "Project README"
  },
  {
    "question_id": 2,
    "question_text": "Why did you choose React for this project?",
    "question_type": "why",
    "difficulty": "medium",
    "context": "Technology choice"
  }
]
```

**Question Types:**
- `why`: Reasoning and decision-making
- `what`: Understanding components and functionality
- `how`: Implementation details
- `where`: Architecture and code organization

**Difficulty Levels:**
- `easy`: Basic understanding
- `medium`: Moderate technical depth
- `hard`: Advanced concepts

**Errors:**
- `404`: Questions not yet generated or candidate not found

---

### 6. Submit Answers

#### `POST /api/candidate/{candidate_id}/answers`
Submit candidate's answers to interview questions.

**Parameters:**
- `candidate_id` (path): Candidate ID

**Request Body:**
```json
{
  "answers": [
    {
      "question_id": 1,
      "answer_text": "This project is a task management application...",
      "time_taken": 120
    },
    {
      "question_id": 2,
      "answer_text": "I chose React because of its component-based architecture...",
      "time_taken": 180
    }
  ]
}
```

**Fields:**
- `question_id`: ID of the question being answered
- `answer_text`: Candidate's answer (min 20 characters recommended)
- `time_taken`: Time spent on answer in seconds

**Response:**
```json
{
  "message": "Answers submitted successfully. Evaluation in progress."
}
```

**Process:**
1. Saves all answers to database
2. Starts background evaluation:
   - Retrieves relevant code context via RAG
   - Uses LLM to evaluate each answer
   - Calculates scores across dimensions
   - Detects fraud signals
   - Generates comprehensive report

**Errors:**
- `404`: Candidate not found
- `500`: Submission error

---

### 7. Get Evaluation Report

#### `GET /api/candidate/{candidate_id}/report`
Get the evaluation report summary.

**Parameters:**
- `candidate_id` (path): Candidate ID

**Response:**
```json
{
  "overall_score": 78.5,
  "understanding_score": 80.0,
  "reasoning_score": 75.0,
  "communication_score": 82.0,
  "logic_score": 76.0,
  "hire_recommendation": "yes",
  "confidence": 0.80,
  "report_pdf_path": "/path/to/report.pdf"
}
```

**Scoring:**
- All scores are on a 0-100 scale
- `overall_score`: Weighted average of all dimensions
- Dimension weights:
  - Understanding: 40%
  - Reasoning: 30%
  - Communication: 20%
  - Logic: 10%

**Hire Recommendations:**
- `strong_yes`: Score ≥ 85 (Confidence: 0.95)
- `yes`: Score ≥ 75 (Confidence: 0.80)
- `maybe`: Score ≥ 60 (Confidence: 0.60)
- `no`: Score ≥ 40 (Confidence: 0.30)
- `strong_no`: Score < 40 (Confidence: 0.10)

**Errors:**
- `404`: Evaluation not yet complete

---

### 8. Download Report PDF

#### `GET /api/candidate/{candidate_id}/report/download`
Download the detailed PDF report.

**Parameters:**
- `candidate_id` (path): Candidate ID

**Response:**
- File download (application/pdf)
- Filename: `candidate_{id}_report_{timestamp}.pdf`

**Report Contents:**
1. Candidate Information
2. Project Summary
3. Overall Scores (with visual charts)
4. Score Breakdown by Dimension
5. Hiring Recommendation
6. Strengths and Weaknesses
7. Detailed Recommendations
8. Question-by-Question Analysis
9. Fraud Detection Results (if applicable)

**Errors:**
- `404`: Report not found or not yet generated

---

### 9. Recruiter Dashboard

#### `GET /api/recruiter/candidates`
List all candidates with their evaluation status.

**Response:**
```json
{
  "candidates": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "role_type": "Frontend",
      "github_url": "https://github.com/username/repo",
      "created_at": "2024-01-15T10:30:00",
      "overall_score": 78.5,
      "hire_recommendation": "yes",
      "status": "evaluated"
    },
    {
      "id": 2,
      "name": "Jane Smith",
      "email": "jane@example.com",
      "role_type": "Backend",
      "github_url": "https://github.com/username/repo2",
      "created_at": "2024-01-16T14:20:00",
      "overall_score": null,
      "hire_recommendation": null,
      "status": "pending"
    }
  ],
  "total": 2
}
```

**Status Values:**
- `pending`: Processing or awaiting answers
- `evaluated`: Evaluation complete

---

#### `GET /api/recruiter/candidate/{candidate_id}`
Get detailed information about a specific candidate.

**Parameters:**
- `candidate_id` (path): Candidate ID

**Response:**
```json
{
  "candidate": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role_type": "Frontend",
    "github_url": "https://github.com/username/repo"
  },
  "repository": {
    "name": "awesome-project",
    "tech_stack": ["JavaScript", "React", "Node.js"],
    "project_summary": "A task management application..."
  },
  "evaluation": {
    "overall_score": 78.5,
    "scores": {
      "understanding": 80.0,
      "reasoning": 75.0,
      "communication": 82.0,
      "logic": 76.0
    },
    "strengths": [
      "Clear understanding of React components",
      "Good code organization"
    ],
    "weaknesses": [
      "Could provide more technical depth",
      "Limited discussion of optimization"
    ],
    "hire_recommendation": "yes",
    "fraud_detected": false
  },
  "questions_count": 8
}
```

**Errors:**
- `404`: Candidate not found

---

## Evaluation Dimensions Explained

### 1. Concept Understanding (40%)
- Does the candidate understand core concepts?
- Can they explain why certain decisions were made?
- Do they grasp the project's purpose and architecture?

### 2. Technical Reasoning (30%)
- Is the technical explanation detailed?
- Do they demonstrate logical thinking?
- Can they justify technical choices?

### 3. Communication (20%)
- Is the explanation clear and articulated?
- Do they structure their answers well?
- Is the language professional?

### 4. Logic & Accuracy (10%)
- Is the answer factually correct?
- Does it match the actual code?
- Are there contradictions?

---

## Fraud Detection

The system automatically detects potential fraud signals:

1. **Generic Responses**: Copy-paste or template answers
2. **Short Answers**: Answers < 20 characters
3. **Code Mismatch**: Answers inconsistent with actual code
4. **Unrelated Content**: Answers not related to the project

**Fraud Signals in Response:**
```json
{
  "fraud_detected": true,
  "fraud_signals": [
    "Q3: Generic response detected: 'i don't know'",
    "Q5: Answer too short (< 20 characters)"
  ]
}
```

---

## Error Handling

All endpoints return errors in this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common HTTP Status Codes:**
- `200`: Success
- `400`: Bad Request (validation error)
- `404`: Not Found
- `500`: Internal Server Error

---

## Rate Limiting

No rate limiting in current version. For production:
- Implement rate limiting per IP
- Current setting: 60 requests per minute (configurable)

---

## Webhooks (Future Feature)

Planned for future versions:
- Notify when repository analysis completes
- Notify when evaluation is ready
- Integration with external HR systems

---

## Example Workflow

### Complete Candidate Evaluation Flow

```javascript
// 1. Submit candidate
POST /api/candidate/submit
{
  "name": "John Doe",
  "email": "john@example.com",
  "github_url": "https://github.com/john/project",
  "role_type": "Frontend"
}
// Returns: { candidate_id: 1 }

// 2. Poll status (every 3 seconds)
GET /api/candidate/1/status
// Wait until status: "ready"

// 3. Get questions
GET /api/candidate/1/questions
// Returns: Array of 6-10 questions

// 4. Submit answers
POST /api/candidate/1/answers
{
  "answers": [
    { "question_id": 1, "answer_text": "...", "time_taken": 120 },
    { "question_id": 2, "answer_text": "...", "time_taken": 180 }
  ]
}

// 5. Wait for evaluation (30-60 seconds)
// Poll status or wait

// 6. Get report
GET /api/candidate/1/report
// Returns: Evaluation scores and recommendation

// 7. Download PDF
GET /api/candidate/1/report/download
// Downloads detailed PDF report
```

---

## Interactive API Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI documentation where you can:
- Test all endpoints
- See request/response schemas
- Execute API calls directly

---

## Support

For API issues or questions:
1. Check server logs for detailed error messages
2. Verify all environment variables are set correctly
3. Ensure database is initialized
4. Review the SETUP.md file for configuration help

---

**Last Updated**: 2024
**API Version**: 1.0.0
