"""CMDB integration endpoints"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from ...cmdb.client import CMDBClient
from ...models import CMDBApplication

router = APIRouter()


@router.get("/applications")
async def list_applications(
    name: Optional[str] = Query(None, description="Filter by application name"),
    limit: int = Query(100, description="Maximum number of results")
):
    """
    Get list of applications from CMDB.

    Args:
        name: Optional name filter
        limit: Maximum results to return

    Returns:
        List of applications
    """
    try:
        client = CMDBClient()
        apps = client.connector.get_applications(name_filter=name, limit=limit)

        return [
            {
                "sys_id": app['sys_id'],
                "name": app.get('name', ''),
                "description": app.get('short_description', '')
            }
            for app in apps
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch applications: {str(e)}")


@router.get("/applications/{app_id}", response_model=CMDBApplication)
async def get_application(app_id: str):
    """
    Get application details with topology.

    Args:
        app_id: Application sys_id or name

    Returns:
        Application with all related CIs and relationships
    """
    try:
        client = CMDBClient()
        app = client.get_application_topology(app_id)
        return app

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch application: {str(e)}")


@router.get("/applications/{app_id}/topology")
async def get_application_topology(app_id: str):
    """
    Get application topology formatted for validation.

    Args:
        app_id: Application sys_id or name

    Returns:
        Topology with resources and connections
    """
    try:
        client = CMDBClient()
        topology_data = client.get_topology_for_validation(app_id)
        return topology_data

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch topology: {str(e)}")
