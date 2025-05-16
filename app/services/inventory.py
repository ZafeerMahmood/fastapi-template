from typing import List, Optional, Union

from fastapi import HTTPException, status
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.models.models import Inventory, Product, Category, InventoryHistory
from app.schemas.inventory import InventoryUpdate, InventoryResponse


class InventoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_inventory(
        self, category_id: Optional[int] = None, limit: int = 100, offset: int = 0
    ) -> List[InventoryResponse]:
        """
        Retrieve inventory with optional filtering by category.
        """
        query = (
            select(Inventory)
            .join(Inventory.product)
            .join(Product.category)
            .options(joinedload(Inventory.product).joinedload(Product.category))
        )

        if category_id:
            query = query.where(Product.category_id == category_id)

        result = await self.db.execute(
            query.order_by(Inventory.quantity).limit(limit).offset(offset)
        )
        inventory_items = result.unique().scalars().all()

        return [
            InventoryResponse(
                id=item.id,
                product_id=item.product_id,
                quantity=item.quantity,
                last_updated=item.last_updated,
                product_name=item.product.name,
                product_sku=item.product.sku,
                product_price=item.product.price,
                category_name=item.product.category.name,
            )
            for item in inventory_items
        ]

    async def get_low_stock_inventory(
        self, threshold: int = 10, category_id: Optional[int] = None
    ) -> List[InventoryResponse]:
        """
        Retrieve products with stock below the specified threshold.
        """
        query = (
            select(Inventory)
            .join(Inventory.product)
            .join(Product.category)
            .options(joinedload(Inventory.product).joinedload(Product.category))
            .where(Inventory.quantity <= threshold)
        )

        if category_id:
            query = query.where(Product.category_id == category_id)

        result = await self.db.execute(query.order_by(Inventory.quantity))
        inventory_items = result.unique().scalars().all()

        return [
            InventoryResponse(
                id=item.id,
                product_id=item.product_id,
                quantity=item.quantity,
                last_updated=item.last_updated,
                product_name=item.product.name,
                product_sku=item.product.sku,
                product_price=item.product.price,
                category_name=item.product.category.name,
            )
            for item in inventory_items
        ]

    async def update_inventory(
        self, product_id: int, inventory_data: InventoryUpdate
    ) -> Optional[InventoryResponse]:
        """
        Update inventory quantity for a product and log the change.
        """
        result = await self.db.execute(
            select(Inventory)
            .join(Inventory.product)
            .join(Product.category)
            .options(joinedload(Inventory.product).joinedload(Product.category))
            .where(Inventory.product_id == product_id)
        )
        inventory = result.unique().scalar_one_or_none()

        if not inventory:
            return None

        # Store previous quantity before update
        previous_quantity = inventory.quantity
        
        # Update inventory
        inventory.quantity = inventory_data.quantity
        
        # Create inventory history entry
        history_entry = InventoryHistory(
            inventory_id=inventory.id,
            quantity_change=inventory_data.quantity - previous_quantity,
            previous_quantity=previous_quantity,
            new_quantity=inventory_data.quantity,
            reason=inventory_data.reason
        )
        
        self.db.add(history_entry)
        await self.db.flush()

        return InventoryResponse(
            id=inventory.id,
            product_id=inventory.product_id,
            quantity=inventory.quantity,
            last_updated=inventory.last_updated,
            product_name=inventory.product.name,
            product_sku=inventory.product.sku,
            product_price=inventory.product.price,
            category_name=inventory.product.category.name,
        ) 