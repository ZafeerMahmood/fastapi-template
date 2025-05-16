from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator, Field


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    category_id: int
    sku: str = Field(..., min_length=3, max_length=50)
    image_url: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    category_id: Optional[int] = None
    sku: Optional[str] = Field(None, min_length=3, max_length=50)
    image_url: Optional[str] = None


class ProductInDBBase(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductResponse(ProductInDBBase):
    category_name: str
    inventory_quantity: Optional[int] = 0 