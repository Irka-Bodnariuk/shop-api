
from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base

from sqlalchemy.orm import relationship


class ProductImage(Base):
    __tablename__ = "product_image"

    product_image_id = Column(Integer, primary_key=True, index=True)

    product_id = Column(
        Integer,
        ForeignKey("products.product_id", ondelete="CASCADE"),
        nullable=False
    )

    image = Column(String(500), nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    
    product = relationship("Product", back_populates="images")
