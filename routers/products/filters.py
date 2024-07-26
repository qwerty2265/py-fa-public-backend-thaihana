from typing import List, Union

from fastapi import Query
from sqlalchemy.orm import aliased

from models.category import Category
from models.product import Product, ProductTags, ProductCategories
from sqlalchemy import func, or_, select, label

from models.tag import Tag


class ProductFilter:
    search_query: str
    min_price: float
    max_price: float
    tags: List[str]
    category: str

    def __init__(self, min_price: float, max_price: float, search: str, tags: List[str], category: str):
        self.min_price = min_price
        self.max_price = max_price
        self.search_query = search
        self.tags = tags
        self.category = category

    async def check(self, query):
        result = query.where(self.min_price <= Product.price) \
            .where(Product.price <= self.max_price) \
            .where(func.lower(Product.product_name).contains(self.search_query.lower()))

        # Дальше бога нет
        if self.category is not None:
            max_depth = 5

            category_hierarchy = select(Category.id, Category.parent_id, label("depth", 0)). \
                filter(Category.category_slug == self.category). \
                cte(name="category_hierarchy", recursive=True)

            category_hierarchy_alias = aliased(category_hierarchy, name="ch")

            category_hierarchy = category_hierarchy.union_all(
                select(
                    Category.id, Category.parent_id, category_hierarchy_alias.c.depth + 1
                ).select_from(
                    category_hierarchy_alias.join(Category, Category.parent_id == category_hierarchy_alias.c.id)
                ).where(category_hierarchy_alias.c.depth < max_depth)
            )

            result = result. \
                join(ProductCategories, Product.id == ProductCategories.product_id). \
                join(category_hierarchy, or_(
                    ProductCategories.category_id == category_hierarchy.c.id,
                    ProductCategories.category_id.in_(select(Category.id)
                                                  .where(category_hierarchy.c.id == ProductCategories.category_id))
                )). \
                distinct()

        if self.tags is not None:
            result = result.join(ProductTags, Product.id == ProductTags.product_id)\
                .join(Tag, Tag.id == ProductTags.tag_id)\
                .filter(Tag.tag_slug.in_(self.tags))\
                .group_by(Product.id).having(func.count(ProductTags.tag_id) == len(self.tags))

        return result


def create_product_filter(min_price: float = Query(default=0),
                          max_price: float = Query(default=999999),
                          search: str = Query(default=""),
                          category: str = Query(default=None),
                          tags: Union[List[str], None] = Query(default=None)):
    return ProductFilter(min_price, max_price, search, tags, category)
