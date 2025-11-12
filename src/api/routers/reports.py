"""Reports API router"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import Optional
import logging

from ...database.session import get_db
from ...database.repository import ValidationHistoryRepository
from ...reporting import PDFReportGenerator
from ...models import ValidationReport

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/{report_id}/pdf")
async def generate_pdf_report(
    report_id: str,
    db: Session = Depends(get_db)
):
    """
    Generate PDF report for a validation

    Args:
        report_id: Validation report ID
        db: Database session

    Returns:
        PDF file as application/pdf
    """
    try:
        # Get validation from database
        validation = ValidationHistoryRepository.get_by_id(db, report_id)

        if not validation:
            raise HTTPException(status_code=404, detail=f"Report {report_id} not found")

        # Reconstruct ValidationReport from database
        report_data = validation.report_json
        report = ValidationReport(**report_data)

        # Generate PDF
        pdf_generator = PDFReportGenerator()
        pdf_content = pdf_generator.generate_report(report)

        # Return PDF as response
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=validation-report-{report_id}.pdf"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating PDF report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")


@router.post("/generate-pdf")
async def generate_pdf_from_report(
    report: ValidationReport
):
    """
    Generate PDF report from a ValidationReport object

    Args:
        report: ValidationReport object

    Returns:
        PDF file as application/pdf
    """
    try:
        # Generate PDF
        pdf_generator = PDFReportGenerator()
        pdf_content = pdf_generator.generate_report(report)

        # Return PDF as response
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=validation-report-{report.id}.pdf"
            }
        )

    except Exception as e:
        logger.error(f"Error generating PDF report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")
