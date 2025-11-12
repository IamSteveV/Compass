"""High-level CMDB client for validation operations"""

from typing import List, Dict, Any, Optional
import logging

from .connector import ServiceNowConnector
from ..models import (
    CMDBConfigurationItem,
    CMDBRelationship,
    CMDBApplication
)

logger = logging.getLogger(__name__)


class CMDBClient:
    """High-level client for CMDB operations"""

    def __init__(self, connector: Optional[ServiceNowConnector] = None):
        """
        Initialize CMDB client.

        Args:
            connector: ServiceNow connector instance (creates new if not provided)
        """
        self.connector = connector or ServiceNowConnector()

    def get_application_topology(self, app_id: str) -> CMDBApplication:
        """
        Get complete application topology including all CIs and relationships.

        Args:
            app_id: Application sys_id or name

        Returns:
            CMDBApplication with all related CIs and relationships
        """
        # Get application details
        if len(app_id) == 32:  # Looks like sys_id
            app_data = self.connector.get_application(app_id)
        else:  # Search by name
            apps = self.connector.get_applications(name_filter=app_id, limit=1)
            app_data = apps[0] if apps else None

        if not app_data:
            raise ValueError(f"Application not found: {app_id}")

        app_sys_id = app_data['sys_id']
        app_name = app_data.get('name', app_id)

        logger.info(f"Fetching topology for application: {app_name} ({app_sys_id})")

        # Get all related CIs
        configuration_items = []

        # Get servers
        servers = self.connector.get_servers(application_id=app_sys_id)
        for server in servers:
            ci = self._parse_ci(server, 'server')
            if ci:
                configuration_items.append(ci)

        # Get databases
        databases = self.connector.get_databases(application_id=app_sys_id)
        for db in databases:
            ci = self._parse_ci(db, 'database')
            if ci:
                configuration_items.append(ci)

        # Get relationships for each CI
        all_relationships = []
        ci_ids = {ci.sys_id for ci in configuration_items}

        for ci in configuration_items:
            rels = self.connector.get_relationships(ci.sys_id)
            for rel in rels:
                relationship = self._parse_relationship(rel)
                if relationship:
                    all_relationships.append(relationship)

        logger.info(f"Found {len(configuration_items)} CIs and {len(all_relationships)} relationships")

        return CMDBApplication(
            sys_id=app_sys_id,
            name=app_name,
            description=app_data.get('short_description', ''),
            configuration_items=configuration_items,
            relationships=all_relationships
        )

    def _parse_ci(self, ci_data: Dict[str, Any], ci_type: str) -> Optional[CMDBConfigurationItem]:
        """Parse raw CI data into CMDBConfigurationItem model"""
        try:
            return CMDBConfigurationItem(
                sys_id=ci_data['sys_id'],
                name=ci_data.get('name', ''),
                type=ci_type,
                environment=ci_data.get('u_environment', ci_data.get('environment', '')),
                tier=ci_data.get('u_tier', ci_data.get('tier', '')),
                business_owner=ci_data.get('owned_by', ci_data.get('business_owner', '')),
                technical_owner=ci_data.get('managed_by', ci_data.get('technical_owner', '')),
                data_classification=ci_data.get('u_data_classification',
                                               ci_data.get('data_classification', '')),
                properties={
                    'encrypted': ci_data.get('encrypted', False),
                    'backup_enabled': ci_data.get('backup_enabled', False),
                    'multi_az': ci_data.get('multi_az', False),
                    'instance_type': ci_data.get('instance_type', ''),
                    'version': ci_data.get('version', ''),
                    **{k: v for k, v in ci_data.items()
                       if k not in ['sys_id', 'name', 'u_environment', 'environment',
                                   'u_tier', 'tier', 'owned_by', 'managed_by',
                                   'u_data_classification', 'data_classification']}
                }
            )
        except KeyError as e:
            logger.warning(f"Failed to parse CI {ci_data.get('sys_id', 'unknown')}: {e}")
            return None

    def _parse_relationship(self, rel_data: Dict[str, Any]) -> Optional[CMDBRelationship]:
        """Parse raw relationship data into CMDBRelationship model"""
        try:
            parent_id = rel_data['parent']['value'] if isinstance(rel_data.get('parent'), dict) \
                else rel_data.get('parent', '')
            child_id = rel_data['child']['value'] if isinstance(rel_data.get('child'), dict) \
                else rel_data.get('child', '')

            rel_type_data = rel_data.get('type', {})
            rel_type = rel_type_data.get('display_value', 'unknown') \
                if isinstance(rel_type_data, dict) else str(rel_type_data)

            return CMDBRelationship(
                parent_id=parent_id,
                child_id=child_id,
                relationship_type=rel_type
            )
        except (KeyError, TypeError) as e:
            logger.warning(f"Failed to parse relationship: {e}")
            return None

    def get_topology_for_validation(self, app_id: str) -> Dict[str, Any]:
        """
        Get application topology formatted for validation.

        Returns a dictionary with resources and context suitable for validation engine.

        Args:
            app_id: Application sys_id or name

        Returns:
            Dictionary with 'resources', 'relationships', and 'topology' for validation
        """
        app = self.get_application_topology(app_id)

        # Convert CIs to dict format for validation
        resources = []
        for ci in app.configuration_items:
            resource = {
                'id': ci.sys_id,
                'name': ci.name,
                'type': ci.type,
                'environment': ci.environment,
                'tier': ci.tier,
                'business_owner': ci.business_owner,
                'technical_owner': ci.technical_owner,
                'data_classification': ci.data_classification,
                **ci.properties
            }
            resources.append(resource)

        # Build topology (network connections)
        topology = []
        for rel in app.relationships:
            # Find parent and child CIs
            parent_ci = next((ci for ci in app.configuration_items
                            if ci.sys_id == rel.parent_id), None)
            child_ci = next((ci for ci in app.configuration_items
                           if ci.sys_id == rel.child_id), None)

            if parent_ci and child_ci:
                connection = {
                    'source': parent_ci.name,
                    'source_tier': parent_ci.tier,
                    'source_zone': parent_ci.properties.get('zone', ''),
                    'target': child_ci.name,
                    'target_tier': child_ci.tier,
                    'target_zone': child_ci.properties.get('zone', ''),
                    'relationship_type': rel.relationship_type
                }
                topology.append(connection)

        # Format relationships for context
        relationships_list = [
            {
                'parent_id': rel.parent_id,
                'child_id': rel.child_id,
                'relationship_type': rel.relationship_type
            }
            for rel in app.relationships
        ]

        return {
            'resources': resources,
            'relationships': relationships_list,
            'topology': topology,
            'source_type': 'cmdb',
            'source_identifier': app.name
        }
