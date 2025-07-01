"""
Analytics Routes
Usage analytics, subscription insights, and admin dashboards
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc, text
from pydantic import BaseModel

from ...db.database import get_db
from ...auth.models import User, Subscription, UsageLog, SubscriptionTier, UsageStats
from ...auth.dependencies import AuthenticatedUser, AdminUser

router = APIRouter(prefix="/analytics", tags=["Analytics"])

# Response Models
class DashboardStats(BaseModel):
    """Dashboard statistics"""
    total_users: int
    active_users: int
    total_requests_today: int
    total_requests_month: int
    revenue_this_month: float
    top_endpoints: List[Dict[str, Any]]
    subscription_breakdown: Dict[str, int]

class UserAnalytics(BaseModel):
    """User analytics response"""
    user_id: str
    total_requests: int
    requests_this_month: int
    requests_today: int
    subscription_tier: str
    join_date: datetime
    last_request: Optional[datetime]
    top_endpoints: List[Dict[str, Any]]

class EndpointAnalytics(BaseModel):
    """Endpoint analytics"""
    endpoint: str
    total_requests: int
    unique_users: int
    average_response_time: float
    error_rate: float
    requests_by_day: List[Dict[str, Any]]

# User Analytics Endpoints

@router.get("/my-usage", response_model=UsageStats)
async def get_my_usage_stats(
    current_user: AuthenticatedUser,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """Get usage statistics for the current user"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Total requests
    total_stmt = select(func.count(UsageLog.id)).where(
        UsageLog.user_id == current_user.id,
        UsageLog.timestamp >= start_date
    )
    total_result = await db.execute(total_stmt)
    total_requests = total_result.scalar() or 0
    
    # Requests today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_stmt = select(func.count(UsageLog.id)).where(
        UsageLog.user_id == current_user.id,
        UsageLog.timestamp >= today_start
    )
    today_result = await db.execute(today_stmt)
    requests_today = today_result.scalar() or 0
    
    # Requests this month
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_stmt = select(func.count(UsageLog.id)).where(
        UsageLog.user_id == current_user.id,
        UsageLog.timestamp >= month_start
    )
    month_result = await db.execute(month_stmt)
    requests_this_month = month_result.scalar() or 0
    
    # Average response time
    avg_time_stmt = select(func.avg(UsageLog.response_time_ms)).where(
        UsageLog.user_id == current_user.id,
        UsageLog.timestamp >= start_date
    )
    avg_time_result = await db.execute(avg_time_stmt)
    average_response_time = float(avg_time_result.scalar() or 0)
    
    # Cache hit rate
    cache_hit_stmt = select(
        func.count(UsageLog.id).filter(UsageLog.cache_hit == True),
        func.count(UsageLog.id)
    ).where(
        UsageLog.user_id == current_user.id,
        UsageLog.timestamp >= start_date
    )
    cache_result = await db.execute(cache_hit_stmt)
    cache_hits, total_cache_requests = cache_result.first()
    cache_hit_rate = (cache_hits / total_cache_requests * 100) if total_cache_requests > 0 else 0
    
    # Top endpoints
    top_endpoints_stmt = select(
        UsageLog.endpoint,
        func.count(UsageLog.id).label("count")
    ).where(
        UsageLog.user_id == current_user.id,
        UsageLog.timestamp >= start_date
    ).group_by(UsageLog.endpoint).order_by(desc("count")).limit(10)
    
    top_endpoints_result = await db.execute(top_endpoints_stmt)
    top_endpoints = [
        {"endpoint": endpoint, "count": count}
        for endpoint, count in top_endpoints_result.fetchall()
    ]
    
    # Usage by day
    usage_by_day_stmt = select(
        func.date(UsageLog.timestamp).label("date"),
        func.count(UsageLog.id).label("count")
    ).where(
        UsageLog.user_id == current_user.id,
        UsageLog.timestamp >= start_date
    ).group_by(func.date(UsageLog.timestamp)).order_by("date")
    
    usage_by_day_result = await db.execute(usage_by_day_stmt)
    usage_by_day = [
        {"date": str(date), "count": count}
        for date, count in usage_by_day_result.fetchall()
    ]
    
    return UsageStats(
        total_requests=total_requests,
        requests_today=requests_today,
        requests_this_month=requests_this_month,
        average_response_time=average_response_time,
        cache_hit_rate=cache_hit_rate,
        top_endpoints=top_endpoints,
        usage_by_day=usage_by_day
    )

