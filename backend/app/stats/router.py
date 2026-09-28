from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_admin
from app.auth.models import AdminUser
from app.db.session import get_db
from app.stats import service
from app.stats.schemas import DashboardStats

router = APIRouter()


@router.get("", response_model=DashboardStats, summary="Estatísticas gerais do catálogo")
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
) -> DashboardStats:
    return await service.get_dashboard_stats(db)
