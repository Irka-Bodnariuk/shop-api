
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class ProductAttribute(Base):
    __tablename__ = "product_attribute"

    product_attribute_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    product_id = Column(
        Integer,
        ForeignKey("products.product_id", ondelete="CASCADE"),
        nullable=False
    )

    group_name = Column(String(150), nullable=True)
    name = Column(String(150), nullable=False)
    value = Column(String(500), nullable=True)
    sort_order = Column(Integer, default=0, nullable=False)

    product = relationship("Product", back_populates="attributes")
