from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.database import get_db
from models.app_credentials import AppCredentials
from models.user import User
from models.application import Application
from schemas.user import AppCredentialInput
from schemas.apps_credential_out import ApplicationOut, UserOut
from typing import List

router = APIRouter()

@router.post("/add-credentials/{user_id}")
async def add_credentials(
    user_id: int,
    credentials: List[AppCredentialInput],
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        for cred in credentials:
            new_cred = AppCredentials(
                user_id=user_id,
                application_id=cred.app_id,
                username=cred.username,
                password=cred.password  # Consider encrypting this
            )
            db.add(new_cred)

        await db.commit()
        return {"message": "Credentials added successfully"}

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all_users", response_model=List[UserOut])
async def get_all_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users

@router.get("/applications", response_model=List[ApplicationOut])
async def get_all_applications(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Application))
    return result.scalars().all()
