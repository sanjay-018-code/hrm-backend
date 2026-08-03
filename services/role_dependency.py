from fastapi import Depends , HTTPException
from services.auth_dependency import get_current_user

def allow_roles(allowed_roles):
    def checker(current_user=Depends(get_current_user)):
        role = current_user.get("role")
        if role not in allowed_roles:
            raise HTTPException(403, "Access Denied")
        return current_user
    return checker