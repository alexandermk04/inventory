import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ProductInformation(Base):
    __tablename__ = 'product_information'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    average_shelf_life_days: Mapped[int] = mapped_column()

class Product(Base):
    __tablename__ = 'products'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(ForeignKey('product_information.name'))
    expiration_date: Mapped[datetime.datetime] = mapped_column()