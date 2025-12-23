"""Auth module initialization"""
from .auth import (
    get_current_user,
    require_auth,
    require_student,
    require_recruiter,
    require_admin,
    CurrentUser
)

__all__ = [
    "get_current_user",
    "require_auth",
    "require_student",
    "require_recruiter",
    "require_admin",
    "CurrentUser"
]
