from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class InventoryBase(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=0)


class InventoryUpdate(BaseModel):
    quantity: int = Field(..., ge=0)
    reason: Optional[str] = None


class InventoryInDBBase(InventoryBase):
    id: int
    last_updated: datetime

    model_config = {"from_attributes": True}


class InventoryResponse(InventoryInDBBase):
    product_name: str
    product_sku: str
    product_price: float
    category_name: str


class InventoryHistoryBase(BaseModel):
    inventory_id: int
    quantity_change: int
    previous_quantity: int
    new_quantity: int
    reason: Optional[str] = None
    timestamp: datetime


class InventoryHistoryCreate(InventoryHistoryBase):
    pass


class InventoryHistoryInDBBase(InventoryHistoryBase):
    id: int

    model_config = {"from_attributes": True}


class InventoryHistoryResponse(InventoryHistoryInDBBase):
    product_name: str 