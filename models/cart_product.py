from sqlalchemy import Column, ForeignKey, Integer

from models.base import Base
from models.product import Product
from models.user import User


class CartProduct(Base):
    __tablename__ = "cart_product"

    user_id = Column(ForeignKey(User.id), nullable=False)
    product_id = Column(ForeignKey(Product.id), nullable=False)
    quantity = Column(Integer, nullable=False)






