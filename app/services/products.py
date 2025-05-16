from typing import List, Optional

from sqlalchemy import select, update, delete as sqlalchemy_delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.models import Product, Category, Inventory
from app.schemas.products import ProductCreate, ProductUpdate, ProductResponse


class ProductsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_products(
        self, 
        category_id: Optional[int] = None, 
        name: Optional[str] = None,
        limit: int = 100, 
        offset: int = 0
    ) -> List[ProductResponse]:
        """
        Retrieve products with filtering options.
        """
        query = (
            select(Product)
            .options(
                joinedload(Product.category),
                joinedload(Product.inventory)
            )
        )

        # Apply filters
        if category_id:
            query = query.where(Product.category_id == category_id)
        if name:
            query = query.where(Product.name.ilike(f"%{name}%"))

        # Apply pagination
        query = query.order_by(Product.name).offset(offset).limit(limit)

        result = await self.db.execute(query)
        products = result.unique().scalars().all()

        return [self._format_product_response(product) for product in products]

    async def get_product_by_id(self, product_id: int) -> Optional[ProductResponse]:
        """
        Retrieve details of a specific product.
        """
        query = (
            select(Product)
            .options(
                joinedload(Product.category),
                joinedload(Product.inventory)
            )
            .where(Product.id == product_id)
        )

        result = await self.db.execute(query)
        product = result.unique().scalar_one_or_none()

        if not product:
            return None

        return self._format_product_response(product)

    async def create_product(self, product_data: ProductCreate) -> ProductResponse:
        """
        Register a new product.
        """
        # Create product
        product = Product(
            name=product_data.name,
            description=product_data.description,
            price=product_data.price,
            category_id=product_data.category_id,
            sku=product_data.sku,
            image_url=product_data.image_url
        )
        self.db.add(product)
        await self.db.flush()

        # Create initial inventory
        inventory = Inventory(
            product_id=product.id,
            quantity=0
        )
        self.db.add(inventory)

        await self.db.commit()
        await self.db.refresh(product)

        # Load related data
        query = (
            select(Product)
            .options(
                joinedload(Product.category),
                joinedload(Product.inventory)
            )
            .where(Product.id == product.id)
        )
        result = await self.db.execute(query)
        product = result.unique().scalar_one()

        return self._format_product_response(product)

    async def update_product(
        self, product_id: int, product_data: ProductUpdate
    ) -> Optional[ProductResponse]:
        """
        Update details of a specific product.
        """
        # Check if product exists
        query = (
            select(Product)
            .options(
                joinedload(Product.category),
                joinedload(Product.inventory)
            )
            .where(Product.id == product_id)
        )
        result = await self.db.execute(query)
        product = result.unique().scalar_one_or_none()

        if not product:
            return None

        # Update product data
        update_data = product_data.model_dump(exclude_unset=True)
        if update_data:
            stmt = (
                update(Product)
                .where(Product.id == product_id)
                .values(**update_data)
            )
            await self.db.execute(stmt)
            await self.db.commit()

            # Refresh product data
            result = await self.db.execute(query)
            product = result.unique().scalar_one()

        return self._format_product_response(product)

    async def delete_product(self, product_id: int) -> bool:
        """
        Delete a specific product.
        """
        # Check if product exists
        query = select(Product).where(Product.id == product_id)
        result = await self.db.execute(query)
        product = result.scalar_one_or_none()

        if not product:
            return False

        # Delete product
        stmt = sqlalchemy_delete(Product).where(Product.id == product_id)
        await self.db.execute(stmt)
        await self.db.commit()

        return True

    def _format_product_response(self, product: Product) -> ProductResponse:
        """
        Format a Product model into a ProductResponse schema.
        """
        inventory_quantity = product.inventory.quantity if product.inventory else 0

        return ProductResponse(
            id=product.id,
            name=product.name,
            description=product.description,
            price=product.price,
            category_id=product.category_id,
            category_name=product.category.name,
            sku=product.sku,
            image_url=product.image_url,
            created_at=product.created_at,
            updated_at=product.updated_at,
            inventory_quantity=inventory_quantity
        ) 