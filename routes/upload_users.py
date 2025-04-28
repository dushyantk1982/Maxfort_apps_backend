from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.user import User
from db.database import get_db
from utils.security import hash_password
from sqlalchemy.exc import IntegrityError
import pandas as pd
from io import BytesIO

router = APIRouter()

@router.post("/upload-users")
async def upload_users(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    try:
        contents = await file.read()
        df = pd.read_excel(BytesIO(contents)) if file.filename.endswith(".xlsx") else pd.read_csv(BytesIO(contents))

        required_columns = {"name", "email", "mobile_number", "password", "role"}
        if not required_columns.issubset(set(df.columns)):
            raise HTTPException(status_code=400, detail=f"CSV/Excel must contain columns: {required_columns}")

        users_created = 0
        for _, row in df.iterrows():
            result = await db.execute(select(User).where(User.email == row["email"]) | (User.mobile_number == mobile_number_str))
            existing_user = result.scalar_one_or_none()

            if existing_user:
                continue

            # Convert mobile_number to string to avoid asyncpg error
            mobile_number_str = str(row["mobile_number"])

            new_user = User(
                name=row["name"],
                email=row["email"],
                mobile_number=mobile_number_str,
                password_hash=hash_password(row["password"]),
                role=row["role"]
            )
            db.add(new_user)
            users_created += 1

        await db.commit()
        return {"message": f"{users_created} users uploaded successfully"}

    except Exception as e:
        await db.rollback()
        print("Error processing uploaded file:", e)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