@router.get("/subscription-info")
async def get_subscription_info(
    current_user: AuthenticatedUser,
    db: AsyncSession = Depends(get_db)
):
    """Get detailed subscription information and usage limits"""
    # Get subscription
    sub_stmt = select(Subscription).where(Subscription.user_id == current_user.id)
    sub_result = await db.execute(sub_stmt)
    subscription = sub_result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    # Get current usage
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Today's usage
    today_usage_stmt = select(func.count(UsageLog.id)).where(
        UsageLog.user_id == current_user.id,
        UsageLog.timestamp >= today
    )
    today_usage_result = await db.execute(today_usage_stmt)
    today_usage = today_usage_result.scalar() or 0
    
    # Month's usage
    month_usage_stmt = select(func.count(UsageLog.id)).where(
        UsageLog.user_id == current_user.id,
        UsageLog.timestamp >= month_start
    )
    month_usage_result = await db.execute(month_usage_stmt)
    month_usage = month_usage_result.scalar() or 0
    
    return {
        "subscription": subscription,
        "usage": {
            "today": today_usage,
            "today_limit": subscription.requests_per_day,
            "today_remaining": max(0, subscription.requests_per_day - today_usage),
            "month": month_usage,
            "month_limit": subscription.requests_per_month,
            "month_remaining": max(0, subscription.requests_per_month - month_usage),
            "percentage_used_today": (today_usage / subscription.requests_per_day * 100) if subscription.requests_per_day > 0 else 0,
            "percentage_used_month": (month_usage / subscription.requests_per_month * 100) if subscription.requests_per_month > 0 else 0
        }
    }

# Admin Analytics Endpoints

@router.get("/admin/dashboard", response_model=DashboardStats)
async def get_admin_dashboard(
    admin_user: AdminUser,
    db: AsyncSession = Depends(get_db)
):
    """Get admin dashboard statistics"""
    # Total users
    total_users_stmt = select(func.count(User.id))
    total_users_result = await db.execute(total_users_stmt)
    total_users = total_users_result.scalar() or 0
    
    # Active users (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    active_users_stmt = select(func.count(func.distinct(User.id))).where(
        User.last_login >= thirty_days_ago
    )
    active_users_result = await db.execute(active_users_stmt)
    active_users = active_users_result.scalar() or 0
    
    # Requests today
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    requests_today_stmt = select(func.count(UsageLog.id)).where(
        UsageLog.timestamp >= today
    )
    requests_today_result = await db.execute(requests_today_stmt)
    total_requests_today = requests_today_result.scalar() or 0
    
    # Requests this month
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    requests_month_stmt = select(func.count(UsageLog.id)).where(
        UsageLog.timestamp >= month_start
    )
    requests_month_result = await db.execute(requests_month_stmt)
    total_requests_month = requests_month_result.scalar() or 0
    
    # Revenue this month (calculated from subscriptions)
    revenue_stmt = select(func.sum(Subscription.amount)).where(
        and_(
            Subscription.status == "active",
            Subscription.started_at >= month_start
        )
    )
    revenue_result = await db.execute(revenue_stmt)
    revenue_this_month = float(revenue_result.scalar() or 0)
    
    # Top endpoints
    top_endpoints_stmt = select(
        UsageLog.endpoint,
        func.count(UsageLog.id).label("requests")
    ).where(
        UsageLog.timestamp >= thirty_days_ago
    ).group_by(UsageLog.endpoint).order_by(desc("requests")).limit(10)
    
    top_endpoints_result = await db.execute(top_endpoints_stmt)
    top_endpoints = [
        {"endpoint": endpoint, "requests": requests}
        for endpoint, requests in top_endpoints_result.fetchall()
    ]
    
    # Subscription breakdown
    sub_breakdown_stmt = select(
        Subscription.tier,
        func.count(Subscription.id).label("count")
    ).where(
        Subscription.status == "active"
    ).group_by(Subscription.tier)
    
    sub_breakdown_result = await db.execute(sub_breakdown_stmt)
    subscription_breakdown = {
        tier: count for tier, count in sub_breakdown_result.fetchall()
    }
    
    return DashboardStats(
        total_users=total_users,
        active_users=active_users,
        total_requests_today=total_requests_today,
        total_requests_month=total_requests_month,
        revenue_this_month=revenue_this_month,
        top_endpoints=top_endpoints,
        subscription_breakdown=subscription_breakdown
    )

