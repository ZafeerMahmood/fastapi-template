from datetime import date
from typing import Optional, List
from enum import Enum

from pydantic import BaseModel


class RevenuePeriodEnum(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ANNUAL = "annual"


class RevenueBase(BaseModel):
    period_start: date
    period_end: date
    total_revenue: float
    total_sales: int
    average_order_value: float


class RevenueResponse(RevenueBase):
    period_label: str
    category_name: Optional[str] = None


class RevenuePeriodData(BaseModel):
    period_name: str
    data: List[RevenueResponse]
    total_revenue: float
    total_sales: int
    average_order_value: float


class RevenueCompareResponse(BaseModel):
    period1: RevenuePeriodData
    period2: RevenuePeriodData
    revenue_change: float
    revenue_change_percentage: float
    sales_change: int
    sales_change_percentage: float 