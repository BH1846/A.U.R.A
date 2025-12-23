"""
Company/Recruiter portal API routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime

from models import get_db
from models.database import Candidate, Evaluation, Question, QuestionScore
from models.multi_tenant import Company, Internship, Application, ApplicationStatus, User
from core.auth import require_recruiter, CurrentUser

router = APIRouter(prefix="/api/company", tags=["company"])


# ============= Internships Management =============

@router.get("/internships")
async def get_company_internships(
    current_user: CurrentUser = Depends(require_recruiter),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """Get all internships for recruiter's company"""
    if not current_user.company_id:
        raise HTTPException(status_code=400, detail="User not associated with a company")
    
    internships = db.query(Internship).filter(
        Internship.company_id == current_user.company_id
    ).offset(skip).limit(limit).all()
    
    total = db.query(func.count(Internship.id)).filter(
        Internship.company_id == current_user.company_id
    ).scalar()
    
    return {
        "items": [{
            "id": i.id,
            "title": i.title,
            "role_type": i.role_type,
            "location": i.location,
            "duration_months": i.duration_months,
            "aura_enabled": i.aura_enabled,
            "is_active": i.is_active,
            "posted_at": i.posted_at,
            "deadline": i.deadline,
            "application_count": db.query(func.count(Application.id)).filter(
                Application.internship_id == i.id
            ).scalar()
        } for i in internships],
        "total": total
    }


@router.get("/internships/{internship_id}")
async def get_internship_details(
    internship_id: int,
    current_user: CurrentUser = Depends(require_recruiter),
    db: Session = Depends(get_db)
):
    """Get detailed internship information"""
    internship = db.query(Internship).filter(
        Internship.id == internship_id,
        Internship.company_id == current_user.company_id
    ).first()
    
    if not internship:
        raise HTTPException(status_code=404, detail="Internship not found")
    
    return {
        "id": internship.id,
        "title": internship.title,
        "description": internship.description,
        "role_type": internship.role_type,
        "location": internship.location,
        "duration_months": internship.duration_months,
        "aura_enabled": internship.aura_enabled,
        "aura_required": internship.aura_required,
        "aura_passing_score": internship.aura_passing_score,
        "is_active": internship.is_active,
        "posted_at": internship.posted_at,
        "deadline": internship.deadline
    }


# ============= Applications Management =============

@router.get("/applications")
async def get_applications(
    current_user: CurrentUser = Depends(require_recruiter),
    db: Session = Depends(get_db),
    internship_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """Get all applications for company's internships"""
    if not current_user.company_id:
        raise HTTPException(status_code=400, detail="User not associated with a company")
    
    # Base query - join with internship to filter by company
    query = db.query(Application).join(Internship).filter(
        Internship.company_id == current_user.company_id
    )
    
    # Apply filters
    if internship_id:
        query = query.filter(Application.internship_id == internship_id)
    if status:
        query = query.filter(Application.status == status)
    
    # Get results
    applications = query.offset(skip).limit(limit).all()
    total = query.count()
    
    # Format response with user and AURA data
    items = []
    for app in applications:
        user = db.query(User).filter(User.id == app.user_id).first()
        candidate = None
        aura_score = None
        
        if app.candidate_id:
            candidate = db.query(Candidate).filter(Candidate.id == app.candidate_id).first()
            if candidate:
                eval_data = db.query(Evaluation).filter(Evaluation.candidate_id == candidate.id).first()
                if eval_data:
                    aura_score = eval_data.overall_score
        
        items.append({
            "id": app.id,
            "internship_id": app.internship_id,
            "internship_title": app.internship.title if app.internship else None,
            "user_id": app.user_id,
            "user_name": user.name if user else "Unknown",
            "user_email": user.email if user else "Unknown",
            "github_url": user.github_url if user else None,
            "status": app.status,
            "aura_score": aura_score,
            "aura_completed": app.aura_completed_at is not None,
            "applied_at": app.applied_at
        })
    
    return {"items": items, "total": total}


@router.get("/applications/{application_id}")
async def get_application_detail(
    application_id: int,
    current_user: CurrentUser = Depends(require_recruiter),
    db: Session = Depends(get_db)
):
    """Get detailed application with AURA assessment"""
    app = db.query(Application).join(Internship).filter(
        Application.id == application_id,
        Internship.company_id == current_user.company_id
    ).first()
    
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    user = db.query(User).filter(User.id == app.user_id).first()
    
    result = {
        "id": app.id,
        "internship": {
            "id": app.internship.id,
            "title": app.internship.title,
            "role_type": app.internship.role_type
        },
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "github_url": user.github_url
        },
        "status": app.status,
        "applied_at": app.applied_at,
        "aura_data": None
    }
    
    # Add AURA assessment if available
    if app.candidate_id:
        candidate = db.query(Candidate).filter(Candidate.id == app.candidate_id).first()
        if candidate:
            evaluation = db.query(Evaluation).filter(Evaluation.candidate_id == candidate.id).first()
            if evaluation:
                result["aura_data"] = {
                    "candidate_id": candidate.id,
                    "overall_score": evaluation.overall_score,
                    "understanding_score": evaluation.understanding_score,
                    "reasoning_score": evaluation.reasoning_score,
                    "communication_score": evaluation.communication_score,
                    "logic_score": evaluation.logic_score,
                    "strengths": evaluation.strengths,
                    "weaknesses": evaluation.weaknesses,
                    "hire_recommendation": evaluation.hire_recommendation,
                    "completed_at": app.aura_completed_at
                }
    
    return result


