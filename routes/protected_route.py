from fastapi import APIRouter, Depends, HTTPException
from auth.auth_jwt import get_current_user

protected_router = APIRouter()

@protected_router.get("/protected")
async def protected_endpoint(user: dict = Depends(get_current_user)):
    # return {"message": "Welcome!", "user": user}
    return {"message": f"Welcome, {user['role']}!", "user": user}

# @protected_router.get("/admin-only")
# async def admin_only(user: dict = Depends(get_current_user)):
#     if user["role"] != "admin":
#         raise HTTPException(status_code=403, detail="Admins only")
#     return {"message": f"Welcome Admin {user['username']}"}

# @protected_router.get("/teacher-only")
# async def teacher_only(user: dict = Depends(get_current_user)):
#     if user["role"] != "teacher":
#         raise HTTPException(status_code=403, detail="Teachers only")
#     return {"message": f"Welcome Teacher {user['username']}"}

# @protected_router.get("/student-only")
# async def student_only(user: dict = Depends(get_current_user)):
#     if user["role"] != "student":
#         raise HTTPException(status_code=403, detail="Students only")
#     return {"message": f"Welcome Student {user['username']}"}

