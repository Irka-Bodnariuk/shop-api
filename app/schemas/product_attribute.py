
from pydantic import BaseModel, ConfigDict, Field


class ProductAttributeCreate(BaseModel):
    group_name: str | None = Field(default=None, max_length=150)
    name: str = Field(min_length=1, max_length=150)
    value: str | None = Field(default=None, max_length=500)
    sort_order: int = Field(default=0, ge=0)


class ProductAttributeUpdate(BaseModel):
    group_name: str | None = Field(default=None, max_length=150)
    name: str | None = Field(default=None, min_length=1, max_length=150)
    value: str | None = Field(default=None, max_length=500)
    sort_order: int | None = Field(default=None, ge=0)


class ProductAttributeResponse(BaseModel):
    product_attribute_id: int
    product_id: int
    group_name: str | None
    name: str
    value: str | None
    sort_order: int

    model_config = ConfigDict(from_attributes=True)
