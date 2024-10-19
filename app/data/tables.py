import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class CategoryProductAssociation(Base):
    __tablename__ = 'category_product_association'
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'), primary_key=True)
    product_information_id: Mapped[int] = mapped_column(ForeignKey('product_information.id'), primary_key=True)

class Category(Base):
    __tablename__ = 'categories'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()

class ProductInformation(Base):
    __tablename__ = 'product_information'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    average_shelf_life_days: Mapped[int | None] = mapped_column()

class Product(Base):
    __tablename__ = 'products'
    id: Mapped[int] = mapped_column(primary_key=True)
    product_information_id: Mapped[int] = mapped_column(ForeignKey('product_information.id'))
    purchase_date: Mapped[datetime.datetime] = mapped_column()
    expiration_date: Mapped[datetime.datetime | None] = mapped_column()