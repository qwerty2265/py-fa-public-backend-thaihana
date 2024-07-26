from sqlalchemy import Column, String, Integer, Numeric, Boolean, ForeignKey

from models.base import Base

from models.category import Category
from models.tag import Tag


class Product(Base):
    __tablename__ = "product"

    visible = Column(Boolean, default=True)

    product_name = Column(String(length=128), nullable=False)
    product_slug = Column(String(length=128), nullable=False, unique=True)
    image_path = Column(String, nullable=False)

    short_description = Column(String(256), nullable=False)
    product_description = Column(String, nullable=False)

    price = Column(Numeric, nullable=False)
    quantity = Column(Integer, nullable=False)
    measure = Column(String, default="gr", nullable=False)
    product_weight = Column(Numeric, nullable=False)


class ProductCategories(Base):
    __tablename__ = "product_categories"

    category_id = Column(ForeignKey(Category.id), nullable=False)
    product_id = Column(ForeignKey(Product.id), nullable=False)


class ProductTags(Base):
    __tablename__ = "product_tags"

    tag_id = Column(ForeignKey(Tag.id), nullable=False)
    product_id = Column(ForeignKey(Product.id), nullable=False)