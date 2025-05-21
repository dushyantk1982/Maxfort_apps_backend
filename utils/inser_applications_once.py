import asyncio
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from db.database import SessionLocal
from models.application import Application  # adjust the path if needed

# Create a database session
# db: Session = SessionLocal()

# Define your application data
async def insert_initial_apps(db: AsyncSession):
# to add applicationss
    apps = [
            {
                "name": "Microsoft Outlook",
                "app_url": "https://outlook.office365.com/mail/",
                "icon_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTHg-9a54f3dr8FdBjk4E7_ORnM1UCfJTxSlw&s",
                "is_microsoft_oauth": True
            },
            {
                "name": "Schoology (LMS)",
                "app_url": "https://maxfortrohini.schoology.com",
                "icon_url": "https://static.wixstatic.com/media/a753e4_e21621006fe54c9b9bd52e8e72fffe06~mv2.png/v1/fill/w_372,h_350,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/PowerSchool%20Parent%20Portal%20-%20just%20logo.png",
                "is_microsoft_oauth": True
            },
            {
                "name": "Entab (ERP)",
                "app_url": "https://www.maxfortcampuscare.in/",
                "icon_url": "https://maxfortrohini.in/wp-content/uploads/2022/12/Maxfort-logo-VB-v2.1-354x300-1.png",
                "is_microsoft_oauth": False
            },
            {
                "name": "Embibe",
                "app_url": "https://www.embibe.com",  # fixed the missing protocol
                "icon_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTEzkaVgt8prNMg0D409JnstHY4yAdMCt-nTpDaLcOumKAXz40tmMSgn3_xxcG8p30byLM&usqp=CAU",
                "is_microsoft_oauth": False
            },
            {
                "name": "Scholastic E- library",
                "app_url": "https://slz02.scholasticlearningzone.com/resources/dp-int/dist/#/login3/INDWTPQ",
                "icon_url": "https://slz02.scholasticlearningzone.com/resources/dp-int/dist/assets/images/scholastic_logo.jpg",
                "is_microsoft_oauth": False
            },
            {
                "name": "Razplus from learning A-Z",
                "app_url": "https://www.kidsa-z.com/ng/",
                "icon_url": "https://aimkt.misacdn.net/app/vr8x81d7/attachment/41f49e45-cff8-4e3a-96bf-c41c7938b3de.png",
                "is_microsoft_oauth": False
            },
            {
                "name": "ICT 360",
                "app_url": "https://kms.ict360.com/ict_v3/login",
                "icon_url": "https://kms.ict360.com/ict_v3/assets/images/ict_logo.png",
                "is_microsoft_oauth": False
            }

        ]

    async with db as session:
        for app in apps:
            result = await session.execute(select(Application).where(Application.name == app['name']))
            existing = result.scalar_one_or_none()
            if not existing:
                new_app = Application(**app)
                session.add(new_app)

        await session.commit()


