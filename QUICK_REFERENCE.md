# Quick Reference: JD-Based Questions Feature

## 🚀 Quick Start

### 1. Run Database Migration
```bash
cd backend
python scripts/migrate_add_jd_support.py
```

### 2. Create a Job Description (Company/Admin)
```bash
curl -X POST http://localhost:8000/api/company/job-descriptions \
  -H "Authorization: Bearer YOUR_RECRUITER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "internship_id": 1,
    "description_text": "We are seeking a Backend Developer with strong Python skills...",
    "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
    "preferred_skills": ["AWS", "Redis", "Kubernetes"]
  }'
```

### 3. Student Starts Assessment
```bash
curl -X POST http://localhost:8000/api/student/aura/1/start \
  -H "Authorization: Bearer YOUR_STUDENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

## 📋 API Endpoints Cheat Sheet

### Company Routes (Recruiters & Admins)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/company/job-descriptions` | Create JD & generate 10 questions |
| GET | `/api/company/job-descriptions/{internship_id}` | Get JD and questions |
| PUT | `/api/company/job-descriptions/{internship_id}` | Update JD & regenerate questions |
| DELETE | `/api/company/job-descriptions/{internship_id}` | Deactivate JD |

### Student Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/student/aura/{application_id}/start` | Start assessment (JD or GitHub) |
| GET | `/api/student/aura/{application_id}/questions` | Get questions |

## 🔑 Key Features

- ✅ **10 standardized questions** per job description
- ✅ **Same questions for all candidates** (fair comparison)
- ✅ **One-time posting** (reused for all applicants)
- ✅ **Company & admin only** access
- ✅ **Auto-generated** from job description
- ✅ **No GitHub required** for students

## 🎯 Question Distribution

| Type | Count | Purpose |
|------|-------|---------|
| WHY | 2 | Motivation, reasoning |
| WHAT | 3 | Concepts, technologies |
| HOW | 3 | Implementation, problem-solving |
| WHERE | 2 | Application, architecture |

**Difficulty:** 3 Easy, 5 Medium, 2 Hard

## 🔐 Authorization

```python
# Company/Admin only
@router.post("/job-descriptions")
async def create_job_description(
    current_user: CurrentUser = Depends(require_recruiter_or_admin)
):
    ...
```

## 📊 Database Schema

```sql
-- New table
CREATE TABLE job_descriptions (
    id INTEGER PRIMARY KEY,
    internship_id INTEGER UNIQUE,
    description_text TEXT,
    role_type VARCHAR(50),
    required_skills JSON,
    preferred_skills JSON,
    questions_data JSON,  -- 10 questions
    created_by INTEGER,
    is_active BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Updated tables
ALTER TABLE questions ADD COLUMN job_description_id INTEGER;
ALTER TABLE questions ADD COLUMN source VARCHAR(20) DEFAULT 'github';
ALTER TABLE internships ADD COLUMN use_jd_questions BOOLEAN DEFAULT 0;
```

## 🔄 Workflow

### Company Posts JD
```
1. POST /job-descriptions
2. System generates 10 questions via LLM
3. internship.use_jd_questions = True
4. Questions stored in JD
```

### Student Takes Assessment
```
1. POST /aura/{app_id}/start
2. Check: internship.use_jd_questions?
   - YES: Copy 10 questions from JD
   - NO: Process GitHub repo (existing flow)
3. GET /aura/{app_id}/questions
4. Answer questions
5. Get evaluated (same pipeline)
```

## 🧪 Testing Checklist

- [ ] Run migration script
- [ ] Create JD via API (recruiter token)
- [ ] Verify 10 questions generated
- [ ] Check `use_jd_questions = True`
- [ ] Start student assessment
- [ ] Verify questions retrieved
- [ ] Submit answers
- [ ] Check evaluation works

## 📝 Example JD Questions

1. **WHY** - "Why are you interested in this Backend Developer role?"
2. **WHAT** - "What experience do you have with Python, FastAPI, PostgreSQL?"
3. **WHAT** - "What are the key responsibilities of a Backend developer?"
4. **HOW** - "How do you ensure code quality in your projects?"
5. **HOW** - "How would you approach learning FastAPI?"
6. **HOW** - "How do you handle debugging in backend systems?"
7. **WHERE** - "Where would you use Docker in production?"
8. **WHERE** - "Where have you solved complex technical problems?"
9. **WHY** - "Why is teamwork important in development?"
10. **HOW** - "How would you design a scalable architecture?" (Hard)

## 🛠️ Configuration

In `config.py`:
```python
MAX_QUESTIONS = 10  # Number of questions to generate
```

## 📚 Documentation Files

- `JOB_DESCRIPTION_QUESTIONS.md` - Complete documentation
- `IMPLEMENTATION_SUMMARY.md` - What was changed
- `QUICK_REFERENCE.md` - This file

## 🆘 Troubleshooting

**Q: JD creation fails?**
- Check recruiter has company_id
- Verify internship exists
- Check no duplicate JD for internship

**Q: Questions not generated?**
- Check GROQ_API_KEY is set
- Verify LLM service is running
- Check logs for errors
- Fallback questions will be used

**Q: Students can't start assessment?**
- Verify application status is PENDING or AURA_INVITED
- Check internship has either JD or student provides GitHub URL
- Verify student is authenticated

## 💡 Tips

- **Create JD early** - Before students apply
- **Review questions** - Check generated questions make sense
- **Update carefully** - Updating JD regenerates ALL questions
- **Don't delete** - Deactivate instead (soft delete)
- **Test first** - Try with test internship before production

## 🔗 Related Files

- Models: `backend/models/database.py`, `backend/models/multi_tenant.py`
- Routes: `backend/routes/company.py`, `backend/routes/student.py`
- Service: `backend/core/phase4_llm/llm_service.py`
- Auth: `backend/core/auth/auth.py`
- Migration: `backend/scripts/migrate_add_jd_support.py`
