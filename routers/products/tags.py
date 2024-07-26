from datetime import datetime

from fastapi import APIRouter, Depends, Request, HTTPException, Body, Query
from fastapi.encoders import jsonable_encoder

from models.category import Category
from routers.auth.auth_bearer import JWTBearer
from utils import to_slug
from sqlalchemy import select, insert, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from config import LIMIT
from models.base import get_async_session
from models.product import ProductCategories, ProductTags, Product
from models.tag import Tag
from models.user import User
from routers.products.products import get_product_by_slug
from schemas.tag import TagCreate, TagUpdate

router = APIRouter(
    prefix="/tags",
    tags=['tag']
)


@router.get("/id/{tag_id}")
async def get_tag_by_id(tag_id: int, session: AsyncSession = Depends(get_async_session)):
    query = select(Tag).where(Tag.id == tag_id)
    result = await session.execute(query)

    return jsonable_encoder(result.first()[0])


@router.get("/{tag_slug}")
async def get_tag_by_slug(tag_slug: str, session: AsyncSession = Depends(get_async_session)):
    query = select(Tag).where(Tag.tag_slug == tag_slug)
    result = await session.execute(query)

    return jsonable_encoder(result.first()[0])


@router.get("")
async def get_tag_all(offset: int, limit: int, search_query: str = Query(default=""), session: AsyncSession = Depends(get_async_session)):
    if limit > LIMIT:
        raise HTTPException(status_code=403, detail="Forbidden")

    query = select(Tag).offset(offset).limit(limit).where(func.lower(Tag.tag_name).contains(search_query.lower()))
    result = await session.execute(query)

    list = []
    for key, tag in enumerate(result.fetchall()):
        list.append(jsonable_encoder(tag[0]))

    return list


@router.post("/create")
async def create_tag(request: Request,
                     new_tag: TagCreate,
                     user: User = Depends(JWTBearer()),
                     session: AsyncSession = Depends(get_async_session)):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden")

    slug = to_slug(f"{new_tag.tag_name}")

    query = select(Tag).where(Tag.tag_slug == slug)
    result = (await session.execute(query)).fetchall()
    if len(result) != 0:
        return {"status": "failure", "detail": "slug is already exists"}

    statement = insert(Tag).values(**new_tag.dict(), tag_slug=slug)
    await session.execute(statement)
    await session.commit()

    return {"status": "success"}


@router.put("/id/{tag_id}")
async def update_tag_by_id(request: Request,
                           tag_id: int,
                           updated_tag: TagUpdate,
                           user: User = Depends(JWTBearer()),
                           session: AsyncSession = Depends(get_async_session)):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden")

    query = select(Tag).where(Tag.id == tag_id)
    result = (await session.execute(query)).first()

    if result is None:
        raise HTTPException(status_code=400, detail="Tag doesn't exist!")

    override_dict = jsonable_encoder(result[0])
    new_dict = updated_tag.dict()

    for key in override_dict:
        if key in new_dict and new_dict[key] is not None:
            override_dict[key] = new_dict[key]

    override_dict.pop("modified_at")
    override_dict.pop("created_at")

    statement = update(Tag).where(Tag.id == tag_id).values(**override_dict,
                                                           created_at=result[0].created_at,
                                                           modified_at=datetime.utcnow())
    await session.execute(statement)
    await session.commit()

    return {"status": "success"}


@router.put("/{tag_slug}")
async def update_tag_by_slug(request: Request,
                             tag_slug: int,
                             updated_product=Body(..., embed=True),
                             user: User = Depends(JWTBearer()),
                             session: AsyncSession = Depends(get_async_session)):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden")

    tag = await get_tag_by_slug(tag_slug, session)

    return await update_tag_by_id(request, tag["id"], updated_product, user, session)


@router.post("/id/{product_id}/add/{tag_id}")
async def add_tag_to_product_by_id(request: Request,
                                   product_id: int,
                                   tag_id: int,
                                   user: User = Depends(JWTBearer()),
                                   session: AsyncSession = Depends(get_async_session)):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden")

    statement = insert(ProductTags).values({
        "tag_id": tag_id,
        "product_id": product_id
    })
    await session.execute(statement)
    await session.commit()

    return {"status": "success"}


@router.post("/{product_slug}/add/{tag_slug}")
async def add_tag_to_product_by_slug(request: Request,
                                     product_slug: str,
                                     tag_slug: str,
                                     user: User = Depends(JWTBearer()),
                                     session: AsyncSession = Depends(get_async_session)):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden")

    tag = await get_tag_by_slug(tag_slug, session)
    product = await get_product_by_slug(product_slug, session)

    return await add_tag_to_product_by_id(request, product["id"], tag["id"], user, session)


@router.delete("/id/{product_id}/remove/{tag_id}")
async def remove_tag_from_product_by_id(request: Request,
                                        product_id: int,
                                        tag_id: int,
                                        user: User = Depends(JWTBearer()),
                                        session: AsyncSession = Depends(get_async_session)):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden")

    statement = delete(ProductCategories).where(
        ProductCategories.category_id == tag_id and
        ProductCategories.product_id == product_id)
    await session.execute(statement)
    await session.commit()

    return {"status": "success"}


@router.delete("/{product_slug}/add/{tag_slug}")
async def remove_tag_to_product_by_slug(request: Request,
                                        product_slug: str,
                                        tag_slug: str,
                                        user: User = Depends(JWTBearer()),
                                        session: AsyncSession = Depends(get_async_session)):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden")

    tag = await get_tag_by_slug(tag_slug, session)
    product = await get_product_by_slug(product_slug, session)

    return await remove_tag_from_product_by_id(request, product["id"], tag["id"], user, session)


@router.get("/in/{category_slug}")
async def get_tags_of_category(
        category_slug: str,
        session: AsyncSession = Depends(JWTBearer())):
    query = select(Tag) \
        .distinct() \
        .join(ProductTags, Tag.id == ProductTags.tag_id) \
        .join(Product, Product.id == ProductTags.product_id) \
        .join(ProductCategories, Product.id == ProductCategories.product_id) \
        .join(Category, Category.id == ProductCategories.category_id) \
        .filter(Category.category_slug == category_slug) \
        .distinct()
    result = await session.execute(query)

    list = []
    for key, tag in enumerate(result.fetchall()):
        list.append(jsonable_encoder(tag[0]))

    return list
