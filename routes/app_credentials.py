from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.database import get_db
from models.app_credentials import AppCredentials
from models.user import User
from models.application import Application
from schemas.user import AppCredentialInput
from schemas.apps_credential_out import ApplicationOut, UserOut, AppCredentialOut
from typing import List
from utils.encryption import encrypt_password, decrypt_password

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
            encrypted_password = encrypt_password(cred.password) # To encrypt password
            new_cred = AppCredentials(
                user_id=user_id,
                application_id=cred.app_id,
                username=cred.username,
                password=encrypted_password  
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


# Get user credentials 
@router.get("/user-credentials/{user_id}", response_model=List[AppCredentialOut])
async def get_user_credentials(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AppCredentials, Application)
        .join(Application, AppCredentials.application_id == Application.id)
        .where(AppCredentials.user_id == user_id)
    )
    rows = result.all()
    if not rows:
        raise HTTPException(status_code=404, detail="No credentials found")

    return [
        AppCredentialOut(
            app_name=app.name,
            username=cred.username,
            # password=cred.password
            password=decrypt_password(cred.password)  # Decrypt the password
        )
        for cred, app in rows
    ]