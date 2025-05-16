from datetime import datetime, date
from typing import Optional, List

from pydantic import BaseModel, Field, model_validator


class SaleItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)


class SaleItemCreate(SaleItemBase):
    pass


class SaleItemInDBBase(SaleItemBase):
    id: int
    sale_id: int
    subtotal: float

    model_config = {"from_attributes": True}


class SaleItemResponse(SaleItemInDBBase):
    product_name: str
    product_sku: str


class SaleBase(BaseModel):
    customer_id: Optional[int] = None
    payment_method: Optional[str] = None
    status: str = "completed"


class SaleCreate(SaleBase):
    items: List[SaleItemCreate]

    @model_validator(mode='after')
    def calculate_total(self):
        values = self.__dict__
        items = values.get("items", [])
        if items:
            values["total_amount"] = sum(item.unit_price * item.quantity for item in items)
        return self


class SaleInDBBase(SaleBase):
    id: int
    total_amount: float
    sale_date: datetime

    model_config = {"from_attributes": True}


class SaleResponse(SaleInDBBase):
    items: List[SaleItemResponse]
    customer_name: Optional[str] = None


class SaleFilter(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    product_id: Optional[int] = None
    category_id: Optional[int] = None 