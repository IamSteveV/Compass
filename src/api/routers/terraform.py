"""Terraform integration API endpoints"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Body
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import logging

from ...config import get_settings
from ...terraform_integration import (
    TerraformCloudClient,
    TerraformStateAnalyzer,
    TerraformResourceGraph
)
from ...validation.engine import ValidationEngine
from ...patterns.matcher import PatternMatcher

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize components
state_analyzer = TerraformStateAnalyzer()
resource_graph = TerraformResourceGraph()
validation_engine = ValidationEngine()
pattern_matcher = PatternMatcher()


class TerraformCloudConfig(BaseModel):
    """Configuration for Terraform Cloud connection"""
    api_token: str
    organization: str
    base_url: Optional[str] = "https://app.terraform.io/api/v2"


class WorkspaceAnalysisRequest(BaseModel):
    """Request for workspace analysis"""
    workspace_name: str
    config: TerraformCloudConfig


@router.get("/cloud/test")
async def test_terraform_cloud_connection(
    api_token: str,
    organization: str,
    base_url: str = "https://app.terraform.io/api/v2"
):
    """
    Test Terraform Cloud API connection

    Args:
        api_token: Terraform Cloud API token
        organization: Organization name
        base_url: API base URL

    Returns:
        Connection test results
    """
    try:
        client = TerraformCloudClient(
            api_token=api_token,
            organization=organization,
            base_url=base_url
        )

        # Try to list workspaces
        workspaces = client.list_workspaces(page_size=5)

        return {
            "success": True,
            "message": "Successfully connected to Terraform Cloud",
            "organization": organization,
            "workspace_count": len(workspaces),
            "sample_workspaces": [w['name'] for w in workspaces[:5]]
        }

    except Exception as e:
        logger.error(f"Terraform Cloud connection test failed: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to connect to Terraform Cloud: {str(e)}"
        )


@router.post("/cloud/workspaces")
async def list_workspaces(config: TerraformCloudConfig):
    """
    List Terraform Cloud workspaces

    Args:
        config: Terraform Cloud configuration

    Returns:
        List of workspaces
    """
    try:
        client = TerraformCloudClient(
            api_token=config.api_token,
            organization=config.organization,
            base_url=config.base_url
        )

        workspaces = client.list_workspaces(page_size=100)

        return {
            "organization": config.organization,
            "workspace_count": len(workspaces),
            "workspaces": workspaces
        }

    except Exception as e:
        logger.error(f"Failed to list workspaces: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cloud/workspace/analyze")
async def analyze_workspace(request: WorkspaceAnalysisRequest):
    """
    Analyze a Terraform Cloud workspace

    Args:
        request: Workspace analysis request

    Returns:
        Comprehensive workspace analysis
    """
    try:
        client = TerraformCloudClient(
            api_token=request.config.api_token,
            organization=request.config.organization,
            base_url=request.config.base_url
        )

        # Get workspace resources
        workspace_data = client.get_workspace_resources(request.workspace_name)

        # If no state, return workspace info only
        if not workspace_data['state']:
            return {
                "workspace": workspace_data['workspace'],
                "message": "No state found for this workspace",
                "has_state": False
            }

        # Download and analyze state
        state_url = workspace_data['state'].get('hosted_state_download_url')
        if not state_url:
            return {
                "workspace": workspace_data['workspace'],
                "state_info": workspace_data['state'],
                "message": "State information available but download URL not provided",
                "has_state": True
            }

        # Download full state
        full_state = client.download_state_file(state_url)

        # Analyze state
        analysis = state_analyzer.analyze_state(full_state)

        # Generate graph data
        graph_data = resource_graph.generate_network_json(
            analysis['resources'],
            analysis['topology']
        )

        # Generate summary stats
        stats = resource_graph.generate_summary_stats(
            analysis['resources'],
            analysis['topology']
        )

        return {
            "workspace": workspace_data['workspace'],
            "analysis": analysis,
            "graph": graph_data,
            "stats": stats,
            "has_state": True
        }

    except Exception as e:
        logger.error(f"Failed to analyze workspace: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cloud/workspace/validate")
async def validate_workspace(request: WorkspaceAnalysisRequest):
    """
    Validate a Terraform Cloud workspace against architectural standards

    Args:
        request: Workspace analysis request

    Returns:
        Validation report
    """
    try:
        client = TerraformCloudClient(
            api_token=request.config.api_token,
            organization=request.config.organization,
            base_url=request.config.base_url
        )

        # Get workspace resources
        workspace_data = client.get_workspace_resources(request.workspace_name)

        if not workspace_data['state']:
            raise HTTPException(status_code=404, detail="No state found for workspace")

        state_url = workspace_data['state'].get('hosted_state_download_url')
        if not state_url:
            raise HTTPException(status_code=404, detail="State download URL not available")

        # Download and analyze state
        full_state = client.download_state_file(state_url)
        analysis = state_analyzer.analyze_state(full_state)

        # Convert to validation context
        validation_context = state_analyzer.get_validation_context(analysis)

        # Match pattern
        pattern_match = pattern_matcher.match_pattern(
            validation_context['resources'],
            validation_context['topology']
        )

        # Run validation
        context = {
            **validation_context,
            'pattern_match': pattern_match,
            'workspace': workspace_data['workspace']
        }

        report = validation_engine.validate(validation_context['resources'], context)

        return report

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to validate workspace: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/state/analyze")
async def analyze_state_file(file: UploadFile = File(...)):
    """
    Analyze a Terraform state file

    Args:
        file: Terraform state file (JSON)

    Returns:
        State analysis results
    """
    if not file.filename.endswith('.json') and not file.filename.endswith('.tfstate'):
        raise HTTPException(
            status_code=400,
            detail="File must be a JSON or .tfstate file"
        )

    try:
        content = await file.read()
        state = json.loads(content)

        # Analyze state
        analysis = state_analyzer.analyze_state(state)

        # Generate graph data
        graph_data = resource_graph.generate_network_json(
            analysis['resources'],
            analysis['topology']
        )

        # Generate summary stats
        stats = resource_graph.generate_summary_stats(
            analysis['resources'],
            analysis['topology']
        )

        # Generate Mermaid diagram
        mermaid_diagram = resource_graph.generate_mermaid_diagram(
            analysis['resources'],
            analysis['topology']
        )

        return {
            "analysis": analysis,
            "graph": graph_data,
            "stats": stats,
            "diagram": {
                "mermaid": mermaid_diagram
            }
        }

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")
    except Exception as e:
        logger.error(f"Failed to analyze state file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/state/validate")
async def validate_state_file(file: UploadFile = File(...)):
    """
    Validate a Terraform state file against architectural standards

    Args:
        file: Terraform state file (JSON)

    Returns:
        Validation report
    """
    if not file.filename.endswith('.json') and not file.filename.endswith('.tfstate'):
        raise HTTPException(
            status_code=400,
            detail="File must be a JSON or .tfstate file"
        )

    try:
        content = await file.read()
        state = json.loads(content)

        # Analyze state
        analysis = state_analyzer.analyze_state(state)

        # Convert to validation context
        validation_context = state_analyzer.get_validation_context(analysis)

        # Match pattern
        pattern_match = pattern_matcher.match_pattern(
            validation_context['resources'],
            validation_context['topology']
        )

        # Run validation
        context = {
            **validation_context,
            'pattern_match': pattern_match,
            'state_file': file.filename
        }

        report = validation_engine.validate(validation_context['resources'], context)

        return report

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")
    except Exception as e:
        logger.error(f"Failed to validate state file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/graph/generate")
async def generate_resource_graph(
    resources: List[Dict[str, Any]],
    topology: List[Dict[str, str]],
    format: str = "json"
):
    """
    Generate resource graph in various formats

    Args:
        resources: List of resource objects
        topology: List of relationship objects
        format: Output format (json, mermaid, dot)

    Returns:
        Graph in requested format
    """
    try:
        if format == "json":
            graph_data = resource_graph.generate_network_json(resources, topology)
            return {"format": "json", "data": graph_data}

        elif format == "mermaid":
            diagram = resource_graph.generate_mermaid_diagram(resources, topology)
            return {"format": "mermaid", "data": diagram}

        elif format == "dot":
            diagram = resource_graph.generate_graphviz_dot(resources, topology)
            return {"format": "dot", "data": diagram}

        elif format == "hierarchy":
            tree = resource_graph.generate_hierarchy_json(resources)
            return {"format": "hierarchy", "data": tree}

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported format: {format}. Supported formats: json, mermaid, dot, hierarchy"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/graph/stats")
async def get_graph_stats(
    resources: List[Dict[str, Any]],
    topology: List[Dict[str, str]]
):
    """
    Get statistics about a resource graph

    Args:
        resources: List of resource objects
        topology: List of relationship objects

    Returns:
        Graph statistics
    """
    try:
        stats = resource_graph.generate_summary_stats(resources, topology)
        return stats

    except Exception as e:
        logger.error(f"Failed to generate stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/circular-dependencies")
async def find_circular_dependencies(
    resources: List[Dict[str, Any]],
    topology: List[Dict[str, str]]
):
    """
    Find circular dependencies in resource graph

    Args:
        resources: List of resource objects
        topology: List of relationship objects

    Returns:
        List of circular dependency chains
    """
    try:
        cycles = resource_graph.find_circular_dependencies(resources, topology)

        return {
            "has_cycles": len(cycles) > 0,
            "cycle_count": len(cycles),
            "cycles": cycles
        }

    except Exception as e:
        logger.error(f"Failed to find circular dependencies: {e}")
        raise HTTPException(status_code=500, detail=str(e))
