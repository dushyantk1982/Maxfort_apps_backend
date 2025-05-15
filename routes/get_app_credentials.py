# router_app_credentials.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.database import get_db
from models import AppCredentials, User, Application
from auth.auth_jwt import get_current_user
from pydantic import BaseModel

router = APIRouter()

class AppCredentialResponse(BaseModel):
    username: str
    password: str

@router.get("/app-credentials/{app_name}", response_model=AppCredentialResponse)
async def get_app_credentials(
    app_name: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    # find the application by name
    result = await session.execute(
        select(Application).where(Application.name == app_name)
    )
    application = result.scalar_one_or_none()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # find credentials
    result = await session.execute(
        select(AppCredentials)
        .where(AppCredentials.user_id == current_user["id"])
        .where(AppCredentials.application_id == application.id)
    )
    credentials = result.scalar_one_or_none()

    if not credentials:
        raise HTTPException(status_code=404, detail="No credentials found for this app")

    return AppCredentialResponse(
        username=credentials.username,
        password=credentials.password
    )
