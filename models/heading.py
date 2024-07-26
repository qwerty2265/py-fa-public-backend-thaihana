from sqlalchemy import Column, String, Boolean

from models.base import Base


class Heading(Base):
    __tablename__ = "heading"

    visible = Column(Boolean, default=True)

    heading_name = Column(String(length=128), nullable=False)
    heading_slug = Column(String(length=128), nullable=False, unique=True)
    image_path = Column(String, nullable=False)

    heading_description = Column(String, nullable=False)





