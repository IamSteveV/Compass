"""ServiceNow CMDB connector for API integration"""

import requests
from typing import List, Dict, Any, Optional
from requests.auth import HTTPBasicAuth
import logging

from ..config import get_settings
from ..models import CMDBConfigurationItem, CMDBRelationship, CMDBApplication

logger = logging.getLogger(__name__)


class ServiceNowConnector:
    """Connector for ServiceNow CMDB API"""

    def __init__(self, instance_url: Optional[str] = None,
                 username: Optional[str] = None,
                 password: Optional[str] = None):
        """
        Initialize ServiceNow connector.

        Args:
            instance_url: ServiceNow instance URL (e.g., https://company.service-now.com)
            username: API username
            password: API password
        """
        settings = get_settings()
        self.instance_url = instance_url or settings.servicenow.instance_url
        self.username = username or settings.servicenow.api_user
        self.password = password or settings.servicenow.api_password
        self.timeout = settings.servicenow.timeout
        self.verify_ssl = settings.servicenow.verify_ssl

        # Remove trailing slash from URL
        self.instance_url = self.instance_url.rstrip('/')

        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(self.username, self.password)
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make HTTP request to ServiceNow API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments for requests

        Returns:
            JSON response as dictionary

        Raises:
            requests.HTTPError: If request fails
        """
        url = f"{self.instance_url}{endpoint}"

        kwargs.setdefault('timeout', self.timeout)
        kwargs.setdefault('verify', self.verify_ssl)

        logger.debug(f"Making {method} request to {url}")

        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request to {url} failed: {e}")
            raise

    def get_configuration_items(self, query: Optional[str] = None,
                                table: str = "cmdb_ci",
                                limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get configuration items from CMDB.

        Args:
            query: ServiceNow query string
            table: CMDB table name
            limit: Maximum number of results

        Returns:
            List of configuration items
        """
        params = {
            'sysparm_limit': limit,
        }
        if query:
            params['sysparm_query'] = query

        endpoint = f"/api/now/table/{table}"
        response = self._make_request('GET', endpoint, params=params)

        return response.get('result', [])

    def get_servers(self, application_id: Optional[str] = None,
                   environment: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get server CIs from CMDB.

        Args:
            application_id: Filter by application sys_id
            environment: Filter by environment

        Returns:
            List of server CIs
        """
        query_parts = []
        if application_id:
            query_parts.append(f"application={application_id}")
        if environment:
            query_parts.append(f"u_environment={environment}")

        query = '^'.join(query_parts) if query_parts else None

        return self.get_configuration_items(query=query, table="cmdb_ci_server")

    def get_databases(self, application_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get database CIs from CMDB.

        Args:
            application_id: Filter by application sys_id

        Returns:
            List of database CIs
        """
        query = f"application={application_id}" if application_id else None
        return self.get_configuration_items(query=query, table="cmdb_ci_database")

    def get_application(self, app_id: str) -> Optional[Dict[str, Any]]:
        """
        Get application details by sys_id.

        Args:
            app_id: Application sys_id

        Returns:
            Application details or None if not found
        """
        endpoint = f"/api/now/table/cmdb_ci_appl/{app_id}"
        try:
            response = self._make_request('GET', endpoint)
            return response.get('result')
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise

    def get_applications(self, name_filter: Optional[str] = None,
                        limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get list of applications.

        Args:
            name_filter: Filter applications by name (contains)
            limit: Maximum number of results

        Returns:
            List of applications
        """
        query = f"nameLIKE{name_filter}" if name_filter else None
        return self.get_configuration_items(query=query, table="cmdb_ci_appl", limit=limit)

    def get_relationships(self, ci_id: str) -> List[Dict[str, Any]]:
        """
        Get relationships for a configuration item.

        Args:
            ci_id: Configuration item sys_id

        Returns:
            List of relationships
        """
        query = f"parent={ci_id}^ORchild={ci_id}"
        endpoint = "/api/now/table/cmdb_rel_ci"
        params = {
            'sysparm_query': query,
            'sysparm_limit': 1000
        }

        response = self._make_request('GET', endpoint, params=params)
        return response.get('result', [])

    def get_ci_by_id(self, ci_id: str, table: str = "cmdb_ci") -> Optional[Dict[str, Any]]:
        """
        Get a configuration item by sys_id.

        Args:
            ci_id: Configuration item sys_id
            table: CMDB table name

        Returns:
            Configuration item details or None if not found
        """
        endpoint = f"/api/now/table/{table}/{ci_id}"
        try:
            response = self._make_request('GET', endpoint)
            return response.get('result')
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise

    def search_cis(self, name: str, ci_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for configuration items by name.

        Args:
            name: Name to search for
            ci_type: Optional CI type filter

        Returns:
            List of matching CIs
        """
        query = f"nameLIKE{name}"
        table = "cmdb_ci"

        if ci_type:
            if ci_type.lower() == "server":
                table = "cmdb_ci_server"
            elif ci_type.lower() == "database":
                table = "cmdb_ci_database"
            elif ci_type.lower() == "application":
                table = "cmdb_ci_appl"

        return self.get_configuration_items(query=query, table=table)
