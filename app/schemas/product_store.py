
from pydantic import BaseModel, ConfigDict


class ProductStoreResponse(BaseModel):
    product_store_id: int
    product_id: int
    store_id: int
    store_name: str

    model_config = ConfigDict(from_attributes=True)
