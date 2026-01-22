"""
Student portal API routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from models import get_db
from models.database import Candidate, Evaluation, Question, QuestionScore, JobDescription
from models.multi_tenant import Internship, Application, ApplicationStatus, User
from core.auth import require_student, CurrentUser
from loguru import logger

router = APIRouter(prefix="/api/student", tags=["student"])


# ============= My Applications =============

@router.get("/applications")
async def get_my_applications(
    current_user: CurrentUser = Depends(require_student),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """Get all applications for current student"""
    applications = db.query(Application).filter(
        Application.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    total = db.query(Application).filter(
        Application.user_id == current_user.id
    ).count()
    
    items = []
    for app in applications:
        internship = db.query(Internship).filter(Internship.id == app.internship_id).first()
        
        aura_data = None
        if app.candidate_id:
            candidate = db.query(Candidate).filter(Candidate.id == app.candidate_id).first()
            if candidate:
                evaluation = db.query(Evaluation).filter(Evaluation.candidate_id == candidate.id).first()
                if evaluation:
                    aura_data = {
                        "completed": True,
                        "score": evaluation.overall_score,
                        "completed_at": app.aura_completed_at
                    }
                else:
                    aura_data = {"completed": False, "in_progress": True}
        
        items.append({
            "id": app.id,
            "internship": {
                "id": internship.id,
                "title": internship.title,
                "company_name": internship.company.name if internship.company else "Unknown",
                "role_type": internship.role_type,
                "location": internship.location,
                "aura_enabled": internship.aura_enabled,
                "aura_required": internship.aura_required
            },
            "status": app.status,
            "applied_at": app.applied_at,
            "aura": aura_data
        })
    
    return {"items": items, "total": total}


@router.get("/applications/{application_id}")
async def get_application_details(
    application_id: int,
    current_user: CurrentUser = Depends(require_student),
    db: Session = Depends(get_db)
):
    """Get detailed application information"""
    app = db.query(Application).filter(
        Application.id == application_id,
        Application.user_id == current_user.id
    ).first()
    
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    internship = db.query(Internship).filter(Internship.id == app.internship_id).first()
    
    result = {
        "id": app.id,
        "internship": {
            "id": internship.id,
            "title": internship.title,
            "description": internship.description,
            "company_name": internship.company.name if internship.company else "Unknown",
            "role_type": internship.role_type,
            "location": internship.location,
            "duration_months": internship.duration_months,
            "aura_enabled": internship.aura_enabled,
            "aura_required": internship.aura_required,
            "deadline": internship.deadline
        },
        "status": app.status,
        "applied_at": app.applied_at,
        "aura_invited_at": app.aura_invited_at,
        "aura_started_at": app.aura_started_at,
        "aura_completed_at": app.aura_completed_at
    }
    
    return result


# ============= AURA Assessment =============

@router.get("/aura/available")
async def get_available_aura_tests(
    current_user: CurrentUser = Depends(require_student),
    db: Session = Depends(get_db)
):
    """Get applications where AURA test is available but not started"""
    applications = db.query(Application).filter(
        Application.user_id == current_user.id,
        Application.status == ApplicationStatus.AURA_INVITED,
        Application.candidate_id.is_(None)
    ).all()
    
    items = []
    for app in applications:
        internship = db.query(Internship).filter(Internship.id == app.internship_id).first()
        items.append({
            "application_id": app.id,
            "internship_title": internship.title,
            "company_name": internship.company.name if internship.company else "Unknown",
            "invited_at": app.aura_invited_at
        })
    
    return {"items": items, "total": len(items)}


class StartAuraRequest(BaseModel):
    """Request to start AURA assessment"""
    github_url: Optional[str] = None


@router.post("/aura/{application_id}/start")
async def start_aura_assessment(
    application_id: int,
    request: StartAuraRequest,
    background_tasks: BackgroundTasks,
    current_user: CurrentUser = Depends(require_student),
    db: Session = Depends(get_db)
):
    """
    Start AURA assessment for an application
    Uses JD questions if available, otherwise requires GitHub URL
    """
    app = db.query(Application).filter(
        Application.id == application_id,
        Application.user_id == current_user.id
    ).first()
    
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    if app.status not in [ApplicationStatus.PENDING, ApplicationStatus.AURA_INVITED]:
        raise HTTPException(status_code=400, detail="Application not eligible for AURA assessment")
    
    # Get internship and check if it uses JD questions
    internship = db.query(Internship).filter(Internship.id == app.internship_id).first()
    if not internship:
        raise HTTPException(status_code=404, detail="Internship not found")
    
    try:
        # Check if candidate already exists for this application
        if app.candidate_id:
            raise HTTPException(status_code=400, detail="AURA assessment already started")
        
        # Create candidate
        candidate = Candidate(
            name=current_user.name,
            email=current_user.email,
            github_url=request.github_url or current_user.github_url or "",
            role_type=internship.role_type
        )
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
        
        # Link application to candidate
        app.candidate_id = candidate.id
        app.status = ApplicationStatus.AURA_IN_PROGRESS
        app.aura_started_at = datetime.utcnow()
        db.commit()
        
        # Generate questions based on internship settings
        if internship.use_jd_questions:
            # Use JD questions
            job_description = db.query(JobDescription).filter(
                JobDescription.internship_id == internship.id,
                JobDescription.is_active == True
            ).first()
            
            if not job_description:
                raise HTTPException(status_code=400, detail="Job description not found for this internship")
            
            logger.info(f"Using JD questions for application {application_id}")
            
            # Create questions from JD
            for q_data in job_description.questions_data:
                question = Question(
                    candidate_id=candidate.id,
                    job_description_id=job_description.id,
                    question_text=q_data['question_text'],
                    question_type=q_data['question_type'],
                    difficulty=q_data['difficulty'],
                    context=q_data['context'],
                    expected_keywords=q_data['expected_keywords'],
                    source='jd'
                )
                db.add(question)
            
            db.commit()
            
            return {
                "message": "AURA assessment started with job description questions",
                "candidate_id": candidate.id,
                "question_source": "job_description",
                "total_questions": len(job_description.questions_data)
            }
            
        else:
            # Use GitHub-based questions
            if not request.github_url and not current_user.github_url:
                raise HTTPException(status_code=400, detail="GitHub URL required for this assessment")
            
            github_url = request.github_url or current_user.github_url
            
            logger.info(f"Starting GitHub-based assessment for application {application_id}")
            
            # Process repository in background
            from main import process_repository
            background_tasks.add_task(process_repository, candidate.id, github_url, internship.role_type)
            
            return {
                "message": "AURA assessment started. Processing GitHub repository...",
                "candidate_id": candidate.id,
                "question_source": "github",
                "status": "processing"
            }
            
    except Exception as e:
        db.rollback()
        logger.error(f"Error starting AURA assessment: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start assessment: {str(e)}")


@router.get("/aura/{application_id}/questions")
async def get_aura_questions(
    application_id: int,
    current_user: CurrentUser = Depends(require_student),
    db: Session = Depends(get_db)
):
    """Get questions for AURA assessment"""
    app = db.query(Application).filter(
        Application.id == application_id,
        Application.user_id == current_user.id
    ).first()
    
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    if not app.candidate_id:
        raise HTTPException(status_code=400, detail="AURA assessment not started")
    
    questions = db.query(Question).filter(Question.candidate_id == app.candidate_id).all()
    
    if not questions:
        raise HTTPException(status_code=404, detail="Questions not yet generated")
    
    return {
        "questions": [
            {
                "question_id": q.id,
                "question_text": q.question_text,
                "question_type": q.question_type,
                "difficulty": q.difficulty,
                "context": q.context,
                "source": q.source
            }
            for q in questions
        ],
        "total": len(questions)
    }


@router.get("/aura/{application_id}/report")
async def get_my_aura_report(
    application_id: int,
    current_user: CurrentUser = Depends(require_student),
    db: Session = Depends(get_db)
):
    """Get AURA assessment report for student's application"""
    app = db.query(Application).filter(
        Application.id == application_id,
        Application.user_id == current_user.id
    ).first()
    
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    if not app.candidate_id:
        raise HTTPException(status_code=400, detail="AURA assessment not started")
    
    candidate = db.query(Candidate).filter(Candidate.id == app.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate data not found")
    
    evaluation = db.query(Evaluation).filter(Evaluation.candidate_id == candidate.id).first()
    if not evaluation:
        raise HTTPException(status_code=400, detail="Assessment not completed")
    
    # Get question scores
    questions = db.query(Question).filter(Question.candidate_id == candidate.id).all()
    question_scores = []
    for q in questions:
        score = db.query(QuestionScore).filter(QuestionScore.question_id == q.id).first()
        if score:
            question_scores.append({
                "question_type": q.question_type,
                "difficulty": q.difficulty,
                "concept_understanding": score.concept_understanding,
                "technical_depth": score.technical_depth,
                "accuracy": score.accuracy,
                "communication": score.communication,
                "relevance": score.relevance,
                "weighted_score": score.weighted_score,
                "feedback": score.feedback
            })
    
    return {
        "candidate_id": candidate.id,
        "overall_score": evaluation.overall_score,
        "dimensional_scores": {
            "understanding": evaluation.understanding_score,
            "reasoning": evaluation.reasoning_score,
            "communication": evaluation.communication_score,
            "logic": evaluation.logic_score
        },
        "strengths": evaluation.strengths,
        "weaknesses": evaluation.weaknesses,
        "recommendations": evaluation.recommendations,
        "hire_recommendation": evaluation.hire_recommendation,
        "question_scores": question_scores,
        "completed_at": app.aura_completed_at
    }


# ============= Profile =============

@router.get("/profile")
async def get_my_profile(
    current_user: CurrentUser = Depends(require_student),
    db: Session = Depends(get_db)
):
    """Get student profile"""
    user = db.query(User).filter(User.id == current_user.id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Count applications
    total_applications = db.query(Application).filter(Application.user_id == current_user.id).count()
    aura_completed = db.query(Application).filter(
        Application.user_id == current_user.id,
        Application.aura_completed_at.isnot(None)
    ).count()
    
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "github_url": user.github_url,
        "resume_url": user.resume_url,
        "stats": {
            "total_applications": total_applications,
            "aura_completed": aura_completed
        }
    }
