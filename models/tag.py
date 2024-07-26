from sqlalchemy import Column, String

from models.base import Base


class Tag(Base):
    __tablename__ = "tag"

    tag_name = Column(String(length=128), nullable=False)
    tag_slug = Column(String(length=128), nullable=False, unique=True)
    image_path = Column(String, nullable=False)






