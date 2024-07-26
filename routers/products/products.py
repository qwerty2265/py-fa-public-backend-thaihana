import datetime

from fastapi import APIRouter, Depends, Request, HTTPException, Body
from fastapi.encoders import jsonable_encoder

from models.category import Category
from models.tag import Tag
from routers.auth.auth_bearer import JWTBearer
from utils import to_slug
from sqlalchemy import select, insert, update, text, func
from sqlalchemy.ext.asyncio import AsyncSession

from config import LIMIT
from models.base import get_async_session
from models.product import Product, ProductCategories, ProductTags
from models.user import User
from routers.products.filters import create_product_filter, ProductFilter
from schemas.product import ProductCreate, ProductUpdate

router = APIRouter(
    prefix="/products",
    tags=['products']
)


@router.get("/id/{product_id}")
async def get_product_by_id(product_id: int, session: AsyncSession = Depends(get_async_session)):
    query = select(Product).where(Product.visible and Product.id == product_id)
    result = await session.execute(query)
    end = result.first()

    if end is None:
        return None
    return jsonable_encoder(end[0])


@router.get("/{product_slug}")
async def get_product_by_slug(product_slug: str, session: AsyncSession = Depends(get_async_session)):
    query = select(Product).where(Product.visible and Product.product_slug == product_slug)
    result = await session.execute(query)
    end = result.first()

    if end is None:
        return None
    return jsonable_encoder(end[0])


@router.get("")
async def get_product_all(offset: int, limit: int, filter: ProductFilter = Depends(create_product_filter),
                          session: AsyncSession = Depends(get_async_session)):
    if limit > LIMIT:
        raise HTTPException(status_code=403, detail="Forbidden")

    query = select(Product).where(Product.visible).offset(offset).limit(limit)
    query = await filter.check(query)
    result = await session.execute(query)

    list = []
    for key, product in enumerate(result.fetchall()):
        list.append(jsonable_encoder(product[0]))

    return list


@router.get("/count/")
async def count_product_all(filter: ProductFilter = Depends(create_product_filter),
                            session: AsyncSession = Depends(get_async_session)):
    query = select(Product).where(Product.visible)
    query = await filter.check(query)

    result = await session.execute(query)

    return len(result.fetchall())


@router.get("/price_range/")
async def get_price_range(filter: ProductFilter = Depends(create_product_filter),
                          session: AsyncSession = Depends(get_async_session)):
    query_min = select(func.min(Product.price)).where(Product.visible)
    query_min = await filter.check(query_min)

    query_max = select(func.max(Product.price)).where(Product.visible)
    query_max = await filter.check(query_max)

    result_min = (await session.execute(query_min)).scalar()
    result_max = (await session.execute(query_max)).scalar()

    return {
        "min_price": result_min,
        "max_price": result_max
    }


@router.get("/{category_id}/all/{offset}")
async def get_category_product_all(category_id: int, offset: int, limit: int,
                                   session: AsyncSession = Depends(get_async_session)):
    if limit > LIMIT:
        raise HTTPException(status_code=403, detail="Forbidden")

    query = select(ProductCategories).where(ProductCategories.category_id == category_id).offset(offset).limit(limit)
    result = await session.execute(query)

    list = []
    for key, productCategory in enumerate(result.fetchall()):
        list.append(await get_product_by_id(productCategory[0].product_id, session))

    return list


@router.get("/{tag_id}/all/{offset}")
async def get_tag_product_all(tag_id: int, offset: int, limit: int, session: AsyncSession = Depends(get_async_session)):
    if limit > LIMIT:
        raise HTTPException(status_code=403, detail="Forbidden")

    query = select(ProductTags).where(ProductTags.tag_id == tag_id).offset(offset).limit(limit)
    result = await session.execute(query)

    list = []
    for key, productTag in enumerate(result.fetchall()):
        list.append(await get_product_by_id(productTag[0].product_id, session))

    return list


@router.get("/id/{product_id}/categories")
async def get_categories_of_product_by_id(product_id: int, session: AsyncSession = Depends(get_async_session)):
    query = select(Category).join(ProductCategories).filter(ProductCategories.product_id == product_id)
    result = await session.execute(query)
    categories = result.fetchall()

    list = []
    for key, category in enumerate(categories):
        list.append(jsonable_encoder(category[0]))

    return list


@router.get("/{product_slug}/categories")
async def get_categories_of_product_by_slug(product_slug: str, session: AsyncSession = Depends(get_async_session)):
    product = await get_product_by_slug(product_slug, session)
    if product is None:
        return None

    return await get_categories_of_product_by_id(product["id"], session)


@router.get("/id/{product_id}/tags")
async def get_tags_of_product_by_id(product_id: int, session: AsyncSession = Depends(get_async_session)):
    query = select(Tag).join(ProductTags).filter(ProductTags.product_id == product_id)
    result = await session.execute(query)
    categories = result.fetchall()

    list = []
    for key, tag in enumerate(categories):
        list.append(jsonable_encoder(tag[0]))

    return list


@router.get("/{product_slug}/tags")
async def get_tags_of_product_by_slug(product_slug: str, session: AsyncSession = Depends(get_async_session)):
    product = await get_product_by_slug(product_slug, session)
    if product is None:
        return None

    return await get_tags_of_product_by_id(product["id"], session)


@router.post("/create")
async def create_product(request: Request,
                         new_product: ProductCreate,
                         user: User = Depends(JWTBearer()),
                         session: AsyncSession = Depends(get_async_session)):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden")

    slug = to_slug(f"{new_product.product_name} {new_product.product_weight}")

    query = select(Product).where(Product.product_slug == slug)
    result = (await session.execute(query)).fetchall()
    if len(result) != 0:
        return {"status": "failure", "detail": "slug is already exists"}

    statement = insert(Product).values(**new_product.dict(), product_slug=slug)
    await session.execute(statement)
    await session.commit()

    return {"status": "success"}


@router.put("/id/{product_id}")
async def update_product_by_id(request: Request,
                               product_id: int,
                               updated_product: ProductUpdate,
                               user: User = Depends(JWTBearer()),
                               session: AsyncSession = Depends(get_async_session)):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden")

    query = select(Product).where(Product.id == product_id)
    result = (await session.execute(query)).first()

    if result is None:
        raise HTTPException(status_code=400, detail="Product doesn't exist!")

    override_dict = jsonable_encoder(result[0])
    new_dict = updated_product.dict()

    for key in override_dict:
        if key in new_dict and new_dict[key] is not None:
            override_dict[key] = new_dict[key]

    override_dict.pop("modified_at")
    override_dict.pop("created_at")

    statement = update(Product).where(Product.id == product_id).values(**override_dict, created_at=result[0].created_at, modified_at=datetime.datetime.utcnow())
    await session.execute(statement)
    await session.commit()

    return {"status": "success"}


@router.put("/{product_slug}")
async def update_product_by_slug(request: Request,
                                 product_slug: str,
                                 updated_product=Body(..., embed=True),
                                 user: User = Depends(JWTBearer()),
                                 session: AsyncSession = Depends(get_async_session)):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden")

    product = await get_product_by_slug(product_slug, session)
    if product is None:
        return {"status": "failure"}

    return await update_product_by_id(request, product["id"], updated_product, user, session)
