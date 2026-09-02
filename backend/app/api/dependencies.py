"""
Common FastAPI dependencies for authentication, database sessions, and parameters.
"""
from typing import Optional
from fastapi import Header, HTTPException, status


def get_current_user_role(x_user_role: Optional[str] = Header(default="CONTROLLER")) -> str:
    """
    Development/Demo role selection header dependency.
    Supported roles: CONTROLLER, MAINTENANCE, ADMIN.
    """
    allowed_roles = {"CONTROLLER", "MAINTENANCE", "ADMIN"}
    role = (x_user_role or "CONTROLLER").upper()
    if role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Allowed roles: {', '.join(allowed_roles)}"
        )
    return role
