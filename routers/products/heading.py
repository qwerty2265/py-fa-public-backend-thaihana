from datetime import datetime

from fastapi import APIRouter, Depends, Request, HTTPException, Body, Query
from fastapi.encoders import jsonable_encoder

from models.category import Category
from models.heading import Heading
from routers.auth.auth_bearer import JWTBearer
from schemas.heading import HeadingCreate, HeadingUpdate
from utils import to_slug
from sqlalchemy import select, insert, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from config import LIMIT
from models.base import get_async_session
from models.user import User
from routers.products.products import get_product_by_slug

router = APIRouter(
    prefix="/headings",
    tags=['headings']
)


@router.get("/id/{heading_id}")
async def get_heading_by_id(heading_id: int, session: AsyncSession = Depends(get_async_session)):
    query = select(Heading).where(Heading.id == heading_id)
    result = await session.execute(query)
    end = result.first()

    if end is None:
        return None
    return jsonable_encoder(end[0])


@router.get("/{heading_slug}")
async def get_heading_by_slug(heading_slug: str, session: AsyncSession = Depends(get_async_session)):
    query = select(Heading).where(Heading.heading_slug == heading_slug)
    result = await session.execute(query)
    end = result.first()

    if end is None:
        return None
    return jsonable_encoder(end[0])


@router.get("")
async def get_heading_all(offset: int, limit: int, search_query: str = Query(default=""),
                          session: AsyncSession = Depends(get_async_session)):
    if limit > LIMIT:
        raise HTTPException(status_code=403, detail="Forbidden")

    query = select(Heading).where(Heading.visible).offset(offset).limit(limit) \
        .where(func.lower(Heading.heading_name).contains(search_query.lower()))
    result = await session.execute(query)

    list = []
    for key, category in enumerate(result.fetchall()):
        list.append(jsonable_encoder(category[0]))

    return list


@router.get("/categories/{heading_slug}")
async def get_categories_of_heading_all(heading_slug: str,
                                        session: AsyncSession = Depends(get_async_session)):
    heading = await get_heading_by_slug(heading_slug, session)
    if heading is None:
        return {"status": "failure"}

    query = select(Category).where(Category.visible).where(Category.heading_id == heading["id"])
    result = await session.execute(query)

    list = []
    for key, category in enumerate(result.fetchall()):
        list.append(jsonable_encoder(category[0]))

    return list


@router.post("/create")
async def create_heading(new_heading: HeadingCreate,
                         user: User = Depends(JWTBearer()),
                         session: AsyncSession = Depends(get_async_session)):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden")

    slug = to_slug(f"{new_heading.heading_name}")

    query = select(Heading).where(Heading.heading_slug == slug)
    result = (await session.execute(query)).fetchall()
    if len(result) != 0:
        return {"status": "failure", "detail": "slug is already exists"}

    statement = insert(Heading).values(**new_heading.dict(), heading_slug=slug)
    await session.execute(statement)
    await session.commit()

    return {"status": "success"}


@router.put("/id/{heading_id}")
async def update_heading_by_id(request: Request,
                               heading_id: int,
                               updated_categories: HeadingUpdate,
                               user: User = Depends(JWTBearer()),
                               session: AsyncSession = Depends(get_async_session)):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden")

    query = select(Heading).where(Heading.id == heading_id)
    result = (await session.execute(query)).first()

    if result is None:
        raise HTTPException(status_code=400, detail="Heading doesn't exist!")

    override_dict = jsonable_encoder(result[0])
    new_dict = updated_categories.dict()

    for key in override_dict:
        if key in new_dict and new_dict[key] is not None:
            override_dict[key] = new_dict[key]

    override_dict.pop("modified_at")
    override_dict.pop("created_at")

    statement = update(Heading).where(Heading.id == heading_id).values(**override_dict,
                                                                       created_at=result[0].created_at,
                                                                       modified_at=datetime.utcnow())
    await session.execute(statement)
    await session.commit()

    return {"status": "success"}


@router.put("/{heading_slug}")
async def update_heading_by_slug(request: Request,
                                 heading_slug: str,
                                 updated_product=Body(..., embed=True),
                                 user: User = Depends(JWTBearer()),
                                 session: AsyncSession = Depends(get_async_session)):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden")

    heading = await get_heading_by_slug(heading_slug, session)
    if heading is None:
        return {"status": "failure"}

    return await update_heading_by_id(request, heading["id"], updated_product, user, session)
