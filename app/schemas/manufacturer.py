
from pydantic import BaseModel, ConfigDict


class ManufacturerResponse(BaseModel):
    manufacturer_id: int
    name: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)