@router.get("/admin/users/{user_id}/analytics", response_model=UserAnalytics)
async def get_user_analytics(
    user_id: str,
    admin_user: AdminUser,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """Get analytics for a specific user (admin only)"""
    # Verify user exists
    user_stmt = select(User).where(User.id == user_id)
    user_result = await db.execute(user_stmt)
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get subscription
    sub_stmt = select(Subscription).where(Subscription.user_id == user_id)
    sub_result = await db.execute(sub_stmt)
    subscription = sub_result.scalar_one_or_none()
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Total requests
    total_stmt = select(func.count(UsageLog.id)).where(
        UsageLog.user_id == user_id
    )
    total_result = await db.execute(total_stmt)
    total_requests = total_result.scalar() or 0
    
    # Requests this month
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_stmt = select(func.count(UsageLog.id)).where(
        UsageLog.user_id == user_id,
        UsageLog.timestamp >= month_start
    )
    month_result = await db.execute(month_stmt)
    requests_this_month = month_result.scalar() or 0
    
    # Requests today
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_stmt = select(func.count(UsageLog.id)).where(
        UsageLog.user_id == user_id,
        UsageLog.timestamp >= today
    )
    today_result = await db.execute(today_stmt)
    requests_today = today_result.scalar() or 0
    
    # Last request
    last_request_stmt = select(func.max(UsageLog.timestamp)).where(
        UsageLog.user_id == user_id
    )
    last_request_result = await db.execute(last_request_stmt)
    last_request = last_request_result.scalar()
    
    # Top endpoints
    top_endpoints_stmt = select(
        UsageLog.endpoint,
        func.count(UsageLog.id).label("count")
    ).where(
        UsageLog.user_id == user_id,
        UsageLog.timestamp >= start_date
    ).group_by(UsageLog.endpoint).order_by(desc("count")).limit(5)
    
    top_endpoints_result = await db.execute(top_endpoints_stmt)
    top_endpoints = [
        {"endpoint": endpoint, "count": count}
        for endpoint, count in top_endpoints_result.fetchall()
    ]
    
    return UserAnalytics(
        user_id=user_id,
        total_requests=total_requests,
        requests_this_month=requests_this_month,
        requests_today=requests_today,
        subscription_tier=subscription.tier if subscription else "free",
        join_date=user.created_at,
        last_request=last_request,
        top_endpoints=top_endpoints
    )

@router.get("/admin/endpoints/{endpoint_path:path}", response_model=EndpointAnalytics)
async def get_endpoint_analytics(
    endpoint_path: str,
    admin_user: AdminUser,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """Get analytics for a specific endpoint (admin only)"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Ensure endpoint starts with /
    if not endpoint_path.startswith("/"):
        endpoint_path = "/" + endpoint_path
    
    # Total requests
    total_stmt = select(func.count(UsageLog.id)).where(
        UsageLog.endpoint == endpoint_path,
        UsageLog.timestamp >= start_date
    )
    total_result = await db.execute(total_stmt)
    total_requests = total_result.scalar() or 0
    
    # Unique users
    unique_users_stmt = select(func.count(func.distinct(UsageLog.user_id))).where(
        UsageLog.endpoint == endpoint_path,
        UsageLog.timestamp >= start_date
    )
    unique_users_result = await db.execute(unique_users_stmt)
    unique_users = unique_users_result.scalar() or 0
    
    # Average response time
    avg_time_stmt = select(func.avg(UsageLog.response_time_ms)).where(
        UsageLog.endpoint == endpoint_path,
        UsageLog.timestamp >= start_date
    )
    avg_time_result = await db.execute(avg_time_stmt)
    average_response_time = float(avg_time_result.scalar() or 0)
    
    # Error rate
    error_count_stmt = select(func.count(UsageLog.id)).where(
        UsageLog.endpoint == endpoint_path,
        UsageLog.timestamp >= start_date,
        UsageLog.status_code >= 400
    )
    error_count_result = await db.execute(error_count_stmt)
    error_count = error_count_result.scalar() or 0
    error_rate = (error_count / total_requests * 100) if total_requests > 0 else 0
    
    # Requests by day
    requests_by_day_stmt = select(
        func.date(UsageLog.timestamp).label("date"),
        func.count(UsageLog.id).label("requests")
    ).where(
        UsageLog.endpoint == endpoint_path,
        UsageLog.timestamp >= start_date
    ).group_by(func.date(UsageLog.timestamp)).order_by("date")
    
    requests_by_day_result = await db.execute(requests_by_day_stmt)
    requests_by_day = [
        {"date": str(date), "requests": requests}
        for date, requests in requests_by_day_result.fetchall()
    ]
    
    return EndpointAnalytics(
        endpoint=endpoint_path,
        total_requests=total_requests,
        unique_users=unique_users,
        average_response_time=average_response_time,
        error_rate=error_rate,
        requests_by_day=requests_by_day
    ) 