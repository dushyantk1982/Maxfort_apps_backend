from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select, and_
from sqlalchemy import select, and_
from sqlalchemy import delete
from db.database import get_db
from models.app_credentials import AppCredentials
from models.user import User
from models.application import Application
import pandas as pd
import io
from schemas.user import AppCredentialInput
from schemas.apps_credential_out import ApplicationOut, UserOut, AppCredentialOut, ApplicationCredentialOut
from schemas.apps_credentials import CredentialUpdateRequest
from typing import List
from utils.encryption import encrypt_password, decrypt_password
from auth.auth_jwt import get_current_user
import traceback
import math

router = APIRouter()

# Replace NaN with None recursively
def clean_nan(obj):
    if isinstance(obj, list):
        return [clean_nan(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: clean_nan(v) for k, v in obj.items()}
    elif isinstance(obj, float) and math.isnan(obj):
        return None
    return obj


# To add apps credentials
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
        .where(AppCredentials.user_id == user_id).order_by(Application.id)
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





# User wise view app credentials
@router.get("/admin/user-credentials/{user_id}", response_model=List[AppCredentialOut])
async def get_user_credentials_admin(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Check if user is admin
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admin can access credentials")
    
    try:
        # Join AppCredentials with Application and User tables
        result = await db.execute(
            select(AppCredentials, Application, User)
            .join(Application, AppCredentials.application_id == Application.id)
            .join(User, AppCredentials.user_id == User.id)
            .where(AppCredentials.user_id == user_id).order_by(User.id)
        )
        rows = result.all()
        
        if not rows:
            return []  # Return empty list if no credentials found

        credentials = []
        for cred, app, user in rows:
            try:
                decrypted_password = decrypt_password(cred.password)
            except Exception:
                decrypted_password = "******"  # Use asterisks for invalid passwords
                
            credentials.append(
                AppCredentialOut(
                    app_name=app.name,
                    username=cred.username,
                    password=decrypted_password,
                    user_name=user.name,
                    user_email=user.email
                )
            )
        
        return credentials

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch credentials: {str(e)}")
    


# Generate and Download excel file
@router.get("/download-credentials-template")
async def download_credentials_template(db: AsyncSession = Depends(get_db)):
    try:
        # Fetch all users and applications
        users_result = await db.execute(select(User).order_by(User.id))
        apps_result = await db.execute(select(Application).order_by(Application.id))
        
        users = users_result.scalars().all()
        applications = apps_result.scalars().all()
        
        # Create a list to store the template data
        template_data = []
        
        # For each user, create rows for all applications
        for user in users:
            for app in applications:
                template_data.append({
                    'user_id': user.id,
                    'user_name': user.name,  # For reference
                    'user_email': user.email,  # For reference
                    'application_id': app.id,
                    'application_name': app.name,  # For reference
                    'username': '',  # Empty for user to fill
                    'password': ''   # Empty for user to fill
                })
        
        # Create DataFrame
        df = pd.DataFrame(template_data)

        # Sort the DataFrame by user_id and application_id
        df = df.sort_values(['user_id', 'application_id'])
        
        # Reorder columns
        df = df[['user_id', 'user_name', 'user_email', 'application_id', 'application_name', 'username', 'password']]
        
        # Create Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Credentials Template')
            
            # Get the worksheet
            worksheet = writer.sheets['Credentials Template']
            
            # Adjust column widths
            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(col)
                )
                worksheet.column_dimensions[chr(65 + idx)].width = max_length + 2
        
        output.seek(0)
        
        # Return the Excel file
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": "attachment; filename=credentials_template.xlsx"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# Upload Excel file(App Credentials)
@router.post("/bulk-upload-credentials")
async def bulk_upload_credentials(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    # try:
        # Read the Excel file
        df = pd.read_excel(file.file)
        
        # Validate required columns
        required_columns = ['user_id', 'application_id', 'username', 'password']
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(
                status_code=400, 
                detail="Excel file must contain columns: user_id, application_id, username, password"
            )
        
        # Remove any rows with empty credentials
        #df = df.dropna(subset=['username', 'password'])

        # Convert user_id and application_id to integers
        df['user_id'] = df['user_id'].astype(int)
        df['application_id'] = df['application_id'].astype(int)
        
        # Get all valid user IDs and application IDs
        users_result = await db.execute(select(User))
        apps_result = await db.execute(select(Application))
        # valid_users = {user.id for user in users_result.scalars().all()}
        # valid_apps = {app.id for app in apps_result.scalars().all()}
        
        # Validate user_ids and application_ids
        # invalid_users = set(df['user_id'].unique()) - valid_users
        # invalid_apps = set(df['application_id'].unique()) - valid_apps

        # Build lookup dictionaries
        # user_lookup = {user.id: user for user in users_result.scalars().all()}
        # app_lookup = {app.id: app for app in apps_result.scalars().all()}

        # Fetch all users and applications once
        users = users_result.scalars().all()
        apps = apps_result.scalars().all()

        # Build lookup sets and dictionaries
        valid_users = {user.id for user in users}
        valid_apps = {app.id for app in apps}
        user_lookup = {user.id: user for user in users}
        app_lookup = {app.id: app for app in apps}

        # Track valid rows to insert
        valid_rows = []
        
        # if invalid_users:
        #     raise HTTPException(
        #         status_code=400,
        #         detail=f"Invalid user IDs found: {invalid_users}"
        #     )
        # if invalid_apps:
        #     raise HTTPException(
        #         status_code=400,
        #         detail=f"Invalid application IDs found: {invalid_apps}"
        #     )
        
        # Process each row
        success_count = 0
        error_count = 0
        errors = []

         # First, delete existing credentials for the users in the file
        user_ids = df['user_id'].unique()
        await db.execute(
            delete(AppCredentials).where(AppCredentials.user_id.in_(user_ids))
        )
        
        # Process each row
        for idx, row in df.iterrows():
            row_number = idx + 2  # Excel header is on row 1
            try:
                user_id = int(row['user_id'])
                application_id = int(row['application_id'])
                # username = str(row['username'] or '').strip()
                # password = str(row['password'] or '').strip()
                username_raw = row['username']
                password_raw = row['password']

                # Explicitly handle NaN
                if pd.isna(username_raw) or pd.isna(password_raw):
                    raise ValueError("Empty username or password")

                username = str(username_raw).strip()
                password = str(password_raw).strip()

                # You can also keep a fallback check
                if not username or not password:
                    raise ValueError("Empty username or password")

                # Validate user_id and application_id
                if user_id not in user_lookup:
                    raise ValueError(f"Invalid user_id: {user_id}")
                if application_id not in app_lookup:
                    raise ValueError(f"Invalid application_id: {application_id}")

                # Validate email match if email column is present
                if 'user_email' in df.columns:
                    uploaded_email = str(row.get('user_email', '')).strip().lower()
                    actual_email = user_lookup[user_id].email.lower()
                    if uploaded_email and uploaded_email != actual_email:
                        raise ValueError(f"user_email mismatch for user_id {user_id} (Expected: {actual_email}, Got: {uploaded_email})")

                # Validate data
                # if not row['username'] or not row['password']:
                #     error_count += 1
                #     errors.append(f"Row {_ + 2}: Empty username or password")
                #     continue
                
                # Validate username/password
                # if not username or not password:
                #     raise ValueError("Empty username or password")


                # Create new credential
                # new_cred = AppCredentials(
                #     user_id=row['user_id'],
                #     application_id=row['application_id'],
                #     username=row['username'],
                #     password=encrypt_password(str(row['password']))  # Convert to string and encrypt
                # )
                # Create new credential
                new_cred = AppCredentials(
                    user_id=user_id,
                    application_id=application_id,
                    username=username,
                    password=encrypt_password(password)
                )

                db.add(new_cred)
                
                success_count += 1
                
            # except Exception as e:
            #     error_count += 1
            #     errors.append(f"Error processing row {_ + 2}: {str(e)}")
            except Exception as e:
                error_count += 1
                error_data = {
                    "row": row_number,
                    # "user_id": row.get('user_id'),
                    # "application_id": row.get('application_id'),
                    "user_name": user_lookup.get(user_id).name if user_id in user_lookup else f"Unknown (ID {user_id})",
                    "application_name": app_lookup.get(application_id).name if application_id in app_lookup else f"Unknown (ID {application_id})",
                    "username": row.get('username'),
                    "error": str(e)
                }
                errors.append(error_data)
        
        # Commit all changes
        await db.commit()
        
        print(success_count)
        print(error_count)
        print(errors)
        # content={"errors": clean_nan(errors if errors else None)}
        return {
            "message": "Bulk upload completed",
            "success_count": success_count,
            "error_count": error_count,
            # "errors": content
            "errors": clean_nan(errors if errors else None)
        }
        
    # except Exception as e:
    #     await db.rollback()
    #     raise HTTPException(status_code=500, detail=str(e))
    # finally:
    #     file.file.close()



# To update app credentials
@router.put("/update-credential/{user_email}/{app_name}")
async def update_credential(user_email:str, app_name:str, credential: CredentialUpdateRequest, db:
     AsyncSession = Depends(get_db)):
    try:
        # Get the user by email
        result = await db.execute(select(User).where(User.email == user_email))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get the application by name
        result = await db.execute(select(Application).where(Application.name == app_name))
        application = result.scalar_one_or_none()
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")

        # Check if the user is updating their own credentials
        # if current_user.email != user_email and current_user.role != "admin":
        #     raise HTTPException(
        #         status_code=403,
        #         detail="You can only update your own credentials"
        #     )

        # Get existing credential or create new one
        result = await db.execute(select(AppCredentials).where(and_(AppCredentials.user_id == user.id,
                AppCredentials.application_id == application.id)))
        existing_credential = result.scalar_one_or_none()

        if existing_credential:
            # Update existing credential
            existing_credential.username = credential.username
            existing_credential.password = encrypt_password(credential.password)
        else:
            # Create new credential
            new_credential = AppCredentials(
                user_id=user.id,
                application_id=application.id,
                username=credential.username,
                password=encrypt_password(credential.password)
            )
            db.add(new_credential)

        await db.commit()
        return {"message": "Credential updated successfully"}

    except Exception as e:
        await db.rollback()
        traceback.print_exc() 
        raise HTTPException(status_code=500, detail=str(e))
    
   