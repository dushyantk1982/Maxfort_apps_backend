import bcrypt
from sqlalchemy.orm import Session
from models import User
from sqlalchemy import or_
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
# from utils.hashing import get_password_hash

async def insert_initial_user(db: AsyncSession):
    result = await db.execute(select(User).where(or_(
        User.email == "admin@gmail.com",
        User.mobile_number == "9926216669")))
    user = result.scalar_one_or_none()

    if user:
        print("Admin already exists")
        return
    # To Encrypt password
    hashed_pw = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()

    new_user = User(
        name="Admin",
        email="admin@gmail.com",
        mobile_number="9926216669",
        is_active=True,
        role="admin",
        password_hash=hashed_pw,
    )

    try:
        db.add(new_user)
        await db.commit()
        print("Admin user created")
    except Exception as e:
        await db.rollback()
        print(f"Failed to create user: {e}")
