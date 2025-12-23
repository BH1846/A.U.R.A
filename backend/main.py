"""
Main FastAPI Application - AURA Skill Verification Agent
Integrates all phases into a cohesive API
"""
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
import os

from config import settings
from models import get_db, init_db
from models.database import Candidate, Repository, Question, QuestionScore, Evaluation, RoleProfile

# Import phase services
from core.phase0_profiles.role_profiles import RoleProfileManager
from core.phase1_github.github_service import github_service, CandidateInput
# Using simplified parser (no tree-sitter dependency)
from core.phase2_parsing.code_parser_simple import ProjectAnalyzer, CodeParser
# RAG and advanced features are optional
try:
    from core.phase3_rag.rag_service import rag_service
except ImportError:
    rag_service = None
from core.phase4_llm.llm_service import llm_service
from core.phase6_evaluation.evaluation_service import evaluation_service, OverallEvaluator
from core.phase7_reporting.report_service import report_generator, ReportData

# Import new multi-tenant routes
from routes.company import router as company_router
from routes.student import router as student_router

from loguru import logger

# Initialize FastAPI app
app = FastAPI(
    title="AURA - Automated Understanding & Role Assessment",
    description="AI-powered skill verification system for technical candidates",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register new routers for multi-tenant features
app.include_router(company_router)
app.include_router(student_router)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    logger.info("AURA system started successfully")


# ============ Health Check Endpoint ============

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring and load balancers"""
    try:
        # Quick database connection check
        db = next(get_db())
        db.execute("SELECT 1")
        db.close()
        
        return {
            "status": "healthy",
            "service": "AURA",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "AURA",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "disconnected",
            "error": str(e)
        }


@app.get("/api/storage-status")
async def get_storage_status():
    """Get current cloud storage configuration and status"""
    try:
        status = github_service.get_storage_status()
        status["timestamp"] = datetime.utcnow().isoformat()
        
        # Add helpful messages
        if status["cloud_storage_enabled"]:
            status["message"] = f"✅ Cloud storage is ACTIVE using {status['storage_provider']}"
        else:
            status["message"] = "ℹ️ Using local filesystem storage"
        
        return status
    except Exception as e:
        logger.error(f"Failed to get storage status: {e}")
        return {
            "error": str(e),
            "message": "Failed to retrieve storage status"
        }


# ============ Request/Response Models ============

class CandidateSubmitResponse(BaseModel):
    candidate_id: int
    message: str
    status: str


class QuestionResponse(BaseModel):
    question_id: int
    question_text: str
    question_type: str
    difficulty: str
    context: str


class AnswerSubmit(BaseModel):
    question_id: int
    answer_text: str
    time_taken: int  # seconds


class AnswersSubmit(BaseModel):
    answers: List[AnswerSubmit]


class EvaluationResponse(BaseModel):
    overall_score: float
    understanding_score: float
    reasoning_score: float
    communication_score: float
    logic_score: float
    hire_recommendation: str
    confidence: float
    report_pdf_path: Optional[str] = None


# ============ API Endpoints ============

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "AURA - Automated Understanding & Role Assessment API",
        "version": "1.0.0",
        "status": "active"
    }


@app.get("/api/roles")
async def get_roles():
    """Get available role types"""
    return {
        "roles": RoleProfileManager.get_all_roles(),
        "message": "Available role types for evaluation"
    }


@app.get("/api/candidates")
async def list_candidates(db: Session = Depends(get_db)):
    """List all candidates"""
    candidates = db.query(Candidate).all()
    
    result = []
    for c in candidates:
        # Determine status based on related data
        has_questions = db.query(Question).filter(Question.candidate_id == c.id).first() is not None
        has_evaluation = db.query(Evaluation).filter(Evaluation.candidate_id == c.id).first() is not None
        
        if has_evaluation:
            status = "completed"
        elif has_questions:
            status = "questions_ready"
        else:
            status = "processing"
        
        # Get repository info
        repo = db.query(Repository).filter(Repository.candidate_id == c.id).first()
        github_url = repo.repo_url if repo else c.github_url
        
        result.append({
            "id": c.id,
            "name": c.name,
            "email": c.email,
            "github_url": github_url,
            "role_type": c.role_type,
            "status": status,
            "created_at": str(c.created_at)
        })
    
    return {"items": result, "total": len(result)}


@app.delete("/api/candidate/{candidate_id}")
async def delete_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """Delete a candidate and all related data"""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Delete related data
    db.query(Question).filter(Question.candidate_id == candidate_id).delete()
    db.query(Repository).filter(Repository.candidate_id == candidate_id).delete()
    db.query(Evaluation).filter(Evaluation.candidate_id == candidate_id).delete()
    
    # Delete candidate
    db.delete(candidate)
    db.commit()
    
    return {"message": f"Candidate {candidate_id} deleted successfully"}


@app.get("/api/roles/{role_type}/skills")
async def get_role_skills(role_type: str):
    """Get skills for a specific role"""
    try:
        profile = RoleProfileManager.get_profile(role_type)
        return {
            "role_type": role_type,
            "description": profile.description,
            "required_skills": [s.skill_name for s in profile.required_skills],
            "optional_skills": [s.skill_name for s in profile.optional_skills]
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/candidate/submit", response_model=CandidateSubmitResponse)
async def submit_candidate(
    candidate_input: CandidateInput,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Phase 1: Submit candidate information and GitHub URL
    Starts repository analysis pipeline
    """
    try:
        logger.info(f"Processing candidate: {candidate_input.name}")
        
        # Validate GitHub URL
        if not github_service.validate_repository(candidate_input.github_url):
            raise HTTPException(status_code=400, detail="Invalid or inaccessible GitHub repository")
        
        # Check if candidate with this email already exists
        existing_candidate = db.query(Candidate).filter(Candidate.email == candidate_input.email).first()
        if existing_candidate:
            logger.info(f"Candidate with email {candidate_input.email} already exists (ID: {existing_candidate.id})")
            
            # Determine status based on related data
            has_questions = db.query(Question).filter(Question.candidate_id == existing_candidate.id).first() is not None
            has_evaluation = db.query(Evaluation).filter(Evaluation.candidate_id == existing_candidate.id).first() is not None
            
            if has_evaluation:
                status = "completed"
            elif has_questions:
                status = "questions_ready"
            else:
                status = "processing"
            
            # Return existing candidate instead of creating duplicate
            return CandidateSubmitResponse(
                candidate_id=existing_candidate.id,
                message="Candidate already exists. Using existing record.",
                status=status
            )
        
        # Create candidate in database
        candidate = Candidate(
            name=candidate_input.name,
            email=candidate_input.email,
            github_url=candidate_input.github_url,
            role_type=candidate_input.role_type
        )
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
        
        # Process repository in background
        background_tasks.add_task(process_repository, candidate.id, candidate_input.github_url, candidate_input.role_type)
        
        return CandidateSubmitResponse(
            candidate_id=candidate.id,
            message="Candidate submitted successfully. Repository analysis in progress.",
            status="processing"
        )
        
    except Exception as e:
        logger.error(f"Error submitting candidate: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


async def process_repository(candidate_id: int, github_url: str, role_type: str):
    """
    Background task to process repository through all phases
    """
    db = next(get_db())
    
    try:
        logger.info(f"Starting repository processing for candidate {candidate_id}")
        
        # Phase 1: Clone repository
        repo_info = github_service.get_repository_info(github_url)
        local_path = github_service.clone_repository(github_url, candidate_id)
        
        # Save repository info
        repository = Repository(
            candidate_id=candidate_id,
            repo_name=repo_info.repo_name,
            repo_url=repo_info.repo_url,
            local_path=local_path,
            languages=repo_info.languages,
            stars=repo_info.stars,
            forks=repo_info.forks,
            last_commit=datetime.fromisoformat(repo_info.last_commit) if repo_info.last_commit else None
        )
        db.add(repository)
        db.commit()
        
        # Phase 2: Parse and analyze project
        analyzer = ProjectAnalyzer(local_path)
        project_structure = analyzer.analyze()
        parser = CodeParser()
        
        # Update repository with analysis
        tech_stack_list = list(project_structure.get('languages', {}).keys())
        repository.tech_stack = tech_stack_list  # Store as list, not dict
        repository.file_structure = {"total_files": project_structure.get('total_files', 0)}
        
        # Parse key files (simplified)
        file_analyses = project_structure.get('files', [])[:10]
        
        # Phase 3: RAG - Skip if service not available
        if rag_service is not None:
            rag_service.process_repository(candidate_id, local_path, file_analyses)
        
        # Phase 4: Generate project summary and questions
        readme_content = ""
        readme_paths = [os.path.join(local_path, 'README.md'), os.path.join(local_path, 'readme.md')]
        for rp in readme_paths:
            if os.path.exists(rp):
                with open(rp, 'r', encoding='utf-8', errors='ignore') as f:
                    readme_content = f.read()
                break
        
        # Simple project summary when no LLM available
        tech_stack = list(project_structure.get('languages', {}).keys())
        project_summary_text = f"Repository: {github_url}\nLanguages: {', '.join(tech_stack)}\nFiles: {project_structure.get('total_files', 0)}"
        
        # Update repository with summary
        repository.project_summary = project_summary_text
        repository.purpose = readme_content[:500] if readme_content else "No README found"
        repository.workflow_summary = "Analysis complete"
        db.commit()
        
        # Get code context for questions (skip RAG if not available)
        code_context = ""
        if rag_service is not None:
            code_context = rag_service.retrieve_context(candidate_id, "main functionality features implementation")
        
        # Generate interview questions using LLM
        required_skills = RoleProfileManager.get_required_skills(role_type)
        
        # Create a simple ProjectSummary-like dict for compatibility
        from core.phase4_llm.llm_service import ProjectSummary
        simple_summary = ProjectSummary(
            title=f"{role_type} Project Analysis",
            description=project_summary_text,
            purpose=repository.purpose or "Code analysis",
            tech_stack_summary=", ".join(tech_stack),
            key_features=["Repository analysis", "Code structure"],
            workflow_description="Standard development workflow",
            complexity_level="intermediate"
        )
        
        # Generate questions
        questions_list = llm_service.generate_interview_questions(
            project_summary=simple_summary,
            role_type=role_type,
            code_context=[{"metadata": {"file_path": f.get("file", "")}, "content": str(f)} for f in file_analyses[:3]],
            required_skills=required_skills
        )
        
        # Save questions to database
        for q in questions_list:
            question = Question(
                candidate_id=candidate_id,
                question_text=q.question_text,
                question_type=q.question_type,
                difficulty=q.difficulty,
                context=q.context,
                expected_keywords=q.expected_keywords
            )
            db.add(question)
        
        db.commit()
        logger.success(f"Repository processing complete for candidate {candidate_id}")
        
    except Exception as e:
        logger.error(f"Error processing repository for candidate {candidate_id}: {e}")
        db.rollback()
    finally:
        db.close()


@app.get("/api/candidate/{candidate_id}/status")
async def get_candidate_status(candidate_id: int, db: Session = Depends(get_db)):
    """Get processing status of candidate"""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    questions = db.query(Question).filter(Question.candidate_id == candidate_id).all()
    
    if questions:
        answered = sum(1 for q in questions if q.answer_text)
        return {
            "status": "completed" if answered == len(questions) else "ready",
            "total_questions": len(questions),
            "answered_questions": answered
        }
    else:
        return {"status": "processing", "message": "Analysis in progress"}


@app.get("/api/candidate/{candidate_id}/questions", response_model=List[QuestionResponse])
async def get_questions(candidate_id: int, db: Session = Depends(get_db)):
    """
    Phase 5: Get interview questions for candidate
    """
    questions = db.query(Question).filter(Question.candidate_id == candidate_id).all()
    
    if not questions:
        raise HTTPException(status_code=404, detail="Questions not yet generated or candidate not found")
    
    return [
        QuestionResponse(
            question_id=q.id,
            question_text=q.question_text,
            question_type=q.question_type,
            difficulty=q.difficulty,
            context=q.context
        )
        for q in questions
    ]


@app.post("/api/candidate/{candidate_id}/answers")
async def submit_answers(
    candidate_id: int,
    answers_data: AnswersSubmit,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Phase 5: Submit candidate answers
    Triggers evaluation pipeline
    """
    try:
        logger.info(f"Received {len(answers_data.answers)} answers for candidate {candidate_id}")
        
        # Save answers
        for answer in answers_data.answers:
            question = db.query(Question).filter(Question.id == answer.question_id).first()
            if question and question.candidate_id == candidate_id:
                question.answer_text = answer.answer_text
                question.time_taken = answer.time_taken
                question.answered_at = datetime.utcnow()
        
        db.commit()
        
        # Start evaluation in background
        background_tasks.add_task(evaluate_candidate, candidate_id)
        
        return {"message": "Answers submitted successfully. Evaluation in progress."}
        
    except Exception as e:
        logger.error(f"Error submitting answers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def evaluate_candidate(candidate_id: int):
    """
    Phase 6 & 7: Evaluate answers and generate report
    """
    db = next(get_db())
    
    try:
        logger.info(f"Starting evaluation for candidate {candidate_id}")
        
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        repository = db.query(Repository).filter(Repository.candidate_id == candidate_id).first()
        questions = db.query(Question).filter(Question.candidate_id == candidate_id).all()
        
        # Delete existing question scores to avoid UNIQUE constraint errors
        question_ids = [q.id for q in questions]
        db.query(QuestionScore).filter(QuestionScore.question_id.in_(question_ids)).delete(synchronize_session=False)
        db.commit()
        logger.info(f"Deleted existing scores for {len(question_ids)} questions")
        
        question_evaluations = []
        all_strengths = []
        all_weaknesses = []
        fraud_signals = []
        
        # Evaluate each question
        for question in questions:
            if not question.answer_text:
                continue
            
            # Get context (skip if RAG not available)
            code_context = ""
            if rag_service is not None:
                context_items = rag_service.retrieve_context(candidate_id, question.question_text, n_results=3)
                code_context = "\n\n".join([item['content'] for item in context_items])
            else:
                # Use repository summary as fallback
                code_context = repository.project_summary or "No context available"
            
            # Evaluate answer
            scores = evaluation_service.evaluate_answer(
                question=question.question_text,
                question_type=question.question_type,
                expected_keywords=question.expected_keywords,
                candidate_answer=question.answer_text,
                code_context=code_context,
                project_summary=repository.project_summary
            )
            
            # Generate feedback
            feedback, strengths, weaknesses = evaluation_service.generate_feedback(
                question=question.question_text,
                answer=question.answer_text,
                scores=scores
            )
            
            # Detect fraud
            is_fraud, fraud_reason = evaluation_service.detect_fraud(
                answer=question.answer_text,
                code_context=code_context,
                question=question.question_text
            )
            
            if is_fraud:
                fraud_signals.append(f"Q{question.id}: {fraud_reason}")
            
            # Calculate weighted score
            weighted_score = evaluation_service.calculate_weighted_score(scores)
            
            # Save scores
            question_score = QuestionScore(
                question_id=question.id,
                concept_understanding=scores.concept_understanding,
                technical_depth=scores.technical_depth,
                accuracy=scores.accuracy,
                communication=scores.communication,
                relevance=scores.relevance,
                weighted_score=weighted_score,
                feedback=feedback,
                strengths=strengths,
                weaknesses=weaknesses,
                fraud_flag=is_fraud,
                fraud_reason=fraud_reason if is_fraud else None
            )
            db.add(question_score)
            
            all_strengths.extend(strengths)
            all_weaknesses.extend(weaknesses)
            
            question_evaluations.append({
                'question': question.question_text,
                'type': question.question_type,
                'difficulty': question.difficulty,
                'answer': question.answer_text,
                'score': weighted_score,
                'feedback': feedback
            })
        
        db.commit()
        
        # Calculate overall scores
        question_eval_objects = [db.query(QuestionScore).filter(QuestionScore.question_id == q.id).first() for q in questions]
        question_eval_objects = [qe for qe in question_eval_objects if qe]
        
        from core.phase6_evaluation.evaluation_service import QuestionEvaluation, DimensionalScore
        eval_list = [
            QuestionEvaluation(
                question_id=qe.question_id,
                scores=DimensionalScore(
                    concept_understanding=qe.concept_understanding,
                    technical_depth=qe.technical_depth,
                    accuracy=qe.accuracy,
                    communication=qe.communication,
                    relevance=qe.relevance
                ),
                weighted_score=qe.weighted_score,
                feedback=qe.feedback,
                strengths=qe.strengths,
                weaknesses=qe.weaknesses,
                fraud_flag=qe.fraud_flag
            )
            for qe in question_eval_objects
        ]
        
        overall_scores = OverallEvaluator.calculate_overall_score(eval_list)
        hire_rec, confidence = OverallEvaluator.generate_recommendation(overall_scores['overall_score'])
        
        # Create evaluation record
        evaluation = Evaluation(
            candidate_id=candidate_id,
            overall_score=overall_scores['overall_score'],
            understanding_score=overall_scores['understanding_score'],
            reasoning_score=overall_scores['reasoning_score'],
            communication_score=overall_scores['communication_score'],
            logic_score=overall_scores['logic_score'],
            strengths=list(set(all_strengths)),
            weaknesses=list(set(all_weaknesses)),
            recommendations=f"Based on the evaluation, this candidate demonstrates {hire_rec.replace('_', ' ')} fit for the {candidate.role_type} role.",
            hire_recommendation=hire_rec,
            confidence=confidence,
            fraud_detected=len(fraud_signals) > 0,
            fraud_signals=fraud_signals if fraud_signals else None
        )
        db.add(evaluation)
        db.commit()
        
        # Phase 7: Generate report
        report_data = ReportData(
            candidate_name=candidate.name,
            candidate_email=candidate.email,
            role_type=candidate.role_type,
            github_url=candidate.github_url,
            project_name=repository.repo_name,
            project_description=repository.project_summary or "N/A",
            tech_stack=repository.tech_stack or [],
            frameworks=[],  # Simplified - no framework detection in minimal version
            overall_score=overall_scores['overall_score'],
            understanding_score=overall_scores['understanding_score'],
            reasoning_score=overall_scores['reasoning_score'],
            communication_score=overall_scores['communication_score'],
            logic_score=overall_scores['logic_score'],
            qa_evaluations=question_evaluations,
            strengths=evaluation.strengths,
            weaknesses=evaluation.weaknesses,
            recommendations=evaluation.recommendations,
            hire_recommendation=hire_rec,
            confidence=confidence,
            fraud_detected=evaluation.fraud_detected,
            fraud_signals=fraud_signals,
            evaluation_date=datetime.now().strftime("%Y-%m-%d %H:%M"),
            total_questions=len(questions)
        )
        
        report_paths = report_generator.generate_reports(report_data, candidate_id)
        evaluation.report_path = report_paths['pdf']
        evaluation.report_generated_at = datetime.utcnow()
        db.commit()
        
        logger.success(f"Evaluation complete for candidate {candidate_id}")
        
    except Exception as e:
        logger.error(f"Error evaluating candidate {candidate_id}: {e}")
        db.rollback()
    finally:
        db.close()


@app.get("/api/candidate/{candidate_id}/report")
async def get_report(candidate_id: int, db: Session = Depends(get_db)):
    """
    Phase 7: Get evaluation report with complete data
    """
    # Get evaluation
    evaluation = db.query(Evaluation).filter(Evaluation.candidate_id == candidate_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not yet complete")
    
    # Get candidate
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Get repository analysis
    repo_analysis = db.query(Repository).filter(Repository.candidate_id == candidate_id).first()
    
    # Get questions and scores
    questions = db.query(Question).filter(Question.candidate_id == candidate_id).all()
    scores = db.query(QuestionScore).join(Question).filter(Question.candidate_id == candidate_id).all()
    
    # Build repository data
    repo_data = {
        "name": repo_analysis.repo_name if repo_analysis else "Unknown",
        "url": candidate.github_url,
        "tech_stack": repo_analysis.tech_stack if repo_analysis else [],
        "languages": repo_analysis.languages if repo_analysis else []
    }
    
    # Build response
    return {
        "candidate": {
            "id": candidate.id,
            "name": candidate.name,
            "email": candidate.email,
            "role_type": candidate.role_type,
            "github_url": candidate.github_url
        },
        "repository": repo_data,
        "questions": [
            {
                "question_id": q.id,
                "question_text": q.question_text,
                "question_type": q.question_type,
                "difficulty": q.difficulty,
                "context": q.context
            }
            for q in questions
        ],
        "answers": [
            {
                "id": q.id,
                "question_id": q.id,
                "answer_text": q.answer_text or "",
                "time_taken": q.time_taken or 0
            }
            for q in questions if q.answer_text
        ],
        "question_scores": [
            {
                "id": s.id,
                "question_id": s.question_id,
                "concept_understanding": s.concept_understanding,
                "technical_depth": s.technical_depth,
                "accuracy": s.accuracy,
                "communication": s.communication,
                "relevance": s.relevance,
                "weighted_score": s.weighted_score,
                "feedback": s.feedback,
                "strengths": s.strengths,
                "weaknesses": s.weaknesses,
                "fraud_flag": s.fraud_flag or False,
                "fraud_reason": s.fraud_reason
            }
            for s in scores
        ],
        "final_score": {
            "overall_score": evaluation.overall_score,
            "understanding_score": evaluation.understanding_score,
            "reasoning_score": evaluation.reasoning_score,
            "communication_score": evaluation.communication_score,
            "logic_score": evaluation.logic_score,
            "hire_recommendation": evaluation.hire_recommendation,
            "confidence": evaluation.confidence
        },
        "report_pdf_path": evaluation.report_path
    }


@app.get("/api/candidate/{candidate_id}/report/download")
async def download_report(candidate_id: int, db: Session = Depends(get_db)):
    """Download PDF report"""
    evaluation = db.query(Evaluation).filter(Evaluation.candidate_id == candidate_id).first()
    
    if not evaluation or not evaluation.report_path:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if not os.path.exists(evaluation.report_path):
        raise HTTPException(status_code=404, detail="Report file not found")
    
    return FileResponse(
        evaluation.report_path,
        media_type='application/pdf',
        filename=os.path.basename(evaluation.report_path),
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "*"
        }
    )


# ============ Recruiter Dashboard Endpoints ============

@app.get("/api/recruiter/candidates")
async def list_candidates(db: Session = Depends(get_db)):
    """
    Phase 8: List all candidates for recruiter dashboard
    """
    candidates = db.query(Candidate).all()
    
    results = []
    for candidate in candidates:
        evaluation = db.query(Evaluation).filter(Evaluation.candidate_id == candidate.id).first()
        
        results.append({
            'id': candidate.id,
            'name': candidate.name,
            'email': candidate.email,
            'role_type': candidate.role_type,
            'github_url': candidate.github_url,
            'created_at': candidate.created_at.isoformat(),
            'overall_score': evaluation.overall_score if evaluation else None,
            'hire_recommendation': evaluation.hire_recommendation if evaluation else None,
            'status': 'evaluated' if evaluation else 'pending'
        })
    
    return {'candidates': results, 'total': len(results)}


@app.get("/api/recruiter/candidate/{candidate_id}")
async def get_candidate_details(candidate_id: int, db: Session = Depends(get_db)):
    """Get detailed candidate information"""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    repository = db.query(Repository).filter(Repository.candidate_id == candidate_id).first()
    evaluation = db.query(Evaluation).filter(Evaluation.candidate_id == candidate_id).first()
    questions = db.query(Question).filter(Question.candidate_id == candidate_id).all()
    
    return {
        'candidate': {
            'id': candidate.id,
            'name': candidate.name,
            'email': candidate.email,
            'role_type': candidate.role_type,
            'github_url': candidate.github_url
        },
        'repository': {
            'name': repository.repo_name if repository else None,
            'tech_stack': repository.tech_stack if repository else [],
            'project_summary': repository.project_summary if repository else None
        },
        'evaluation': {
            'overall_score': evaluation.overall_score if evaluation else None,
            'scores': {
                'understanding': evaluation.understanding_score if evaluation else None,
                'reasoning': evaluation.reasoning_score if evaluation else None,
                'communication': evaluation.communication_score if evaluation else None,
                'logic': evaluation.logic_score if evaluation else None
            },
            'strengths': evaluation.strengths if evaluation else [],
            'weaknesses': evaluation.weaknesses if evaluation else [],
            'hire_recommendation': evaluation.hire_recommendation if evaluation else None,
            'fraud_detected': evaluation.fraud_detected if evaluation else False
        } if evaluation else None,
        'questions_count': len(questions)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
