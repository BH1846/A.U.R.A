# Job Description-Based Question Generation

## Overview

AURA now supports **two modes** for generating interview questions:

1. **GitHub-based questions** - Traditional mode analyzing candidate's GitHub projects
2. **Job Description (JD) based questions** - NEW mode using standardized questions from the job posting

## Key Features

### 1. One-Time JD Posting
- Companies can post a job description once per internship
- The system generates **exactly 10 standardized questions** from the JD
- These questions are **reused for all candidates** applying to that job
- Ensures fairness and consistency across all applicants

### 2. Same Questions for All Candidates
- All candidates applying to the same job get the **identical 10 questions**
- Questions focus on role requirements, skills, and general technical knowledge
- Questions are not dependent on individual GitHub projects
- Enables fair comparison between candidates

### 3. Company & Admin Access Only
- Job descriptions can only be created/edited by:
  - **Company recruiters** (for their own internships)
  - **System admins** (for any internship)
- Dedicated page/API endpoints for JD management
- Secure authentication ensures only authorized access

## Database Models

### JobDescription Model
```python
class JobDescription:
    id: int
    internship_id: int  # One JD per internship
    description_text: str  # Full job description
    role_type: str  # Frontend, Backend, ML, DevOps
    required_skills: List[str]  # Required skills from JD
    preferred_skills: List[str]  # Nice-to-have skills
    questions_data: JSON  # 10 pre-generated questions
    created_by: int  # User who created it
    is_active: bool
    created_at: datetime
    updated_at: datetime
```

### Updated Question Model
```python
class Question:
    # ... existing fields ...
    job_description_id: int  # Links to JD if using JD questions
    source: str  # 'jd' or 'github'
```

### Updated Internship Model
```python
class Internship:
    # ... existing fields ...
    use_jd_questions: bool  # Toggle between JD and GitHub questions
```

## API Endpoints

### Company Routes (Recruiters & Admins Only)

#### Create Job Description
```http
POST /api/company/job-descriptions
Authorization: Bearer <token>
Content-Type: application/json

{
  "internship_id": 123,
  "description_text": "We are looking for a Backend Developer...",
  "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
  "preferred_skills": ["AWS", "Redis", "CI/CD"]
}

Response:
{
  "id": 456,
  "internship_id": 123,
  "description_text": "...",
  "role_type": "Backend",
  "required_skills": [...],
  "preferred_skills": [...],
  "questions_count": 10,
  "questions": [
    {
      "question_text": "Why are you interested in this Backend Developer role?",
      "question_type": "why",
      "difficulty": "easy",
      "context": "Motivation and interest",
      "expected_keywords": ["interest", "passion", "backend", "learn"],
      "evaluation_criteria": ["Clear motivation", "Alignment with role"]
    },
    // ... 9 more questions
  ],
  "created_at": "2026-01-22T10:00:00",
  "is_active": true
}
```

#### Get Job Description
```http
GET /api/company/job-descriptions/{internship_id}
Authorization: Bearer <token>

Response: Same as create response
```

#### Update Job Description
```http
PUT /api/company/job-descriptions/{internship_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "description_text": "Updated job description...",
  "required_skills": ["Python", "FastAPI", "PostgreSQL"],
  "preferred_skills": ["Kubernetes"]
}

Note: Questions are regenerated when JD is updated
```

#### Delete Job Description
```http
DELETE /api/company/job-descriptions/{internship_id}
Authorization: Bearer <token>

Response:
{
  "message": "Job description deactivated successfully"
}

Note: Soft delete - sets is_active=False and use_jd_questions=False
```

### Student Routes

#### Start AURA Assessment
```http
POST /api/student/aura/{application_id}/start
Authorization: Bearer <token>
Content-Type: application/json

{
  "github_url": "https://github.com/user/repo"  // Optional if JD questions
}

Response (JD-based):
{
  "message": "AURA assessment started with job description questions",
  "candidate_id": 789,
  "question_source": "job_description",
  "total_questions": 10
}

Response (GitHub-based):
{
  "message": "AURA assessment started. Processing GitHub repository...",
  "candidate_id": 789,
  "question_source": "github",
  "status": "processing"
}
```

#### Get Questions
```http
GET /api/student/aura/{application_id}/questions
Authorization: Bearer <token>

Response:
{
  "questions": [
    {
      "question_id": 1001,
      "question_text": "What experience do you have with Python, FastAPI, PostgreSQL?",
      "question_type": "what",
      "difficulty": "medium",
      "context": "Technical skills",
      "source": "jd"
    },
    // ... 9 more questions
  ],
  "total": 10
}
```

## Question Generation Logic

### JD-Based Questions (10 questions)

The LLM generates questions with this distribution:

**By Type:**
- 2 WHY questions - Understanding motivations and reasoning
- 3 WHAT questions - Understanding concepts and technologies
- 3 HOW questions - Understanding implementation and problem-solving
- 2 WHERE questions - Understanding application and architecture

