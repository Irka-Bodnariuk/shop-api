
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.manufacturer import ManufacturerResponse
from app.schemas.product_image import ProductImageCreate
from app.schemas.product_attribute import ProductAttributeCreate


class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = None
    seo_keyword: str | None = None
    meta_title: str | None = None
    meta_description: str | None = None
    meta_keyword: str | None = None
    image: str | None = None
    status: int = Field(default=0, ge=0, le=1)
    price: Decimal | None = Field(default=None, gt=0)
    model: str | None = None
    manufacturer_id: int | None = None


class ProductCreate(ProductBase):
    category_ids: list[int] = Field(default_factory=list)
    images: list[ProductImageCreate] = Field(default_factory=list)
    attributes: list[ProductAttributeCreate] = Field(default_factory=list)


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = None
    seo_keyword: str | None = None
    meta_title: str | None = None
    meta_description: str | None = None
    meta_keyword: str | None = None
    image: str | None = None
    status: int | None = Field(default=None, ge=0, le=1)
    price: Decimal | None = Field(default=None, gt=0)
    model: str | None = None
    manufacturer_id: int | None = None
    category_ids: list[int] | None = None


class ProductCategoryInfo(BaseModel):
    category_id: int
    name: str
    category_path: str


class ProductImageInfo(BaseModel):
    product_image_id: int
    image: str
    sort_order: int

    model_config = ConfigDict(from_attributes=True)


class ManufacturerInfo(BaseModel):
    manufacturer_id: int
    name: str
    description: str | None = None


class ProductAttributeInfo(BaseModel):
    product_attribute_id: int
    group_name: str
    name: str
    value: str
    sort_order: int

    model_config = ConfigDict(from_attributes=True)

class ProductStoreInfo(BaseModel):
    product_store_id: int
    store_id: int
    store_name: str


class ProductResponse(ProductBase):
    product_id: int
    rating: float = 0
    viewed: int = 0
    date_added: datetime | None = None
    date_modify: datetime | None = None

    categories: list[ProductCategoryInfo] = Field(default_factory=list)
    images: list[ProductImageInfo] = Field(default_factory=list)
    attributes: list[ProductAttributeInfo] = Field(default_factory=list)
    manufacturer: ManufacturerInfo | None = None
    stores: list[ProductStoreInfo] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ProductListItem(BaseModel):
    product_id: int
    name: str
    category_path: str
    price: Decimal | None
    status: int
