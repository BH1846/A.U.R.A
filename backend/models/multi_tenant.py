"""
Multi-tenancy models for I-Intern integration
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from models.database import Base


class UserRole(str, enum.Enum):
    """User roles in the system"""
    STUDENT = "student"
    RECRUITER = "recruiter"
    ADMIN = "admin"


class ApplicationStatus(str, enum.Enum):
    """Application status"""
    PENDING = "pending"
    AURA_INVITED = "aura_invited"
    AURA_IN_PROGRESS = "aura_in_progress"
    AURA_COMPLETED = "aura_completed"
    SHORTLISTED = "shortlisted"
    INTERVIEWED = "interviewed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class User(Base):
    """User model - integrates with I-Intern auth"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # I-Intern user ID (from JWT token)
    i_intern_user_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # User info
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.STUDENT)
    
    # Student-specific
    github_url = Column(String(500))
    resume_url = Column(String(500))
    
    # Company relationship (for recruiters)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    company = relationship("Company", back_populates="users")
    applications = relationship("Application", back_populates="user", foreign_keys="Application.user_id")
    
    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


class Company(Base):
    """Company/Organization model"""
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # I-Intern company ID
    i_intern_company_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # Company info
    name = Column(String(255), nullable=False)
    description = Column(Text)
    website = Column(String(500))
    logo_url = Column(String(500))
    
    # Settings
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="company")
    internships = relationship("Internship", back_populates="company")
    
    def __repr__(self):
        return f"<Company {self.name}>"


class Internship(Base):
    """Internship posting"""
    __tablename__ = "internships"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # I-Intern internship ID
    i_intern_internship_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # Internship details
    title = Column(String(255), nullable=False)
    description = Column(Text)
    role_type = Column(String(50), nullable=False)  # Frontend, Backend, ML, DevOps
    location = Column(String(255))
    duration_months = Column(Integer)
    
    # AURA settings
    aura_enabled = Column(Boolean, default=True)
    aura_required = Column(Boolean, default=False)  # Required vs optional
    aura_passing_score = Column(Integer, default=60)  # Minimum score for auto-shortlist
    
    # Status
    is_active = Column(Boolean, default=True)
    posted_at = Column(DateTime, default=datetime.utcnow)
    deadline = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="internships")
    applications = relationship("Application", back_populates="internship")
    
    def __repr__(self):
        return f"<Internship {self.title} at {self.company.name if self.company else 'Unknown'}>"


class Application(Base):
    """Job application with AURA assessment"""
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    internship_id = Column(Integer, ForeignKey("internships.id"), nullable=False)
    
    # I-Intern application ID
    i_intern_application_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # Application status
    status = Column(SQLEnum(ApplicationStatus), nullable=False, default=ApplicationStatus.PENDING)
    
    # AURA assessment
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=True, unique=True)
    aura_invited_at = Column(DateTime)
    aura_started_at = Column(DateTime)
    aura_completed_at = Column(DateTime)
    
    # Metadata
    applied_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="applications", foreign_keys=[user_id])
    internship = relationship("Internship", back_populates="applications")
    candidate = relationship("Candidate", back_populates="application", uselist=False)
    
    def __repr__(self):
        return f"<Application {self.id}: {self.status}>"