**By Difficulty:**
- 3 Easy questions - Basic concepts, motivation
- 5 Medium questions - Technical understanding, experience
- 2 Hard questions - Problem-solving, architecture

**Each Question Includes:**
- `question_text` - The actual question
- `question_type` - why/what/how/where
- `difficulty` - easy/medium/hard
- `context` - Reference to JD requirement
- `expected_keywords` - 5-7 keywords for evaluation
- `evaluation_criteria` - 3-4 criteria for scoring

### GitHub-Based Questions

Remains unchanged - generates questions specific to the candidate's project.

## Workflow

### For Companies

1. **Post Internship** (via I-Intern platform)
2. **Create Job Description** (AURA company portal)
   - Write detailed JD
   - Specify required/preferred skills
   - System auto-generates 10 questions
3. **Review Questions** (optional)
   - Can regenerate by updating JD
4. **Enable JD Questions** (automatic when JD created)
   - `internship.use_jd_questions = True`
5. **Review Applications**
   - All candidates answer same questions
   - Fair comparison of responses

### For Students

1. **Apply to Internship** (via I-Intern platform)
2. **Receive AURA Invitation**
3. **Start Assessment**
   - If JD questions: Get 10 questions immediately
   - If GitHub questions: Provide GitHub URL, wait for processing
4. **Answer Questions**
   - Same interface for both modes
5. **Submit & Get Evaluated**
   - Evaluation works the same for both modes

## Benefits

### For Companies
✅ **Consistency** - All candidates get same questions
✅ **Fairness** - No bias from project quality/complexity
✅ **Efficiency** - No need to wait for GitHub processing
✅ **Control** - Define exactly what skills to test
✅ **Comparison** - Easy to compare candidate responses

### For Students
✅ **Faster** - No GitHub analysis time
✅ **Fair** - Everyone gets same questions
✅ **Clarity** - Questions directly related to job requirements
✅ **Preparation** - Can prepare based on JD skills

### For System
✅ **Scalable** - No repository cloning/processing overhead
✅ **Cost-effective** - Questions generated once, used many times
✅ **Reliable** - No dependency on GitHub availability
✅ **Flexible** - Companies can choose mode per internship

## Configuration

### Switching Modes

Companies can choose per internship:

```python
# Use JD questions
internship.use_jd_questions = True  # Set automatically when JD created

# Use GitHub questions
internship.use_jd_questions = False  # Default or when JD deleted
```

### Settings

In `config.py`:
```python
MAX_QUESTIONS = 10  # Number of questions to generate
```

## Example Questions from JD

**For a Backend Developer role:**

1. **WHY** - "Why are you interested in this Backend Developer position?"
2. **WHAT** - "What experience do you have with Python, FastAPI, and PostgreSQL?"
3. **WHAT** - "What are the key responsibilities of a Backend developer?"
4. **HOW** - "How do you ensure code quality in your projects?"
5. **HOW** - "How would you approach learning a new technology required for this role?"
6. **HOW** - "How do you handle debugging in backend development?"
7. **WHERE** - "Where would you use Docker in production applications?"
8. **WHERE** - "Where have you demonstrated problem-solving skills in past work?"
9. **WHY** - "Why is collaboration important in development teams?"
10. **HOW** - "How would you design a scalable backend architecture?" (Hard)

## Security & Authorization

### Access Control Matrix

| Action | Student | Recruiter | Admin |
|--------|---------|-----------|-------|
| Create JD | ❌ | ✅ (own company) | ✅ (all) |
| View JD | ❌ | ✅ (own company) | ✅ (all) |
| Update JD | ❌ | ✅ (own company) | ✅ (all) |
| Delete JD | ❌ | ✅ (own company) | ✅ (all) |
| Answer Questions | ✅ | ❌ | ❌ |

### Authentication

Uses existing I-Intern JWT authentication:
```python
@router.post("/job-descriptions")
async def create_job_description(
    current_user: CurrentUser = Depends(require_recruiter_or_admin)
):
    # Only recruiters and admins can access
    ...
```

## Migration Guide

### Existing Internships
- Continue using GitHub-based questions by default
- Can add JD anytime to switch to JD questions
- No impact on existing assessments

### New Internships
- Choose mode when setting up AURA
- Can switch modes before first candidate applies
- Cannot switch after candidates have started assessment

## Future Enhancements

Potential improvements:
- [ ] Question bank/templates per role type
- [ ] Custom question editing before generation
- [ ] Mix of JD and GitHub questions
- [ ] Company-specific question pools
- [ ] Question difficulty adjustment
- [ ] Multi-language support for questions
- [ ] A/B testing different question sets

## Support

For questions or issues:
- **Technical**: Check logs in `backend/logs/`
- **API**: Refer to `/docs` endpoint
- **Database**: Run migrations for new tables
