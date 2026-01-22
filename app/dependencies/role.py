from fastapi import Depends, HTTPException, status
from app.core.authen import get_current_user
from app.models.models import users

def require_roles(*allowed_roles):
    def role_dependency(current_user: users = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are not allowed to perform this action")
        return current_user
    return role_dependency

