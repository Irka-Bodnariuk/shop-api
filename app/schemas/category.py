
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    parent_category_id: int | None = Field(default=None, ge=0)
    seo_keyword: str | None = None
    meta_title: str | None = None
    meta_description: str | None = None
    meta_keyword: str | None = None
    image: str | None = None
    status: int = Field(default=1, ge=0, le=1)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    parent_category_id: int | None = Field(default=None, ge=0)
    seo_keyword: str | None = None
    meta_title: str | None = None
    meta_description: str | None = None
    meta_keyword: str | None = None
    image: str | None = None
    status: int | None = Field(default=None, ge=0, le=1)


class CategoryResponse(CategoryBase):
    category_id: int
    date_added: datetime | None = None
    date_modify: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class CategoryListItem(BaseModel):
    category_id: int
    name: str
    category_path: str
    status: int
    status_label: str

    model_config = ConfigDict(from_attributes=True)
