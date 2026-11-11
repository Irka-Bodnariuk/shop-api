
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Store(Base):
    __tablename__ = "stores"

    store_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)

    product_links = relationship(
        "ProductStore",
        back_populates="store",
        cascade="all, delete-orphan"
    )
