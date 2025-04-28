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

    apps = [
            {
                "name": "Microsoft Outlook",
                "app_url": "https://login.microsoftonline.com/common/oauth2/authorize?client_id=00000002-0000-0ff1-ce00-000000000000&redirect_uri=https%3a%2f%2foutlook.office365.com%2fowa%2f&resource=00000002-0000-0ff1-ce00-000000000000&response_mode=form_post&response_type=code+id_token&scope=openid&msafed=1&msaredir=1&client-request-id=23d508a5-df78-2562-5cab-e568ccc3ba0d&protectedtoken=true&claims=%7b%22id_token%22%3a%7b%22xms_cc%22%3a%7b%22values%22%3a%5b%22CP1%22%5d%7d%7d%7d&nonce=638767523468902311.ce8c037e-3f69-40bc-b8a9-e0ded7cc319d&state=Dcu9DoIwFEDhou_iVrltoT8DcTAxDOCAJBq29rYmEgmmEIxvb4fvbCcjhOyTXZJBClFSaCVVyUUhtQEuGDti0AhCBSqe0tACHFKnraEBfPAKUTDjs_TW-fy1-WlZ7RoqdojBv2LAtZ8rW3eAdSubn9n8o1scN7GZzDRM73HoW369laPjsLn75ePO-g8&sso_reload=true",
                "icon_url": "https://uhf.microsoft.com/images/microsoft/RE1Mu3b.png",
                "is_microsoft_oauth": True
            },
            {
                "name": "Schoology (LMS)",
                "app_url": "https://maxfortrohini.schoology.com",
                "icon_url": "https://uhf.microsoft.com/images/microsoft/RE1Mu3b.png",
                "is_microsoft_oauth": False
            },
            {
                "name": "Entab (ERP)",
                "app_url": "https://www.maxfortcampuscare.in/",
                "icon_url": "https://maxfortrohini.in/wp-content/uploads/2022/12/Maxfort-logo-VB-v2.1-354x300-1.png",
                "is_microsoft_oauth": False
            },
            {
                "name": "Embibe",
                "app_url": "http://www.embibe.com",  # fixed the missing protocol
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


