from typing import List, Optional

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.inventory import InventoryResponse, InventoryUpdate
from app.services.inventory import InventoryService

router = APIRouter()


@router.get("/", response_model=List[InventoryResponse])
async def get_inventory(
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve current inventory status.
    """
    return await InventoryService(db).get_inventory(category_id, limit, offset)


@router.get("/low-stock", response_model=List[InventoryResponse])
async def get_low_stock_inventory(
    threshold: int = Query(10, ge=1, description="Low stock threshold"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve products with low stock.
    """
    return await InventoryService(db).get_low_stock_inventory(threshold, category_id)


@router.put("/{product_id}", response_model=InventoryResponse)
async def update_inventory(
    product_id: int,
    inventory_data: InventoryUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update inventory level for a product.
    """
    inventory = await InventoryService(db).update_inventory(product_id, inventory_data)
    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found in inventory",
        )
    return inventory 