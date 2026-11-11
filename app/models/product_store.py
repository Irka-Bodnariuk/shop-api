
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class ProductStore(Base):
    __tablename__ = "product_store"

    product_store_id = Column(Integer, primary_key=True, index=True)

    product_id = Column(
        Integer,
        ForeignKey("products.product_id", ondelete="CASCADE"),
        nullable=False
    )

    store_id = Column(
        Integer,
        ForeignKey("stores.store_id", ondelete="CASCADE"),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "store_id",
            name="uq_product_store"
        ),
    )

    product = relationship("Product", back_populates="store_links")
    store = relationship("Store", back_populates="product_links")
