from fastapi import FastAPI, Depends, HTTPException
from db.database import engine
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db import database  
from models import user, application, app_credentials, otps
from fastapi.middleware.cors import CORSMiddleware
from db.database import Base, engine, SessionLocal
from contextlib import asynccontextmanager
from routes import admin, auth_otp, protected_route, auth, user_list, update_user, upload_users, app_credentials, all_applications, get_app_credentials, get_profile, notifications, users_to_notify
from starlette.routing import BaseRoute
from models.otps import OTP
import logging
from utils.insert_initial_user import insert_initial_user
from utils.inser_applications_once import insert_initial_apps
import os
from sqlalchemy import inspect
from sqlalchemy.future import select
from models.user import User

app = FastAPI(root_path="/api")



# Lifespan context for initializing the DB
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        inspector = inspect(conn.sync_engine)
        tables = inspector.get_table_names()

        if "users" not in tables or "applications" not in tables or "app_credentials" not in tables or "otps" not in tables:
            await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        user_exists = await session.execute(select(User).limit(1))
        if not user_exists.scalar():
            await insert_initial_user(session)
            await insert_initial_apps(session)

    yield

# Only one instance of FastAPI with lifespan
app = FastAPI(lifespan=lifespan)

@app.post("/insert_initial")
async def read_root():
    return {"msg": "User created"}

# Include all routers
app.include_router(admin.router)
app.include_router(auth_otp.router)
app.include_router(protected_route.protected_router)
app.include_router(auth.router)
app.include_router(user_list.router)
app.include_router(update_user.router)
app.include_router(upload_users.router)
app.include_router(app_credentials.router)
app.include_router(all_applications.router)
app.include_router(get_app_credentials.router)
app.include_router(get_profile.router)


# Allow request from ReactJS
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.DEBUG)
@app.get("/routes-debug")
def get_routes():
    # return [{"path": route.path, "methods": list(route.methods)} for route in app.routes]
    return [
        {
            "path": route.path,
            "methods": list(route.methods),
            "name": route.name,
            "endpoint": route.endpoint.__name__ if hasattr(route.endpoint, "__name__") else str(route.endpoint)
        }
        for route in app.routes
        if hasattr(route, "methods")
    ]