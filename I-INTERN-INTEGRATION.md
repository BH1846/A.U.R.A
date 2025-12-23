# AURA I-Intern Integration

## Overview

AURA is now integrated with the I-Intern platform as an embedded skill evaluation engine. This integration provides multi-tenancy support with separate portals for students and recruiters.

## Architecture

### Multi-Tenancy Model

```
I-Intern Platform
├── Companies
│   └── Recruiters (can view all applicants for their company)
└── Students (can only see their own applications)

AURA System
├── Applications (linked to I-Intern internships)
├── Candidates (linked to applications)
└── Evaluations (AURA assessment results)
```

### Authentication Flow

1. **I-Intern passes JWT token** to AURA (via URL parameter or header)
2. **AURA validates token** and extracts user information
3. **User is auto-created** in AURA database if first time
4. **Role-based access** controls data visibility

**JWT Token Format:**
```json
{
  "user_id": "123",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "student" | "recruiter",
  "company_id": "456" (optional, for recruiters),
  "company_name": "Acme Corp",
  "exp": 1234567890
}
```

## API Endpoints

### Student Portal (`/api/student/*`)

- `GET /api/student/applications` - List all student's applications
- `GET /api/student/applications/{id}` - Get application details
- `GET /api/student/aura/available` - List available AURA tests
- `GET /api/student/aura/{application_id}/report` - Get AURA report
- `GET /api/student/profile` - Get student profile

### Company Portal (`/api/company/*`)

- `GET /api/company/internships` - List company internships
- `GET /api/company/internships/{id}` - Get internship details
- `GET /api/company/applications` - List applications with filters
- `GET /api/company/applications/{id}` - Get application with AURA data
- `GET /api/company/analytics/overview` - Get analytics dashboard
- `GET /api/company/rankings` - Get candidates ranked by AURA score

### Standalone AURA Endpoints (Public)

- `POST /api/candidates` - Create new candidate
- `GET /api/candidates/{id}` - Get candidate info
- `POST /api/questions/generate` - Generate questions
- `POST /api/answers/submit` - Submit answers
- `GET /api/report/{id}` - Get evaluation report

## Frontend Routes

### Student Portal

- `/student/dashboard` - View all applications and AURA assessments
- `/student/application/{id}` - Application details
- `/student/aura/{applicationId}/report` - AURA report view

### Company/Recruiter Portal

- `/company/dashboard` - Analytics and overview
- `/company/applications` - List and filter applications
- `/company/application/{id}` - Application details with AURA data
- `/company/rankings` - Ranked candidate list
- `/company/internships` - Manage internships

### Standalone (Public)

- `/` - Home page
- `/submit` - Submit repository for assessment
- `/questions/{candidateId}` - Answer questions
- `/report/{candidateId}` - View report
- `/dashboard` - Admin dashboard

## Database Models

### New Tables

**users**
- i_intern_user_id (unique)
- email, name, role
- company_id (for recruiters)
- github_url, resume_url (for students)

**companies**
- i_intern_company_id (unique)
- name, description, website, logo_url

**internships**
- i_intern_internship_id (unique)
- company_id
- title, description, role_type
- aura_enabled, aura_required, aura_passing_score

**applications**
- i_intern_application_id (unique)
- user_id, internship_id
- candidate_id (links to AURA assessment)
- status (pending, aura_invited, aura_completed, etc.)
- timestamps

### Updated Tables

**candidates**
- Added relationship to `applications`

## Configuration

### Backend (.env)

```bash
# JWT Configuration for I-Intern integration
JWT_SECRET=shared-secret-with-i-intern
JWT_ALGORITHM=HS256

# Existing AURA config
DATABASE_URL=postgresql://...
GROQ_API_KEY=...
UPLOADCARE_PUB_KEY=...
```

### Frontend

Token is automatically extracted from:
1. URL parameter: `?token=xxx`
2. LocalStorage: `aura_auth_token`

## Integration Steps

### For I-Intern Platform

1. **Generate JWT token** with user information
2. **Redirect to AURA** with token in URL:
   ```
   https://aura.example.com/student/dashboard?token=xxx
   ```
3. **Receive webhook** when AURA assessment completes (optional)

### For AURA Standalone

1. Keep existing flow working
2. Public endpoints remain accessible
3. No authentication required for standalone use

## Data Isolation

### Student Access
- Can only see own applications
- Can only access own AURA reports
- Cannot see other students' data

### Recruiter Access
- Can see all applications for their company's internships
- Can view AURA assessments for applicants
- Cannot see other companies' data

### Admin Access
- Can see all data across all companies
- Can manage system configuration

## Deployment

### Backend

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations (creates new tables)
python -m alembic upgrade head

# Start server
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
# Install dependencies
npm install

# Build for production
npm run build

# Serve with nginx (included in Dockerfile)
```

## API Authentication

All protected endpoints require JWT token in Authorization header:

```bash
curl -H "Authorization: Bearer <token>" \
  https://api.aura.example.com/api/student/applications
```

## Testing

### Generate Test Token

```python
import jwt
from datetime import datetime, timedelta

# Student token
student_token = jwt.encode({
    "user_id": "1",
    "email": "student@test.com",
    "name": "Test Student",
    "role": "student",
    "exp": datetime.utcnow() + timedelta(days=1)
}, "your-secret-key", algorithm="HS256")

# Recruiter token
recruiter_token = jwt.encode({
    "user_id": "2",
    "email": "recruiter@company.com",
    "name": "Test Recruiter",
    "role": "recruiter",
    "company_id": 1,
    "company_name": "Test Company",
    "exp": datetime.utcnow() + timedelta(days=1)
}, "your-secret-key", algorithm="HS256")
```

### Test Endpoints

```bash
# Student - get applications
curl -H "Authorization: Bearer $STUDENT_TOKEN" \
  http://localhost:8000/api/student/applications

# Recruiter - get analytics
curl -H "Authorization: Bearer $RECRUITER_TOKEN" \
  http://localhost:8000/api/company/analytics/overview
```

## Backwards Compatibility

- Existing AURA functionality remains intact
- Standalone mode works without authentication
- Public endpoints are unaffected
- Old URLs continue to work

## Next Steps

1. **Configure JWT_SECRET** - Coordinate with I-Intern team
2. **Deploy database migrations** - Create new tables
3. **Test integration** - Verify token flow
4. **Set up webhooks** - Notify I-Intern of assessment completion
5. **Monitor logs** - Check for authentication issues

## Support

For integration issues, check:
- JWT token format and expiry
- Database connection and migrations
- CORS configuration for I-Intern domain
- API endpoint accessibility
