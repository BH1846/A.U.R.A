"""
Phase 0: Role Skill Profile Management
Define and manage skill profiles for different internship roles
"""
from typing import Dict, List
from pydantic import BaseModel


class SkillProfile(BaseModel):
    """Skill profile model"""
    skill_name: str
    weight: float  # 0-1
    required: bool
    category: str  # technical, soft, tool


class RoleProfileSchema(BaseModel):
    """Role profile schema"""
    role_type: str
    description: str
    required_skills: List[SkillProfile]
    optional_skills: List[SkillProfile]
    

# Predefined Role Profiles
ROLE_PROFILES: Dict[str, RoleProfileSchema] = {
    "Frontend": RoleProfileSchema(
        role_type="Frontend",
        description="Frontend Development Internship - Focus on UI/UX and client-side development",
        required_skills=[
            SkillProfile(skill_name="React", weight=0.25, required=True, category="technical"),
            SkillProfile(skill_name="JavaScript/TypeScript", weight=0.20, required=True, category="technical"),
            SkillProfile(skill_name="HTML/CSS", weight=0.15, required=True, category="technical"),
            SkillProfile(skill_name="State Management", weight=0.15, required=True, category="technical"),
            SkillProfile(skill_name="API Integration", weight=0.15, required=True, category="technical"),
            SkillProfile(skill_name="Responsive Design", weight=0.10, required=True, category="technical"),
        ],
        optional_skills=[
            SkillProfile(skill_name="Next.js", weight=0.08, required=False, category="technical"),
            SkillProfile(skill_name="Testing (Jest/Vitest)", weight=0.07, required=False, category="technical"),
            SkillProfile(skill_name="UI Frameworks (Tailwind/MUI)", weight=0.06, required=False, category="tool"),
            SkillProfile(skill_name="Performance Optimization", weight=0.05, required=False, category="technical"),
        ]
    ),
    
    "Backend": RoleProfileSchema(
        role_type="Backend",
        description="Backend Development Internship - Focus on server-side logic and APIs",
        required_skills=[
            SkillProfile(skill_name="FastAPI/Flask/Django", weight=0.20, required=True, category="technical"),
            SkillProfile(skill_name="RESTful API Design", weight=0.18, required=True, category="technical"),
            SkillProfile(skill_name="Database (SQL/NoSQL)", weight=0.18, required=True, category="technical"),
            SkillProfile(skill_name="Authentication & Authorization", weight=0.15, required=True, category="technical"),
            SkillProfile(skill_name="Python/Node.js", weight=0.15, required=True, category="technical"),
            SkillProfile(skill_name="Error Handling", weight=0.10, required=True, category="technical"),
        ],
        optional_skills=[
            SkillProfile(skill_name="Microservices", weight=0.08, required=False, category="technical"),
            SkillProfile(skill_name="Caching (Redis)", weight=0.07, required=False, category="technical"),
            SkillProfile(skill_name="Message Queues", weight=0.06, required=False, category="technical"),
            SkillProfile(skill_name="API Documentation", weight=0.05, required=False, category="technical"),
        ]
    ),
    
    "ML": RoleProfileSchema(
        role_type="ML",
        description="Machine Learning Internship - Focus on ML models and data science",
        required_skills=[
            SkillProfile(skill_name="Model Training", weight=0.25, required=True, category="technical"),
            SkillProfile(skill_name="Model Evaluation", weight=0.20, required=True, category="technical"),
            SkillProfile(skill_name="Data Preprocessing", weight=0.18, required=True, category="technical"),
            SkillProfile(skill_name="Python ML Libraries", weight=0.15, required=True, category="tool"),
            SkillProfile(skill_name="Feature Engineering", weight=0.12, required=True, category="technical"),
            SkillProfile(skill_name="Model Optimization", weight=0.10, required=True, category="technical"),
        ],
        optional_skills=[
            SkillProfile(skill_name="Deep Learning (PyTorch/TensorFlow)", weight=0.10, required=False, category="technical"),
            SkillProfile(skill_name="MLOps", weight=0.08, required=False, category="technical"),
            SkillProfile(skill_name="Computer Vision/NLP", weight=0.08, required=False, category="technical"),
            SkillProfile(skill_name="Model Deployment", weight=0.07, required=False, category="technical"),
        ]
    ),
    
    "DevOps": RoleProfileSchema(
        role_type="DevOps",
        description="DevOps Internship - Focus on CI/CD, infrastructure, and automation",
        required_skills=[
            SkillProfile(skill_name="CI/CD Pipelines", weight=0.25, required=True, category="technical"),
            SkillProfile(skill_name="Docker/Containerization", weight=0.20, required=True, category="tool"),
            SkillProfile(skill_name="Cloud Platform (AWS/Azure/GCP)", weight=0.18, required=True, category="tool"),
            SkillProfile(skill_name="Infrastructure as Code", weight=0.15, required=True, category="technical"),
            SkillProfile(skill_name="Scripting (Bash/Python)", weight=0.12, required=True, category="technical"),
            SkillProfile(skill_name="Monitoring & Logging", weight=0.10, required=True, category="technical"),
        ],
        optional_skills=[
            SkillProfile(skill_name="Kubernetes", weight=0.10, required=False, category="tool"),
            SkillProfile(skill_name="Terraform/Ansible", weight=0.08, required=False, category="tool"),
            SkillProfile(skill_name="Security Best Practices", weight=0.07, required=False, category="technical"),
            SkillProfile(skill_name="Performance Tuning", weight=0.06, required=False, category="technical"),
        ]
    ),
    
    "FullStack": RoleProfileSchema(
        role_type="FullStack",
        description="Full Stack Development Internship - Frontend + Backend",
        required_skills=[
            SkillProfile(skill_name="Frontend Framework", weight=0.18, required=True, category="technical"),
            SkillProfile(skill_name="Backend Framework", weight=0.18, required=True, category="technical"),
            SkillProfile(skill_name="API Development", weight=0.15, required=True, category="technical"),
            SkillProfile(skill_name="Database", weight=0.15, required=True, category="technical"),
            SkillProfile(skill_name="JavaScript/TypeScript", weight=0.12, required=True, category="technical"),
            SkillProfile(skill_name="Authentication", weight=0.12, required=True, category="technical"),
            SkillProfile(skill_name="State Management", weight=0.10, required=True, category="technical"),
        ],
        optional_skills=[
            SkillProfile(skill_name="DevOps Basics", weight=0.08, required=False, category="technical"),
            SkillProfile(skill_name="Testing", weight=0.07, required=False, category="technical"),
            SkillProfile(skill_name="Microservices", weight=0.06, required=False, category="technical"),
        ]
    )
}


