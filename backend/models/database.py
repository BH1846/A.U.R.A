"""
Database models for AURA system
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Candidate(Base):
    """Candidate model"""
    __tablename__ = "candidates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    github_url = Column(String(500), nullable=False)
    role_type = Column(String(50), nullable=False)  # Frontend, Backend, ML, DevOps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    repository = relationship("Repository", back_populates="candidate", uselist=False)
    questions = relationship("Question", back_populates="candidate")
    evaluation = relationship("Evaluation", back_populates="candidate", uselist=False)
    
    def __repr__(self):
        return f"<Candidate {self.name} ({self.email})>"


class Repository(Base):
    """Repository model"""
    __tablename__ = "repositories"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), unique=True)
    
    repo_name = Column(String(255), nullable=False)
    repo_url = Column(String(500), nullable=False)
    local_path = Column(String(500))
    
    # Extracted information
    languages = Column(JSON)  # List of languages
    tech_stack = Column(JSON)  # List of technologies
    file_structure = Column(JSON)  # Directory tree
    main_files = Column(JSON)  # Entry points
    
    # Analysis results
    project_summary = Column(Text)
    purpose = Column(Text)
    workflow_summary = Column(Text)
    
    # Metadata
    stars = Column(Integer, default=0)
    forks = Column(Integer, default=0)
    last_commit = Column(DateTime)
    
    parsed_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="repository")
    modules = relationship("CodeModule", back_populates="repository")
    
    def __repr__(self):
        return f"<Repository {self.repo_name}>"


class CodeModule(Base):
    """Code module/component extracted from repository"""
    __tablename__ = "code_modules"
    
    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"))
    
    file_path = Column(String(500), nullable=False)
    module_type = Column(String(50))  # api, model, util, component, etc.
    name = Column(String(255))
    
    # Extracted elements
    functions = Column(JSON)  # List of function names and signatures
    classes = Column(JSON)  # List of class names and methods
    imports = Column(JSON)  # List of imports
    
    # Content
    code_content = Column(Text)
    documentation = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    repository = relationship("Repository", back_populates="modules")
    
    def __repr__(self):
        return f"<CodeModule {self.name} in {self.file_path}>"


class Question(Base):
    """Interview question"""
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    
    question_text = Column(Text, nullable=False)
    question_type = Column(String(20))  # why, what, how, where
    difficulty = Column(String(20))  # easy, medium, hard
    context = Column(Text)  # Related code/context
    expected_keywords = Column(JSON)  # Keywords that should appear in answer
    
    # Answer
    answer_text = Column(Text)
    answered_at = Column(DateTime)
    time_taken = Column(Integer)  # seconds
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="questions")
    score = relationship("QuestionScore", back_populates="question", uselist=False)
    
    def __repr__(self):
        return f"<Question {self.id}: {self.question_type}>"


class QuestionScore(Base):
    """Score for individual question"""
    __tablename__ = "question_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), unique=True)
    
    # Dimensional scores (0-10)
    concept_understanding = Column(Float, default=0.0)
    technical_depth = Column(Float, default=0.0)
    accuracy = Column(Float, default=0.0)
    communication = Column(Float, default=0.0)
    relevance = Column(Float, default=0.0)
    
    # Weighted score
    weighted_score = Column(Float, default=0.0)
    
    # Feedback
    feedback = Column(Text)
    strengths = Column(JSON)
    weaknesses = Column(JSON)
    
    # Fraud detection
    fraud_flag = Column(Boolean, default=False)
    fraud_reason = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    question = relationship("Question", back_populates="score")
    
    def __repr__(self):
        return f"<QuestionScore {self.question_id}: {self.weighted_score:.2f}>"


class Evaluation(Base):
    """Overall evaluation for candidate"""
    __tablename__ = "evaluations"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), unique=True)
    
    # Overall scores
    overall_score = Column(Float, default=0.0)  # 0-100
    understanding_score = Column(Float, default=0.0)
    reasoning_score = Column(Float, default=0.0)
    communication_score = Column(Float, default=0.0)
    logic_score = Column(Float, default=0.0)
    
    # Skill breakdown
    skill_scores = Column(JSON)  # {skill_name: score}
    
    # Analysis
    strengths = Column(JSON)  # List of strength areas
    weaknesses = Column(JSON)  # List of weakness areas
    recommendations = Column(Text)
    
    # Decision
    hire_recommendation = Column(String(20))  # strong_yes, yes, maybe, no, strong_no
    confidence = Column(Float)  # 0-1
    
    # Fraud detection
    fraud_detected = Column(Boolean, default=False)
    fraud_signals = Column(JSON)
    
    # Report
    report_path = Column(String(500))
    report_generated_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="evaluation")
    
    def __repr__(self):
        return f"<Evaluation {self.candidate_id}: {self.overall_score:.2f}>"


class RoleProfile(Base):
    """Role-specific skill profile"""
    __tablename__ = "role_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    role_type = Column(String(50), unique=True, nullable=False)  # Frontend, Backend, ML, DevOps
    
    required_skills = Column(JSON)  # List of required skills
    optional_skills = Column(JSON)  # List of optional/bonus skills
    skill_weights = Column(JSON)  # {skill_name: weight}
    
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<RoleProfile {self.role_type}>"
