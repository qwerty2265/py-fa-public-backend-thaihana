from datetime import datetime

from fastapi import APIRouter, Depends, Request, HTTPException, Body, Query
from fastapi.encoders import jsonable_encoder

from routers.auth.auth_bearer import JWTBearer
from utils import to_slug
from sqlalchemy import select, insert, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from config import LIMIT
from models.base import get_async_session
from models.category import Category
from models.product import ProductCategories
from models.user import User
from routers.products.products import get_product_by_slug
from schemas.category import CategoryUpdate

router = APIRouter(
    prefix="/categories",
    tags=['categories']
)


@router.get("/id/{category_id}")
async def get_category_by_id(category_id: int, session: AsyncSession = Depends(get_async_session)):
    query = select(Category).where(Category.id == category_id)
    result = await session.execute(query)
    end = result.first()

    if end is None:
        return None
    return jsonable_encoder(end[0])


@router.get("/{category_slug}")
async def get_category_by_slug(category_slug: str, session: AsyncSession = Depends(get_async_session)):
    query = select(Category).where(Category.category_slug == category_slug)
    result = await session.execute(query)
    end = result.first()

    if end is None:
        return None
    return jsonable_encoder(end[0])


@router.get("")
async def get_category_all(offset: int, limit: int, search_query: str = Query(default=""), session: AsyncSession = Depends(get_async_session)):
    if limit > LIMIT:
        raise HTTPException(status_code=403, detail="Forbidden")

    query = select(Category).where(Category.visible).offset(offset).limit(limit).where(func.lower(Category.category_name).contains(search_query.lower()))
    result = await session.execute(query)

    list = []
    for key, category in enumerate(result.fetchall()):
        list.append(jsonable_encoder(category[0]))

    return list


@router.post("/create")
async def create_category(request: Request,
                          new_category: CategoryUpdate,
                          user: User = Depends(JWTBearer()),
                          session: AsyncSession = Depends(get_async_session)):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden")

    slug = to_slug(f"{new_category.category_name}")

    query = select(Category).where(Category.category_slug == slug)
    result = (await session.execute(query)).fetchall()
    if len(result) != 0:
        return {"status": "failure", "detail": "slug is already exists"}

    statement = insert(Category).values(**new_category.dict(), category_slug=slug)
    await session.execute(statement)
    await session.commit()

    return {"status": "success"}


@router.put("/id/{category_id}")
async def update_category_by_id(request: Request,
                                category_id: int,
                                updated_categories: CategoryUpdate,
                                user: User = Depends(JWTBearer()),
                                session: AsyncSession = Depends(get_async_session)):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden")

    query = select(Category).where(Category.id == category_id)
    result = (await session.execute(query)).first()

    if result is None:
        raise HTTPException(status_code=400, detail="Category doesn't exist!")

    override_dict = jsonable_encoder(result[0])
    new_dict = updated_categories.dict()

    for key in override_dict:
        if key in new_dict and new_dict[key] is not None:
            override_dict[key] = new_dict[key]

    override_dict.pop("modified_at")
    override_dict.pop("created_at")

    statement = update(Category).where(Category.id == category_id).values(**override_dict,
                                                                          created_at=result[0].created_at,
                                                                          modified_at=datetime.utcnow())
    await session.execute(statement)
    await session.commit()

    return {"status": "success"}


@router.put("/{category_slug}")
async def update_category_by_slug(request: Request,
                                  category_slug: str,
                                  updated_product=Body(..., embed=True),
                                  user: User = Depends(JWTBearer()),
                                  session: AsyncSession = Depends(get_async_session)):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden")

    category = await get_category_by_slug(category_slug, session)
    if category is None:
        return {"status": "failure"}

    return await update_category_by_id(request, category["id"], updated_product, user, session)


@router.post("/id/{product_id}/add/{category_id}")
async def add_category_to_product(request: Request,
                                  product_id: int,
                                  category_id: int,
                                  user: User = Depends(JWTBearer()),
                                  session: AsyncSession = Depends(get_async_session)):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden")

    statement = insert(ProductCategories).values({
        "category_id": category_id,
        "product_id": product_id
    })
    await session.execute(statement)
    await session.commit()

    return {"status": "success"}


@router.post("/{product_slug}/add/{category_slug}")
async def add_category_to_product_by_slug(request: Request,
                                          product_slug: str,
                                          category_slug: str,
                                          user: User = Depends(JWTBearer()),
                                          session: AsyncSession = Depends(get_async_session)):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden")

    category = await get_category_by_slug(category_slug, session)
    product = await get_product_by_slug(product_slug, session)

    return await add_category_to_product(request, product["id"], category["id"], user, session)


@router.delete("/id/{product_id}/remove/{category_id}")
async def remove_category_from_product_by_id(request: Request,
                                             product_id: int,
                                             category_id: int,
                                             user: User = Depends(JWTBearer()),
                                             session: AsyncSession = Depends(get_async_session)):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden")

    statement = delete(ProductCategories).where(
        ProductCategories.category_id == category_id and
        ProductCategories.product_id == product_id)
    await session.execute(statement)
    await session.commit()

    return {"status": "success"}


@router.delete("/{product_slug}/remove/{category_slug}")
async def remove_category_to_product_by_slug(request: Request,
                                             product_slug: str,
                                             category_slug: str,
                                             user: User = Depends(JWTBearer()),
                                             session: AsyncSession = Depends(get_async_session)):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden")

    category = await get_category_by_slug(category_slug, session)
    product = await get_product_by_slug(product_slug, session)

    return await remove_category_from_product_by_id(request, product["id"], category["id"], user, session)
