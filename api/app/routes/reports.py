from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import Optional
import os
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.research_report import ResearchReport, ReportType
from app.schemas.report import ReportResponse, ReportListResponse

router = APIRouter(prefix="/reports", tags=["研报"])


@router.get("", response_model=ReportListResponse)
async def list_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    report_type: Optional[str] = None,
    keyword: Optional[str] = None,
    source: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(ResearchReport)
    count_query = select(func.count(ResearchReport.report_id))
    
    if report_type:
        query = query.where(ResearchReport.report_type == report_type)
        count_query = count_query.where(ResearchReport.report_type == report_type)
    
    if keyword:
        filter_cond = or_(
            ResearchReport.title.contains(keyword),
            ResearchReport.related_stock.contains(keyword),
            ResearchReport.industry.contains(keyword),
        )
        query = query.where(filter_cond)
        count_query = count_query.where(filter_cond)
    
    if source:
        query = query.where(ResearchReport.source.contains(source))
        count_query = count_query.where(ResearchReport.source.contains(source))
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    query = query.order_by(ResearchReport.publish_time.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    reports = result.scalars().all()
    
    items = []
    for r in reports:
        resp = ReportResponse.model_validate(r)
        resp.has_pdf = bool(r.file_path and os.path.exists(r.file_path))
        items.append(resp)
    
    return ReportListResponse(total=total, items=items)


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ResearchReport).where(ResearchReport.report_id == report_id)
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="研报不存在")
    
    resp = ReportResponse.model_validate(report)
    resp.has_pdf = bool(report.file_path and os.path.exists(report.file_path))
    return resp


@router.get("/{report_id}/download")
async def download_report_pdf(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ResearchReport).where(ResearchReport.report_id == report_id)
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="研报不存在")
    
    if not report.file_path or not os.path.exists(report.file_path):
        raise HTTPException(status_code=404, detail="PDF文件不存在")
    
    return FileResponse(
        report.file_path,
        media_type="application/pdf",
        filename=f"{report.title}.pdf",
    )
