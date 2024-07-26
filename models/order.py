from sqlalchemy import Column, String, ForeignKey, Integer, Boolean

from models.base import Base
from models.product import Product
from models.user import User


class Order(Base):
    __tablename__ = "order"

    active = Column(Boolean, default=True)

    order_number = Column(String(length=128), nullable=False, unique=True)

    user_id = Column(ForeignKey(User.id), nullable=True)
    mobile_phone = Column(String(length=128), nullable=False)


class OrderProduct(Base):
    __tablename__ = "order_product"

    order_id = Column(ForeignKey(Order.id), nullable=False)
    product_id = Column(ForeignKey(Product.id), nullable=False)
    quantity = Column(Integer, nullable=False)



