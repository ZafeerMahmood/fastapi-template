from typing import List, Optional
from datetime import date, datetime, timedelta
import calendar

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Sale, SaleItem, Product, Category
from app.schemas.revenue import (
    RevenueResponse, RevenuePeriodEnum, RevenuePeriodData, RevenueCompareResponse
)


class RevenueService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_revenue_by_period(
        self, 
        period: RevenuePeriodEnum, 
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        category_id: Optional[int] = None
    ) -> List[RevenueResponse]:
        """
        Get revenue statistics by period (daily, weekly, monthly, or annual).
        """
        end_date = end_date or date.today()
        if start_date is None:
            if period == RevenuePeriodEnum.DAILY:
                start_date = end_date - timedelta(days=30)
            elif period == RevenuePeriodEnum.WEEKLY:
                start_date = end_date - timedelta(weeks=12)
            elif period == RevenuePeriodEnum.MONTHLY:
                start_date = end_date.replace(month=1 if end_date.month < 13 else 13 - 12)
            else:
                start_date = end_date.replace(year=end_date.year - 5)

        query = select(Sale)
        
        if category_id is not None:
            query = (
                query.join(Sale.items)
                .join(SaleItem.product)
                .join(Product.category)
                .where(Category.id == category_id)
            )
        
        query = query.where(
            and_(
                Sale.sale_date >= datetime.combine(start_date, datetime.min.time()),
                Sale.sale_date <= datetime.combine(end_date, datetime.max.time())
            )
        )
        
        result = await self.db.execute(query)
        sales = result.scalars().all()
        
        if period == RevenuePeriodEnum.DAILY:
            return await self._group_revenue_by_day(sales, start_date, end_date, category_id)
        elif period == RevenuePeriodEnum.WEEKLY:
            return await self._group_revenue_by_week(sales, start_date, end_date, category_id)
        elif period == RevenuePeriodEnum.MONTHLY:
            return await self._group_revenue_by_month(sales, start_date, end_date, category_id)
        else:  # Annual
            return await self._group_revenue_by_year(sales, start_date, end_date, category_id)

    async def compare_revenue(
        self,
        period: RevenuePeriodEnum,
        period1_start: date,
        period1_end: date,
        period2_start: date,
        period2_end: date,
        category_id: Optional[int] = None
    ) -> RevenueCompareResponse:
        """
        Compare revenue between two time periods.
        """
        period1_data = await self.get_revenue_by_period(period, period1_start, period1_end, category_id)
        period2_data = await self.get_revenue_by_period(period, period2_start, period2_end, category_id)
        
        period1_total_revenue = sum(item.total_revenue for item in period1_data)
        period1_total_sales = sum(item.total_sales for item in period1_data)
        period1_avg_order = period1_total_revenue / period1_total_sales if period1_total_sales > 0 else 0
        
        period2_total_revenue = sum(item.total_revenue for item in period2_data)
        period2_total_sales = sum(item.total_sales for item in period2_data)
        period2_avg_order = period2_total_revenue / period2_total_sales if period2_total_sales > 0 else 0
        
        revenue_change = period2_total_revenue - period1_total_revenue
        revenue_change_pct = (revenue_change / period1_total_revenue * 100) if period1_total_revenue > 0 else 0
        sales_change = period2_total_sales - period1_total_sales
        sales_change_pct = (sales_change / period1_total_sales * 100) if period1_total_sales > 0 else 0
        
        period1_name = f"{period1_start.strftime('%Y-%m-%d')} to {period1_end.strftime('%Y-%m-%d')}"
        period2_name = f"{period2_start.strftime('%Y-%m-%d')} to {period2_end.strftime('%Y-%m-%d')}"
        
        return RevenueCompareResponse(
            period1=RevenuePeriodData(
                period_name=period1_name,
                data=period1_data,
                total_revenue=period1_total_revenue,
                total_sales=period1_total_sales,
                average_order_value=period1_avg_order
            ),
            period2=RevenuePeriodData(
                period_name=period2_name,
                data=period2_data,
                total_revenue=period2_total_revenue,
                total_sales=period2_total_sales,
                average_order_value=period2_avg_order
            ),
            revenue_change=revenue_change,
            revenue_change_percentage=revenue_change_pct,
            sales_change=sales_change,
            sales_change_percentage=sales_change_pct
        )

    async def _group_revenue_by_day(
        self, 
        sales: List[Sale], 
        start_date: date, 
        end_date: date,
        category_name: Optional[str] = None
    ) -> List[RevenueResponse]:
        """Group sales by day and calculate revenue metrics."""
        result = []
        current_date = start_date
        
        daily_data = {}
        while current_date <= end_date:
            daily_data[current_date] = {
                "total_revenue": 0,
                "total_sales": 0,
                "order_count": 0
            }
            current_date += timedelta(days=1)
        
        for sale in sales:
            sale_date = sale.sale_date.date()
            if sale_date in daily_data:
                daily_data[sale_date]["total_revenue"] += sale.total_amount
                daily_data[sale_date]["total_sales"] += sum(item.quantity for item in sale.items)
                daily_data[sale_date]["order_count"] += 1
        
        for day, data in daily_data.items():
            avg_order = data["total_revenue"] / data["order_count"] if data["order_count"] > 0 else 0
            result.append(
                RevenueResponse(
                    period_start=day,
                    period_end=day,
                    total_revenue=data["total_revenue"],
                    total_sales=data["total_sales"],
                    average_order_value=avg_order,
                    period_label=day.strftime("%Y-%m-%d"),
                    category_name=category_name
                )
            )
        
        return result

    async def _group_revenue_by_week(
        self, 
        sales: List[Sale],
        start_date: date,
        end_date: date,
        category_name: Optional[str] = None
    ) -> List[RevenueResponse]:
        """Group sales by week and calculate revenue metrics."""
        result = []
        
        start_weekday = start_date.weekday()
        first_day = start_date - timedelta(days=start_weekday)
        
        weekly_data = {}
        current_week_start = first_day
        
        while current_week_start <= end_date:
            current_week_end = current_week_start + timedelta(days=6)
            weekly_data[current_week_start] = {
                "end_date": current_week_end,
                "total_revenue": 0,
                "total_sales": 0,
                "order_count": 0
            }
            current_week_start += timedelta(days=7)
        
        for sale in sales:
            sale_date = sale.sale_date.date()
            sale_weekday = sale_date.weekday()
            sale_week_start = sale_date - timedelta(days=sale_weekday)
            
            if sale_week_start in weekly_data:
                weekly_data[sale_week_start]["total_revenue"] += sale.total_amount
                weekly_data[sale_week_start]["total_sales"] += sum(item.quantity for item in sale.items)
                weekly_data[sale_week_start]["order_count"] += 1
        
        for week_start, data in weekly_data.items():
            avg_order = data["total_revenue"] / data["order_count"] if data["order_count"] > 0 else 0
            result.append(
                RevenueResponse(
                    period_start=week_start,
                    period_end=data["end_date"],
                    total_revenue=data["total_revenue"],
                    total_sales=data["total_sales"],
                    average_order_value=avg_order,
                    period_label=f"Week of {week_start.strftime('%Y-%m-%d')}",
                    category_name=category_name
                )
            )
        
        return result

    async def _group_revenue_by_month(
        self, 
        sales: List[Sale],
        start_date: date,
        end_date: date,
        category_name: Optional[str] = None
    ) -> List[RevenueResponse]:
        """Group sales by month and calculate revenue metrics."""
        result = []
        
        monthly_data = {}
        current_year = start_date.year
        current_month = start_date.month
        
        while (current_year < end_date.year) or (current_year == end_date.year and current_month <= end_date.month):
            month_start = date(current_year, current_month, 1)
            last_day = calendar.monthrange(current_year, current_month)[1]
            month_end = date(current_year, current_month, last_day)
            
            monthly_data[month_start] = {
                "end_date": month_end,
                "total_revenue": 0,
                "total_sales": 0,
                "order_count": 0
            }
            
            if current_month == 12:
                current_month = 1
                current_year += 1
            else:
                current_month += 1
        
        for sale in sales:
            sale_date = sale.sale_date.date()
            month_start = date(sale_date.year, sale_date.month, 1)
            
            if month_start in monthly_data:
                monthly_data[month_start]["total_revenue"] += sale.total_amount
                monthly_data[month_start]["total_sales"] += sum(item.quantity for item in sale.items)
                monthly_data[month_start]["order_count"] += 1
        
        for month_start, data in monthly_data.items():
            avg_order = data["total_revenue"] / data["order_count"] if data["order_count"] > 0 else 0
            result.append(
                RevenueResponse(
                    period_start=month_start,
                    period_end=data["end_date"],
                    total_revenue=data["total_revenue"],
                    total_sales=data["total_sales"],
                    average_order_value=avg_order,
                    period_label=month_start.strftime("%B %Y"),
                    category_name=category_name
                )
            )
        
        return result

    async def _group_revenue_by_year(
        self, 
        sales: List[Sale],
        start_date: date,
        end_date: date,
        category_name: Optional[str] = None
    ) -> List[RevenueResponse]:
        """Group sales by year and calculate revenue metrics."""
        result = []
        
        yearly_data = {}
        for year in range(start_date.year, end_date.year + 1):
            year_start = date(year, 1, 1)
            year_end = date(year, 12, 31)
            
            yearly_data[year] = {
                "start_date": year_start,
                "end_date": year_end,
                "total_revenue": 0,
                "total_sales": 0,
                "order_count": 0
            }
        
        for sale in sales:
            sale_year = sale.sale_date.year
            
            if sale_year in yearly_data:
                yearly_data[sale_year]["total_revenue"] += sale.total_amount
                yearly_data[sale_year]["total_sales"] += sum(item.quantity for item in sale.items)
                yearly_data[sale_year]["order_count"] += 1
        
        for year, data in yearly_data.items():
            avg_order = data["total_revenue"] / data["order_count"] if data["order_count"] > 0 else 0
            result.append(
                RevenueResponse(
                    period_start=data["start_date"],
                    period_end=data["end_date"],
                    total_revenue=data["total_revenue"],
                    total_sales=data["total_sales"],
                    average_order_value=avg_order,
                    period_label=str(year),
                    category_name=category_name
                )
            )
        
        return result 