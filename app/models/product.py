
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base

from sqlalchemy import ForeignKey


class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, index=True)

    name = Column(String(150), nullable=False)
    description = Column(String(500), nullable=True)

    seo_keyword = Column(String(255), nullable=True)
    meta_title = Column(String(255), nullable=True)
    meta_description = Column(String(500), nullable=True)
    meta_keyword = Column(String(500), nullable=True)

    image = Column(String(500), nullable=True)

    status = Column(Integer, default=0, nullable=False)

    date_added = Column(DateTime, server_default=func.now())
    date_modify = Column(DateTime, onupdate=func.now(), nullable=True)

    price = Column(Numeric(10, 2), nullable=True)
    model = Column(String(100), nullable=True)

    manufacturer_id = Column(
        Integer,
        ForeignKey("manufacturers.manufacturer_id"),
        nullable=True
    )

    manufacturer = relationship("Manufacturer", back_populates="products")

    rating = Column(Float, default=0)
    viewed = Column(Integer, default=0)

    category_links = relationship(
        "ProductCategory",
        back_populates="product",
        cascade="all, delete-orphan"
    )
    
    images = relationship(
        "ProductImage",
        back_populates="product",
        cascade="all, delete-orphan"
    )

    attributes = relationship(
        "ProductAttribute",
        back_populates="product",
        cascade="all, delete-orphan"
    )

    store_links = relationship(
    "ProductStore",
    back_populates="product",
    cascade="all, delete-orphan"
)