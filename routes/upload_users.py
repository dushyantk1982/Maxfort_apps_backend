from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from models.user import User
from db.database import get_db
from utils.security import hash_password
from sqlalchemy.exc import IntegrityError
import pandas as pd
from io import BytesIO
import re

# Function to validate mail id
def is_valid_email(email: str) -> bool:
    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(email_regex, email) is not None

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
        failed_users= []
        for _, row in df.iterrows():
            try:
                # Convert mobile_number to string to avoid asyncpg error
                mobile_number_str = str(row["mobile_number"])

                # Validate data
                if not row["email"] or not row["name"] or not mobile_number_str:
                    failed_users.append({
                        "name": row.get("name", ""),
                        "email": row.get("email", ""),
                        "mobile_number": mobile_number_str,
                        "reason": "Missing required fields"
                    })
                    continue

                # Validate mobile number length (should be at least 10 digits)
                if len(mobile_number_str) < 10 or not mobile_number_str.isdigit():
                    failed_users.append({
                        "name": row.get("name", ""),
                        "email": row.get("email", ""),
                        "mobile_number": mobile_number_str,
                        "reason": "Mobile number must be at least 10 digits"
                    })
                    continue
                # Validate email format
                if not is_valid_email(row["email"]):
                    failed_users.append({
                        "name": row.get("name", ""),
                        "email": row.get("email", ""),
                        "mobile_number": mobile_number_str,
                        "reason": "Invalid email format"
                    })
                    continue

                # result = await db.execute(select(User).where(User.email == row["email"]) | (User.mobile_number == mobile_number_str))
                result = await db.execute(select(User).where(or_(User.email == row["email"], User.mobile_number == mobile_number_str)))
                existing_user = result.scalar_one_or_none()

                if existing_user:
                    failed_users.append({
                        "name": row["name"],
                        "email": row["email"],
                        "mobile_number": mobile_number_str,
                        "reason": "User with this email or mobile number already exists"
                    })
                    continue

                # # Convert mobile_number to string to avoid asyncpg error
                # mobile_number_str = str(row["mobile_number"])

                new_user = User(
                    name=row["name"],
                    email=row["email"],
                    mobile_number=mobile_number_str,
                    password_hash=hash_password(row["password"]),
                    role=row["role"]
                )
                db.add(new_user)
                users_created += 1

            except Exception as row_error:
                failed_users.append({
                    "name": row.get("name", ""),
                    "email": row.get("email", ""),
                    "mobile_number": row.get("mobile_number", ""),
                    "reason": f"Processing error: {str(row_error)}"
                })

        await db.commit()
        return {"message": f"{users_created} users uploaded successfully",
                "failed_users": failed_users}

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
