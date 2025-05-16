from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.models import Sale, SaleItem, Product, Customer, Category
from app.schemas.sales import SaleResponse, SaleCreate, SaleFilter, SaleItemResponse


class SalesService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_sales(
        self, filters: SaleFilter, limit: int = 100, offset: int = 0
    ) -> List[SaleResponse]:
        """
        Retrieve sales with filtering options.
        """
        query = (
            select(Sale)
            .options(
                joinedload(Sale.customer),
                joinedload(Sale.items).joinedload(SaleItem.product).joinedload(Product.category)
            )
        )

        if filters.start_date:
            query = query.where(Sale.sale_date >= filters.start_date)
        if filters.end_date:
            query = query.where(Sale.sale_date <= filters.end_date)
        if filters.product_id:
            query = query.join(Sale.items).where(SaleItem.product_id == filters.product_id)
        if filters.category_id:
            query = query.join(Sale.items).join(SaleItem.product).join(Product.category).where(
                Category.id == filters.category_id
            )

        query = query.order_by(Sale.sale_date.desc()).offset(offset).limit(limit)

        result = await self.db.execute(query)
        sales = result.unique().scalars().all()

        return [await self._format_sale_response(sale) for sale in sales]

    async def get_sale_by_id(self, sale_id: int) -> Optional[SaleResponse]:
        """
        Retrieve details of a specific sale.
        """
        query = (
            select(Sale)
            .options(
                joinedload(Sale.customer),
                joinedload(Sale.items).joinedload(SaleItem.product).joinedload(Product.category)
            )
            .where(Sale.id == sale_id)
        )

        result = await self.db.execute(query)
        sale = result.unique().scalar_one_or_none()

        if not sale:
            return None

        return await self._format_sale_response(sale)

    async def create_sale(self, sale_data: SaleCreate) -> SaleResponse:
        """
        Create a new sale with items.
        """
        sale = Sale(
            customer_id=sale_data.customer_id,
            payment_method=sale_data.payment_method,
            status=sale_data.status,
            total_amount=sum(item.unit_price * item.quantity for item in sale_data.items)
        )
        self.db.add(sale)
        await self.db.flush()

        for item_data in sale_data.items:
            sale_item = SaleItem(
                sale_id=sale.id,
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                unit_price=item_data.unit_price,
                subtotal=item_data.unit_price * item_data.quantity
            )
            self.db.add(sale_item)

        await self.db.commit()
        await self.db.refresh(sale)

        return await self.get_sale_by_id(sale.id)

    async def _format_sale_response(self, sale: Sale) -> SaleResponse:
        """
        Format a Sale model into a SaleResponse schema.
        """
        sale_items = []
        for item in sale.items:
            sale_item = SaleItemResponse(
                id=item.id,
                sale_id=item.sale_id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                subtotal=item.subtotal,
                product_name=item.product.name,
                product_sku=item.product.sku
            )
            sale_items.append(sale_item)

        return SaleResponse(
            id=sale.id,
            customer_id=sale.customer_id,
            customer_name=sale.customer.name if sale.customer else None,
            payment_method=sale.payment_method,
            status=sale.status,
            total_amount=sale.total_amount,
            sale_date=sale.sale_date,
            items=sale_items
        ) 