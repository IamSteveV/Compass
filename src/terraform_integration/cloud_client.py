"""Terraform Cloud/Enterprise API client"""

import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TerraformCloudClient:
    """Client for Terraform Cloud/Enterprise API integration"""

    def __init__(
        self,
        api_token: str,
        organization: str,
        base_url: str = "https://app.terraform.io/api/v2"
    ):
        """
        Initialize Terraform Cloud client

        Args:
            api_token: Terraform Cloud API token
            organization: Organization name
            base_url: API base URL (default: Terraform Cloud, can be Enterprise URL)
        """
        self.api_token = api_token
        self.organization = organization
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/vnd.api+json'
        })

    def list_workspaces(self, page_size: int = 20) -> List[Dict[str, Any]]:
        """
        List all workspaces in the organization

        Args:
            page_size: Number of workspaces per page

        Returns:
            List of workspace objects
        """
        try:
            url = f"{self.base_url}/organizations/{self.organization}/workspaces"
            params = {'page[size]': page_size}

            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            workspaces = []

            for workspace in data.get('data', []):
                workspaces.append({
                    'id': workspace['id'],
                    'name': workspace['attributes']['name'],
                    'terraform_version': workspace['attributes'].get('terraform-version'),
                    'working_directory': workspace['attributes'].get('working-directory'),
                    'auto_apply': workspace['attributes'].get('auto-apply', False),
                    'execution_mode': workspace['attributes'].get('execution-mode'),
                    'resource_count': workspace['attributes'].get('resource-count', 0),
                    'created_at': workspace['attributes'].get('created-at'),
                    'updated_at': workspace['attributes'].get('updated-at')
                })

            return workspaces

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to list workspaces: {e}")
            raise ValueError(f"Failed to fetch workspaces from Terraform Cloud: {str(e)}")

    def get_workspace(self, workspace_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific workspace

        Args:
            workspace_name: Name of the workspace

        Returns:
            Workspace details
        """
        try:
            url = f"{self.base_url}/organizations/{self.organization}/workspaces/{workspace_name}"

            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            data = response.json()
            workspace = data['data']

            return {
                'id': workspace['id'],
                'name': workspace['attributes']['name'],
                'description': workspace['attributes'].get('description'),
                'terraform_version': workspace['attributes'].get('terraform-version'),
                'working_directory': workspace['attributes'].get('working-directory'),
                'auto_apply': workspace['attributes'].get('auto-apply', False),
                'execution_mode': workspace['attributes'].get('execution-mode'),
                'resource_count': workspace['attributes'].get('resource-count', 0),
                'vcs_repo': workspace['attributes'].get('vcs-repo'),
                'created_at': workspace['attributes'].get('created-at'),
                'updated_at': workspace['attributes'].get('updated-at'),
                'environment': workspace['attributes'].get('environment', 'unknown'),
                'tags': workspace['attributes'].get('tag-names', [])
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get workspace {workspace_name}: {e}")
            raise ValueError(f"Workspace '{workspace_name}' not found: {str(e)}")

    def get_current_state(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current state version for a workspace

        Args:
            workspace_id: Workspace ID

        Returns:
            Current state version information or None
        """
        try:
            url = f"{self.base_url}/workspaces/{workspace_id}/current-state-version"

            response = self.session.get(url, timeout=30)

            if response.status_code == 404:
                return None  # No state yet

            response.raise_for_status()

            data = response.json()
            state = data.get('data')

            if not state:
                return None

            return {
                'id': state['id'],
                'created_at': state['attributes'].get('created-at'),
                'serial': state['attributes'].get('serial'),
                'terraform_version': state['attributes'].get('terraform-version'),
                'hosted_state_download_url': state['attributes'].get('hosted-state-download-url'),
                'modules': state['attributes'].get('modules', {}),
                'providers': state['attributes'].get('providers', {}),
                'resources': state['attributes'].get('resources', []),
                'resource_count': len(state['attributes'].get('resources', []))
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get current state for workspace {workspace_id}: {e}")
            raise ValueError(f"Failed to fetch state: {str(e)}")

    def download_state_file(self, state_download_url: str) -> Dict[str, Any]:
        """
        Download state file from Terraform Cloud

        Args:
            state_download_url: URL to download state file

        Returns:
            State file JSON
        """
        try:
            response = self.session.get(state_download_url, timeout=30)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download state file: {e}")
            raise ValueError(f"Failed to download state file: {str(e)}")

    def list_runs(self, workspace_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        List recent runs for a workspace

        Args:
            workspace_id: Workspace ID
            limit: Maximum number of runs to retrieve

        Returns:
            List of run objects
        """
        try:
            url = f"{self.base_url}/workspaces/{workspace_id}/runs"
            params = {'page[size]': limit}

            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            runs = []

            for run in data.get('data', []):
                runs.append({
                    'id': run['id'],
                    'status': run['attributes'].get('status'),
                    'created_at': run['attributes'].get('created-at'),
                    'message': run['attributes'].get('message'),
                    'has_changes': run['attributes'].get('has-changes', False),
                    'is_destroy': run['attributes'].get('is-destroy', False),
                    'resource_additions': run['attributes'].get('resource-additions', 0),
                    'resource_changes': run['attributes'].get('resource-changes', 0),
                    'resource_destructions': run['attributes'].get('resource-destructions', 0),
                    'terraform_version': run['attributes'].get('terraform-version')
                })

            return runs

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to list runs for workspace {workspace_id}: {e}")
            raise ValueError(f"Failed to fetch runs: {str(e)}")

    def get_workspace_resources(self, workspace_name: str) -> Dict[str, Any]:
        """
        Get comprehensive resource information for a workspace

        Args:
            workspace_name: Name of the workspace

        Returns:
            Dictionary with workspace details, state, and resources
        """
        # Get workspace details
        workspace = self.get_workspace(workspace_name)

        # Get current state
        state_info = self.get_current_state(workspace['id'])

        result = {
            'workspace': workspace,
            'state': state_info,
            'resources': []
        }

        # If state exists and has a download URL, fetch full state
        if state_info and state_info.get('hosted_state_download_url'):
            try:
                full_state = self.download_state_file(state_info['hosted_state_download_url'])

                # Extract resources from state
                if 'resources' in full_state:
                    result['resources'] = full_state['resources']
                elif 'values' in full_state and 'root_module' in full_state['values']:
                    result['resources'] = self._extract_resources_from_state(full_state)

            except Exception as e:
                logger.warning(f"Could not download full state: {e}")

        return result

    def _extract_resources_from_state(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract resource information from Terraform state

        Args:
            state: Full Terraform state JSON

        Returns:
            List of resource objects
        """
        resources = []

        def process_module(module: Dict[str, Any], module_path: str = "root"):
            """Recursively process module resources"""
            for resource in module.get('resources', []):
                resources.append({
                    'type': resource.get('type'),
                    'name': resource.get('name'),
                    'provider': resource.get('provider_name'),
                    'module': module_path,
                    'mode': resource.get('mode', 'managed'),
                    'values': resource.get('values', {}),
                    'address': resource.get('address')
                })

            # Process child modules
            for child_module in module.get('child_modules', []):
                child_path = f"{module_path}.{child_module.get('address', 'unknown')}"
                process_module(child_module, child_path)

        if 'values' in state and 'root_module' in state['values']:
            process_module(state['values']['root_module'])

        return resources

    def get_workspace_variables(self, workspace_id: str) -> List[Dict[str, Any]]:
        """
        Get variables configured for a workspace

        Args:
            workspace_id: Workspace ID

        Returns:
            List of variable objects
        """
        try:
            url = f"{self.base_url}/workspaces/{workspace_id}/vars"

            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            data = response.json()
            variables = []

            for var in data.get('data', []):
                variables.append({
                    'id': var['id'],
                    'key': var['attributes'].get('key'),
                    'value': var['attributes'].get('value') if not var['attributes'].get('sensitive') else '***SENSITIVE***',
                    'category': var['attributes'].get('category'),
                    'sensitive': var['attributes'].get('sensitive', False),
                    'hcl': var['attributes'].get('hcl', False),
                    'description': var['attributes'].get('description')
                })

            return variables

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get workspace variables: {e}")
            raise ValueError(f"Failed to fetch variables: {str(e)}")