# ============= Analytics & Rankings =============

@router.get("/analytics/overview")
async def get_analytics_overview(
    current_user: CurrentUser = Depends(require_recruiter),
    db: Session = Depends(get_db),
    internship_id: Optional[int] = None
):
    """Get analytics overview for company internships"""
    if not current_user.company_id:
        raise HTTPException(status_code=400, detail="User not associated with a company")
    
    # Base query
    query = db.query(Application).join(Internship).filter(
        Internship.company_id == current_user.company_id
    )
    
    if internship_id:
        query = query.filter(Application.internship_id == internship_id)
    
    # Total applications
    total_applications = query.count()
    
    # Status breakdown
    status_counts = {}
    for status in ApplicationStatus:
        count = query.filter(Application.status == status.value).count()
        status_counts[status.value] = count
    
    # AURA statistics
    aura_completed = query.filter(Application.aura_completed_at.isnot(None)).count()
    
    # Average AURA score
    avg_score_query = db.query(func.avg(Evaluation.overall_score)).join(
        Candidate, Candidate.id == Evaluation.candidate_id
    ).join(
        Application, Application.candidate_id == Candidate.id
    ).join(
        Internship, Internship.id == Application.internship_id
    ).filter(
        Internship.company_id == current_user.company_id
    )
    
    if internship_id:
        avg_score_query = avg_score_query.filter(Application.internship_id == internship_id)
    
    avg_score = avg_score_query.scalar() or 0
    
    return {
        "total_applications": total_applications,
        "status_breakdown": status_counts,
        "aura_completed": aura_completed,
        "aura_average_score": round(avg_score, 2)
    }


@router.get("/rankings")
async def get_candidate_rankings(
    current_user: CurrentUser = Depends(require_recruiter),
    db: Session = Depends(get_db),
    internship_id: Optional[int] = None,
    limit: int = Query(20, ge=1, le=100)
):
    """Get ranked list of candidates by AURA score"""
    if not current_user.company_id:
        raise HTTPException(status_code=400, detail="User not associated with a company")
    
    # Query applications with evaluations
    query = db.query(
        Application,
        User,
        Candidate,
        Evaluation
    ).join(
        Internship, Internship.id == Application.internship_id
    ).join(
        User, User.id == Application.user_id
    ).join(
        Candidate, Candidate.id == Application.candidate_id
    ).join(
        Evaluation, Evaluation.candidate_id == Candidate.id
    ).filter(
        Internship.company_id == current_user.company_id,
        Application.aura_completed_at.isnot(None)
    )
    
    if internship_id:
        query = query.filter(Application.internship_id == internship_id)
    
    # Order by score descending
    query = query.order_by(desc(Evaluation.overall_score))
    
    results = query.limit(limit).all()
    
    rankings = []
    for rank, (app, user, candidate, evaluation) in enumerate(results, 1):
        rankings.append({
            "rank": rank,
            "application_id": app.id,
            "user_name": user.name,
            "user_email": user.email,
            "github_url": user.github_url,
            "internship_id": app.internship_id,
            "internship_title": app.internship.title,
            "overall_score": evaluation.overall_score,
            "understanding_score": evaluation.understanding_score,
            "reasoning_score": evaluation.reasoning_score,
            "communication_score": evaluation.communication_score,
            "logic_score": evaluation.logic_score,
            "hire_recommendation": evaluation.hire_recommendation,
            "completed_at": app.aura_completed_at
        })
    
    return {"rankings": rankings, "total": len(rankings)}
