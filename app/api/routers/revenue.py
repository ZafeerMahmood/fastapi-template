from typing import Optional, List
from datetime import date

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.revenue import RevenueResponse, RevenuePeriodEnum, RevenueCompareResponse
from app.services.revenue import RevenueService

router = APIRouter()


@router.get("/daily", response_model=List[RevenueResponse])
async def get_daily_revenue(
    start_date: Optional[date] = Query(None, description="Start date for revenue analysis"),
    end_date: Optional[date] = Query(None, description="End date for revenue analysis"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get daily revenue statistics.
    """
    return await RevenueService(db).get_revenue_by_period(
        RevenuePeriodEnum.DAILY, start_date, end_date, category_id
    )


@router.get("/weekly", response_model=List[RevenueResponse])
async def get_weekly_revenue(
    start_date: Optional[date] = Query(None, description="Start date for revenue analysis"),
    end_date: Optional[date] = Query(None, description="End date for revenue analysis"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get weekly revenue statistics.
    """
    return await RevenueService(db).get_revenue_by_period(
        RevenuePeriodEnum.WEEKLY, start_date, end_date, category_id
    )


@router.get("/monthly", response_model=List[RevenueResponse])
async def get_monthly_revenue(
    start_date: Optional[date] = Query(None, description="Start date for revenue analysis"),
    end_date: Optional[date] = Query(None, description="End date for revenue analysis"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get monthly revenue statistics.
    """
    return await RevenueService(db).get_revenue_by_period(
        RevenuePeriodEnum.MONTHLY, start_date, end_date, category_id
    )


@router.get("/annual", response_model=List[RevenueResponse])
async def get_annual_revenue(
    start_date: Optional[date] = Query(None, description="Start date for revenue analysis"),
    end_date: Optional[date] = Query(None, description="End date for revenue analysis"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get annual revenue statistics.
    """
    return await RevenueService(db).get_revenue_by_period(
        RevenuePeriodEnum.ANNUAL, start_date, end_date, category_id
    )


@router.get("/compare", response_model=RevenueCompareResponse)
async def compare_revenue(
    period: RevenuePeriodEnum = Query(RevenuePeriodEnum.MONTHLY, description="Period for comparison"),
    period1_start: date = Query(..., description="Start date for first period"),
    period1_end: date = Query(..., description="End date for first period"),
    period2_start: date = Query(..., description="Start date for second period"),
    period2_end: date = Query(..., description="End date for second period"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    db: AsyncSession = Depends(get_db),
):
    """
    Compare revenue between two time periods.
    """
    return await RevenueService(db).compare_revenue(
        period, period1_start, period1_end, period2_start, period2_end, category_id
    ) 