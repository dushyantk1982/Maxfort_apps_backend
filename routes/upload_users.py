from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from models.user import User
from db.database import get_db
from utils.security import hash_password
from starlette.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import pandas as pd
from io import BytesIO
import re
import pandas as pd
import traceback
import math
from fastapi.encoders import jsonable_encoder


# Function to change in string
def clean_str(value):
    if value is None:
        return None
    if isinstance(value, float):
        if math.isnan(value):
            return None
        if value.is_integer():
            return str(int(value))
        else:
            return str(value).strip()
    return str(value).strip()


# Function to validate mail id
def is_valid_email(email: str) -> bool:
    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(email_regex, email) is not None

# Function to clean failed users 
def clean_failed_user(user_dict):
    cleaned = {}
    for k, v in user_dict.items():
        if isinstance(v, float) and math.isnan(v):
            cleaned[k] = None
        elif isinstance(v, str):
            cleaned[k] = v.strip()
        else:
            cleaned[k] = v
    return cleaned

router = APIRouter()


@router.post("/upload-users")
async def upload_users(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    try:
        contents = await file.read()
        df = pd.read_excel(BytesIO(contents)) if file.filename.endswith(".xlsx") else pd.read_csv(BytesIO(contents))

        df.columns = [col.strip().lower().replace('\xa0', '').replace('\u200b', '') for col in df.columns]

        required_columns = {"name", "email", "mobile_number", "password", "role", "employee_code", "admission_no", "class", "section"}
        if not required_columns.issubset(set(df.columns)):
            print("Actual columns:", df.columns.tolist())  # helpful debug output
            raise HTTPException(status_code=400, detail=f"CSV/Excel must contain columns: {required_columns}")

        users_created = 0
        failed_users= []
        for _, row in df.iterrows():
            try:
                # Clean and extract values
                name = clean_str(row.get("name"))
                email = clean_str(row.get("email"))
                password = clean_str(row.get("password"))
                role = clean_str(row.get("role")).lower() if row.get("role") else None
                mobile_number = clean_str(row.get("mobile_number"))

                # Common optional fields — clean all upfront
                employee_code = clean_str(row.get("employee_code"))
                admission_no = clean_str(row.get("admission_no"))
                class_name = clean_str(row.get("class"))
                section = clean_str(row.get("section"))

                # Validate required fields
                if not email or not name or not mobile_number:
                    failed_users.append({
                        "name": name,
                        "email": email,
                        "mobile_number": mobile_number,
                        "employee_code": employee_code,
                        "admission_no": admission_no,
                        "class_name": class_name,
                        "section": section,
                        "reason": "Missing required fields"
                    })
                    continue

                if len(mobile_number) < 10 or not mobile_number.isdigit():
                    failed_users.append({
                        "name": name,
                        "email": email,
                        "mobile_number": mobile_number,
                        "reason": "Mobile number must be at least 10 digits"
                    })
                    continue

                if not is_valid_email(email):
                    failed_users.append({
                        "name": name,
                        "email": email,
                        "mobile_number": mobile_number,
                        "reason": "Invalid email format"
                    })
                    continue

                # Check for duplicates
                result = await db.execute(select(User).where(or_(User.email == email, User.mobile_number == mobile_number)))
                if result.scalar_one_or_none():
                    failed_users.append({
                        "name": name,
                        "email": email,
                        "mobile_number": mobile_number,
                        "reason": "Duplicate email or mobile"
                    })
                    continue

                # Build user data
                new_user_data = {
                    "name": name,
                    "email": email,
                    "mobile_number": mobile_number,
                    "password_hash": hash_password(password),
                    "role": role,
                    "is_active": True,
                }

                # Role-specific optional fields
                if role == "student":
                    new_user_data.update({
                        "employee_code": None,
                        "admission_no": admission_no,
                        "class_name": class_name,
                        "section": section,
                    })
                elif role == "teacher":
                    new_user_data.update({
                        "employee_code": employee_code,
                        "admission_no": None,
                        "class_name": None,
                        "section": None,
                    })
                else:
                    new_user_data.update({
                        "employee_code": employee_code,
                        "admission_no": None,
                        "class_name": None,
                        "section": None,
                    })

                # Save user
                new_user = User(**new_user_data)
                db.add(new_user)
                await db.commit()
                users_created += 1

            except Exception as row_error:
                await db.rollback()
                failed_users.append({
                    "name": name,
                    "email": email,
                    "mobile_number": mobile_number,
                    "employee_code": employee_code,
                    "admission_no": admission_no,
                    "class_name": class_name,
                    "section": section,
                    "reason": f"Processing error: {str(row_error)}"
                })


        # for _, row in df.iterrows():
        #     try:
        #         # Convert mobile_number to string to avoid asyncpg error
        #         mobile_number_str = str(row["mobile_number"]).strip()

        #         # Validate data
        #         if not row["email"] or not row["name"] or not mobile_number_str:
        #             failed_users.append({
        #                 "name": row.get("name", ""),
        #                 "email": row.get("email", ""),
        #                 "mobile_number": mobile_number_str,
        #                 "employee_code": row.get("employee_code", ""),
        #                 "admission_no": row.get("admission_no", ""),
        #                 "class_name": row.get("class", ""),
        #                 "section": row.get("section", ""),
        #                 "reason": "Missing required fields"
        #             })
        #             continue

        #         # Validate mobile number length (should be at least 10 digits)
        #         if len(mobile_number_str) < 10 or not mobile_number_str.isdigit():
        #             failed_users.append({
        #                 "name": row.get("name", ""),
        #                 "email": row.get("email", ""),
        #                 "mobile_number": mobile_number_str,
        #                 "employee_code": row.get("employee_code", ""),
        #                 "admission_no": row.get("admission_no", ""),
        #                 "class_name": row.get("class", ""),
        #                 "section": row.get("section", ""),
        #                 "reason": "Mobile number must be at least 10 digits"
        #             })
        #             continue
        #         # Validate email format
        #         if not is_valid_email(row["email"]):
        #             failed_users.append({
        #                 "name": row.get("name", ""),
        #                 "email": row.get("email", ""),
        #                 "mobile_number": mobile_number_str,
        #                 "employee_code": row.get("employee_code", ""),
        #                 "admission_no": row.get("admission_no", ""),
        #                 "class_name": row.get("class", ""),
        #                 "section": row.get("section", ""),
        #                 "reason": "Invalid email format"
        #             })
        #             continue

        #         # result = await db.execute(select(User).where(User.email == row["email"]) | (User.mobile_number == mobile_number_str))
        #         result = await db.execute(select(User).where(or_(User.email == row["email"], User.mobile_number == mobile_number_str)))
        #         existing_user = result.scalar_one_or_none()

        #         if existing_user:
        #             failed_users.append({
        #                 "name": row["name"],
        #                 "email": row["email"],
        #                 "mobile_number": mobile_number_str,
        #                 "employee_code": row.get("employee_code", ""),
        #                 "admission_no": row.get("admission_no", ""),
        #                 "class_name": row.get("class", ""),
        #                 "section": row.get("section", ""),
        #                 "reason": "User with this email or mobile number already exists"
        #             })
        #             continue

        #         new_user_data={
        #             "name": row["name"],
        #             "email": row["email"],
        #             "mobile_number": mobile_number_str,
        #             "is_active": True,
        #             "password_hash": hash_password(row["password"]),
        #             "role": row["role"],
        #         }
        #         employee_code = clean_str(row.get("employee_code"))
        #         admission_no = clean_str(row.get("admission_no"))
        #         class_name = clean_str(row.get("class"))
        #         section = clean_str(row.get("section"))
                
        #         role = row["role"].strip().lower()
                

        #         if role == "student":
        #             new_user_data["employee_code"] = None
        #             # new_user_data["admission_no"] = clean_str(row.get("admission_no"))
        #             new_user_data["admission_no"] = admission_no
        #             # new_user_data["class_name"] = clean_str(row.get("class"))
        #             new_user_data["class_name"] = class_name
        #             # new_user_data["section"] = clean_str(row.get("section"))
        #             new_user_data["section"] = section
        #         elif role == "teacher":
        #             # new_user_data["employee_code"] = clean_str(row.get("employee_code"))
        #             new_user_data["employee_code"] = employee_code
        #             new_user_data["admission_no"] = None
        #             new_user_data["class_name"] = None
        #             new_user_data["section"] = None
        #         else:
        #             # new_user_data["employee_code"] = clean_str(row.get("employee_code"))
        #             new_user_data["employee_code"] = employee_code
        #             new_user_data["admission_no"] = None
        #             new_user_data["class_name"] = None
        #             new_user_data["section"] = None
                
        #         new_user = User(**new_user_data)
        #         db.add(new_user)
        #         users_created += 1
        #         await db.commit()

        #     except Exception as row_error:
        #         await db.rollback()
        #         failed_users.append({
        #             "name": row.get("name", ""),
        #             "email": row.get("email", ""),
        #             "mobile_number": row.get("mobile_number", ""),
        #             "employee_code": row.get("employee_code", ""),
        #             "admission_no": row.get("admission_no", ""),
        #             "class_name": row.get("class", ""),
        #             "section": row.get("section", ""),
        #             "reason": f"Processing error: {str(row_error)}"
        #         })

        # await db.commit()
        # return {"message": f"{users_created} users uploaded successfully",
        #         "failed_users": failed_users}
        cleaned_failed_users = [clean_failed_user(user) for user in failed_users]
        return JSONResponse(content=jsonable_encoder({
            "message": f"{users_created} users uploaded successfully",
            "failed_users": cleaned_failed_users
        }))

    except Exception as e:
        # Log full stack trace to terminal
        traceback.print_exc()
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    
    