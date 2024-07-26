from sqlalchemy import Column, String, Boolean, ForeignKey

from models.base import Base
from models.heading import Heading


class Category(Base):
    __tablename__ = "category"

    visible = Column(Boolean, default=True)

    heading_id = Column(ForeignKey(Heading.id), nullable=False)
    parent_id = Column(ForeignKey(__tablename__ + ".id"), nullable=False)

    category_name = Column(String(length=128), nullable=False)
    category_slug = Column(String(length=128), nullable=False, unique=True)
    image_path = Column(String, nullable=False)

    category_description = Column(String, nullable=False)





