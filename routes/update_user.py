# routes/user_route.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from schemas.UserUpdateSchema import UserUpdateSchema
from models import User
from db.database import get_db, SessionLocal
from utils.security import hash_password

router = APIRouter()

@router.put("/users/{user_id}")
async def update_user(user_id: int, updated_user: UserUpdateSchema, db: AsyncSession = Depends(get_db)):
    print("Incoming data:", updated_user)
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.name = updated_user.name
    user.email = updated_user.email
    user.mobile_number = updated_user.mobile_number
    user.role = updated_user.role
    user.is_active = updated_user.is_active
    user.employee_code = updated_user.employee_code
    user.admission_no = updated_user.admission_no
    user.class_name = updated_user.class_name
    user.section = updated_user.section

    if updated_user.password:
        user.password_hash = hash_password(updated_user.password)
    # if updated_user.name is not None:
    #     user.name = updated_user.name
    # if updated_user.email is not None:
    #     user.email = updated_user.email
    # if updated_user.mobile_number is not None:
    #     user.mobile_number = updated_user.mobile_number
    # if updated_user.role is not None:
    #     user.role = updated_user.role
    # if updated_user.is_active is not None:
    #     user.is_active = updated_user.is_active
    # if updated_user.password:
    #     user.password_hash = hash_password(updated_user.password)

    try:
        await db.commit()
        await db.refresh(user)
        return {
                "message": "User updated successfully",
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "mobile_number": user.mobile_number,
                    "role": user.role,
                    "is_active": user.is_active,
                    "employee_code": user.employee_code,
                    "admission_no": user.admission_no,
                    "class_name": user.class_name,
                    "section": user.section,
                    "password_hash":user.password_hash,
                }
            }
    except Exception as e:
        await db.rollback()
        print("Error during user update:", str(e))
        raise HTTPException(status_code=500, detail="Failed to update user")