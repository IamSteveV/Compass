"""Pattern management endpoints"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from typing import List, Optional
from pathlib import Path

from ...patterns.library import PatternLibrary
from ...models import Pattern

router = APIRouter()

# Initialize pattern library
library = PatternLibrary()


@router.get("/", response_model=List[Pattern])
async def list_patterns(
    status: Optional[str] = Query(None, description="Filter by status (approved, draft, etc.)")
):
    """
    Get list of all architecture patterns.

    Args:
        status: Optional status filter

    Returns:
        List of patterns
    """
    patterns = library.get_all_patterns()

    if status:
        patterns = [p for p in patterns if p.metadata.status == status]

    return patterns


@router.get("/{pattern_id}", response_model=Pattern)
async def get_pattern(pattern_id: str):
    """
    Get a specific pattern by ID.

    Args:
        pattern_id: Pattern ID (e.g., PAT-001)

    Returns:
        Pattern details
    """
    pattern = library.get_pattern(pattern_id)

    if not pattern:
        raise HTTPException(status_code=404, detail=f"Pattern not found: {pattern_id}")

    return pattern


@router.get("/{pattern_id}/diagram")
async def get_pattern_diagram(pattern_id: str):
    """
    Get pattern diagram image.

    Args:
        pattern_id: Pattern ID

    Returns:
        Diagram image file
    """
    diagram_path = library.get_pattern_diagram_path(pattern_id)

    if not diagram_path or not diagram_path.exists():
        raise HTTPException(status_code=404, detail=f"Diagram not found for pattern: {pattern_id}")

    return FileResponse(diagram_path)


@router.get("/search/{query}")
async def search_patterns(query: str):
    """
    Search patterns by name or description.

    Args:
        query: Search query string

    Returns:
        List of matching patterns
    """
    results = library.search_patterns(query)
    return results


@router.post("/reload")
async def reload_patterns():
    """
    Reload patterns from repository.

    Returns:
        Number of patterns loaded
    """
    library.reload()
    return {
        "status": "success",
        "patterns_loaded": len(library)
    }
