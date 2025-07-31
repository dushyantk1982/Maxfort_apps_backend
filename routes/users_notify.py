from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, distinct
from db.database import get_db
from models import User
from schemas.user import UserResponse
from typing import List

router = APIRouter()

@router.get("/users/search", response_model=List[UserResponse])
async def search_users(query: str = Query(...), db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(
        or_(
            User.employee_code.ilike(f"%{query}%"),
            User.admission_no.ilike(f"%{query}%"),
            User.class_name.ilike(f"%{query}%"),
            User.section.ilike(f"%{query}%"),
        )
    )
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/users/filters")
async def get_user_filter(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(
            User.employee_code,
            User.admission_no,
            User.class_name,
            User.section,
        ).distinct()
    )

    filters = result.all()

    print("Fetched Filters:", filters)
    return[
        {
            "employee_codes": row[0],
            "admission_nos": row[1],
            "class_names": row[2],
            "sections": row[3],
        }
        for row in filters
    ]