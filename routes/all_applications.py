from fastapi import APIRouter, Depends
from sqlalchemy.future import select
# from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from models import Application

router = APIRouter()

@router.get("/all_applications")
async def get_applications(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Application))
    applications = result.scalars().all()
    return applications
    
