
from pydantic import BaseModel, ConfigDict, Field


class ProductImageCreate(BaseModel):
    image: str = Field(min_length=1, max_length=500)
    sort_order: int = Field(default=0, ge=0)


class ProductImageUpdate(BaseModel):
    sort_order: int = Field(ge=0)


class ProductImageResponse(BaseModel):
    product_image_id: int
    product_id: int
    image: str
    sort_order: int

    model_config = ConfigDict(from_attributes=True)
