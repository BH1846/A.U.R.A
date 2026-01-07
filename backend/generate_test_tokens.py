"""
Test token generator for I-Intern integration
Use this to generate JWT tokens for testing student/recruiter portals
"""
import jwt
from datetime import datetime, timedelta
from config import settings

def generate_student_token(user_id="1", email="student@test.com", name="Test Student"):
    """Generate a test student token"""
    payload = {
        "user_id": user_id,
        "email": email,
        "name": name,
        "role": "student",
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token

def generate_recruiter_token(user_id="2", email="recruiter@company.com", name="Test Recruiter", company_id=1):
    """Generate a test recruiter token"""
    payload = {
        "user_id": user_id,
        "email": email,
        "name": name,
        "role": "recruiter",
        "company_id": company_id,
        "company_name": "Test Company",
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token

if __name__ == "__main__":
    print("=" * 80)
    print("AURA I-INTERN INTEGRATION - TEST TOKENS")
    print("=" * 80)
    print()
    
    # Generate student token
    student_token = generate_student_token()
    print("STUDENT TOKEN:")
    print(student_token)
    print()
    print("Student URL:")
    print(f"http://localhost:5173/?token={student_token}")
    print("Or: http://localhost:5173/student/dashboard?token={token}")
    print()
    print("-" * 80)
    print()
    
    # Generate recruiter token
    recruiter_token = generate_recruiter_token()
    print("RECRUITER TOKEN:")
    print(recruiter_token)
    print()
    print("Recruiter URL:")
    print(f"http://localhost:5173/?token={recruiter_token}")
    print("Or: http://localhost:5173/company/dashboard?token={token}")
    print()
    print("=" * 80)
    print()
    print("Copy one of the URLs above and paste in your browser to test!")
    print("The token will be automatically stored and you'll see role-based navigation.")
