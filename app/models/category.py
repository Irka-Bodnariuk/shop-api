
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)

    parent_category_id = Column(
        Integer,
        ForeignKey("categories.category_id", ondelete="CASCADE"),
        nullable=True
    )

    seo_keyword = Column(String(255), nullable=True)
    meta_title = Column(String(255), nullable=True)
    meta_description = Column(String(500), nullable=True)
    meta_keyword = Column(String(500), nullable=True)
    image = Column(String(500), nullable=True)

    status = Column(Integer, default=1, nullable=False)

    date_added = Column(DateTime, server_default=func.now())
    date_modify = Column(DateTime, onupdate=func.now(), nullable=True)

    parent = relationship(
        "Category",
        remote_side=[category_id],
        back_populates="children"
    )

    children = relationship(
        "Category",
        back_populates="parent",
        cascade="all, delete-orphan"
    )

    product_links = relationship(
        "ProductCategory",
        back_populates="category",
        cascade="all, delete-orphan"
    )