class RoleProfileManager:
    """Manage role profiles"""
    
    @staticmethod
    def get_profile(role_type: str) -> RoleProfileSchema:
        """Get profile for a role"""
        if role_type not in ROLE_PROFILES:
            raise ValueError(f"Unknown role type: {role_type}. Available: {list(ROLE_PROFILES.keys())}")
        return ROLE_PROFILES[role_type]
    
    @staticmethod
    def get_all_roles() -> List[str]:
        """Get all available role types"""
        return list(ROLE_PROFILES.keys())
    
    @staticmethod
    def get_required_skills(role_type: str) -> List[str]:
        """Get required skill names for a role"""
        profile = RoleProfileManager.get_profile(role_type)
        return [skill.skill_name for skill in profile.required_skills]
    
    @staticmethod
    def get_all_skills(role_type: str) -> List[str]:
        """Get all skill names (required + optional) for a role"""
        profile = RoleProfileManager.get_profile(role_type)
        return [skill.skill_name for skill in profile.required_skills + profile.optional_skills]
    
    @staticmethod
    def get_skill_weights(role_type: str) -> Dict[str, float]:
        """Get skill weights for a role"""
        profile = RoleProfileManager.get_profile(role_type)
        weights = {}
        for skill in profile.required_skills + profile.optional_skills:
            weights[skill.skill_name] = skill.weight
        return weights
    
    @staticmethod
    def calculate_skill_match(role_type: str, detected_skills: List[str]) -> float:
        """
        Calculate skill match percentage
        Returns: 0-100
        """
        profile = RoleProfileManager.get_profile(role_type)
        weights = RoleProfileManager.get_skill_weights(role_type)
        
        total_weight = 0.0
        matched_weight = 0.0
        
        for skill in profile.required_skills + profile.optional_skills:
            total_weight += skill.weight
            if any(detected.lower() in skill.skill_name.lower() or 
                   skill.skill_name.lower() in detected.lower() 
                   for detected in detected_skills):
                matched_weight += skill.weight
        
        return (matched_weight / total_weight * 100) if total_weight > 0 else 0.0
