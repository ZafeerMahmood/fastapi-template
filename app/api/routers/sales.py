from typing import List, Optional
from datetime import date

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.sales import SaleResponse, SaleFilter
from app.services.sales import SalesService

router = APIRouter()


@router.get("/", response_model=List[SaleResponse])
async def get_sales(
    start_date: Optional[date] = Query(None, description="Filter sales from this date"),
    end_date: Optional[date] = Query(None, description="Filter sales until this date"),
    product_id: Optional[int] = Query(None, description="Filter by product ID"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of sales to return"),
    offset: int = Query(0, ge=0, description="Number of sales to skip"),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve sales with filtering options.
    """
    filters = SaleFilter(
        start_date=start_date,
        end_date=end_date,
        product_id=product_id,
        category_id=category_id,
    )
    return await SalesService(db).get_sales(filters, limit, offset)


@router.get("/{sale_id}", response_model=SaleResponse)
async def get_sale(
    sale_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve details of a specific sale.
    """
    sale = await SalesService(db).get_sale_by_id(sale_id)
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sale with ID {sale_id} not found",
        )
    return sale 