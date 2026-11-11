
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class ProductCategory(Base):
    __tablename__ = "product_category"

    product_category_id = Column(Integer, primary_key=True, index=True)

    product_id = Column(
        Integer,
        ForeignKey("products.product_id", ondelete="CASCADE"),
        nullable=False
    )

    category_id = Column(
        Integer,
        ForeignKey("categories.category_id", ondelete="CASCADE"),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "category_id",
            name="uq_product_category"
        ),
    )

    product = relationship("Product", back_populates="category_links")
    category = relationship("Category", back_populates="product_links")
