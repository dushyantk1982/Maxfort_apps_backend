from fastapi import APIRouter, Depends, Query
# from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from sqlalchemy import func
from db.database import get_db
from models.user import User
from pydantic import BaseModel
from typing import List
from pydantic import TypeAdapter
from typing import Optional

router = APIRouter()

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    mobile_number: str
    role: str
    is_active: bool
    employee_code: str
    admission_no:str
    class_name:str
    section:str

    model_config = {
        "from_attributes": True  # Pydantic v2 way to support ORM mode
    }

@router.get("/users")
async def get_users(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(15, le=100),
    # search_filter: str = Query(None),
    # employee_code: str = Query(None),
    # admission_no: str = Query(None),
    # class_name: str = Query(None),
    # section: str = Query(None),
    # user_role: str = Query(None),

    search_filter: Optional[str] = None,
    employee_code: Optional[str] = None,
    admission_no: Optional[str] = None,
    class_name: Optional[str] = None,
    section: Optional[str] = None,
    user_role: Optional[str] = None,
    
):
    offset = (page - 1) * per_page

    query = select(User)
    count_query = select(func.count(User.id))

    user_filter = []

    if search_filter:
        like_pattern = f"{search_filter}"

# For filter
        user_filter.append(or_(
            User.employee_code.ilike(like_pattern),
            User.admission_no.ilike(like_pattern),
            User.class_name.ilike(like_pattern),
            User.section.ilike(like_pattern),
            User.role.ilike(like_pattern),
        
        ))

    if employee_code:
        user_filter.append(User.employee_code == employee_code)
    if admission_no:
        user_filter.append(User.admission_no == admission_no)
    if class_name:
        user_filter.append(User.class_name == class_name)
    if section:
        user_filter.append(User.section == section)
    if user_role:
        user_filter.append(User.role == user_role)

    if user_filter:
        query = query.where(*user_filter)
        count_query = count_query.where(*user_filter)
        



# this is search bar
        # filter_condition  = or_(User.admission_no.ilike(like_pattern) | User.employee_code.ilike(like_pattern) | User.class_name.ilike(like_pattern) | User.section.ilike(like_pattern))
        # query = query.where(filter_condition)
        # count_query = count_query.where(filter_condition)

    
    # total_query = select(func.count()).select_from(query.subquery())

    total = await db.scalar(count_query)

    result = await db.execute(query.order_by(User.id).offset(offset).limit(per_page))


    # Count total users
    # total = await db.scalar(select(func.count(User.id)))
    
    # Get paginated results
    # offset = (page - 1) * per_page
    # result = await db.execute(select(User).order_by(User.id).offset(offset).limit(per_page))
    users = result.scalars().all()

    # users_data = [UserOut.from_orm(user).dict() for user in users]
     # Use TypeAdapter for list of ORM objects
    adapter = TypeAdapter(List[UserOut])
    users_data = adapter.dump_python(users)

    return JSONResponse(content={
        "users": users_data,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    })

    


# Route to add filter functionality
@router.get("/users/userFilters")
async def get_user_filters(db: AsyncSession = Depends(get_db)):
    employee_code = await db.execute(select(func.distinct(User.employee_code)).order_by(User.employee_code))
    admission_no = await db.execute(select(func.distinct(User.admission_no)).order_by(User.admission_no))
    class_names = await db.execute(select(func.distinct(User.class_name)).order_by(User.class_name))
    sections = await db.execute(select(func.distinct(User.section)).order_by(User.section))
    roles = await db.execute(select(func.distinct(User.role)).order_by(User.role))

    return {
        "employee_codes": [row[0] for row in employee_code.all() if row[0]],
        "admission_nos": [row[0] for row in admission_no.all() if row[0]],
        "class_names": [row[0] for row in class_names.all() if row[0]],
        "sections": [row[0] for row in sections.all() if row[0]],
        "roles": [row[0] for row in roles.all() if row[0]],
    }