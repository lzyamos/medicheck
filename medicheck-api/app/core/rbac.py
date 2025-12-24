from fastapi import HTTPException, status

def require_role(user: dict, allowed: set[str]):
    if not user or user.get("role") not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied (role restriction)."
        )
