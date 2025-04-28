from fastapi import APIRouter, Depends, Query
# from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from db.database import get_db
from models.user import User
from pydantic import BaseModel
from typing import List
from pydantic import TypeAdapter

router = APIRouter()

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    mobile_number: str
    role: str
    is_active: bool

    model_config = {
        "from_attributes": True  # Pydantic v2 way to support ORM mode
    }

@router.get("/users")
async def get_users(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(15, le=100)
):
    # Count total users
    total = await db.scalar(select(func.count(User.id)))
    
    # Get paginated results
    offset = (page - 1) * per_page
    result = await db.execute(select(User).offset(offset).limit(per_page))
    users = result.scalars().all()

    # users_data = [UserOut.from_orm(user).dict() for user in users]
     # Use TypeAdapter for list of ORM objects
    adapter = TypeAdapter(List[UserOut])
    users_data = adapter.dump_python(users)

    return JSONResponse(content={
        "users": users_data,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    })

    