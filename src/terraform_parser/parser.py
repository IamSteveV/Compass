"""Parser for Terraform JSON plan files"""

import json
from typing import Dict, Any, List, Optional
import logging
from pathlib import Path

from ..models import TerraformPlan, TerraformResource
from ..config import get_settings

logger = logging.getLogger(__name__)


class TerraformParser:
    """Parser for Terraform JSON plan output"""

    def __init__(self):
        self.settings = get_settings()

    def parse_plan_file(self, file_path: str) -> TerraformPlan:
        """
        Parse Terraform plan JSON file.

        Args:
            file_path: Path to terraform plan JSON file

        Returns:
            TerraformPlan object

        Raises:
            ValueError: If file is invalid or too large
            FileNotFoundError: If file doesn't exist
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Terraform plan file not found: {file_path}")

        # Check file size
        file_size_mb = path.stat().st_size / (1024 * 1024)
        if file_size_mb > self.settings.terraform.max_file_size_mb:
            raise ValueError(
                f"Terraform plan file too large: {file_size_mb:.2f}MB "
                f"(max: {self.settings.terraform.max_file_size_mb}MB)"
            )

        logger.info(f"Parsing Terraform plan file: {file_path} ({file_size_mb:.2f}MB)")

        with open(file_path, 'r') as f:
            plan_data = json.load(f)

        return self.parse_plan_data(plan_data)

    def parse_plan_data(self, plan_data: Dict[str, Any]) -> TerraformPlan:
        """
        Parse Terraform plan data dictionary.

        Args:
            plan_data: Terraform plan as dictionary (from JSON)

        Returns:
            TerraformPlan object
        """
        # Extract terraform version
        terraform_version = plan_data.get('terraform_version', 'unknown')

        # Parse resources from planned_values and resource_changes
        resources = []

        # Get resources from planned_values (final state)
        if 'planned_values' in plan_data and 'root_module' in plan_data['planned_values']:
            root_module = plan_data['planned_values']['root_module']
            resources.extend(self._parse_resources_from_module(root_module))

        # Get resource changes (for change actions)
        if 'resource_changes' in plan_data:
            self._add_change_actions(resources, plan_data['resource_changes'])

        # Parse variables
        variables = {}
        if 'variables' in plan_data:
            variables = {k: v.get('value') for k, v in plan_data['variables'].items()}

        # Parse outputs
        outputs = {}
        if 'planned_values' in plan_data and 'outputs' in plan_data['planned_values']:
            outputs = {k: v.get('value') for k, v in plan_data['planned_values']['outputs'].items()}

        logger.info(f"Parsed {len(resources)} resources from Terraform plan")

        return TerraformPlan(
            terraform_version=terraform_version,
            resources=resources,
            variables=variables,
            outputs=outputs
        )

    def _parse_resources_from_module(self, module: Dict[str, Any],
                                     module_path: str = "") -> List[TerraformResource]:
        """
        Recursively parse resources from a Terraform module.

        Args:
            module: Module data from Terraform plan
            module_path: Path to this module (for nested modules)

        Returns:
            List of TerraformResource objects
        """
        resources = []

        # Parse resources in this module
        if 'resources' in module:
            for resource_data in module['resources']:
                resource = self._parse_resource(resource_data, module_path)
                if resource:
                    resources.append(resource)

        # Parse child modules recursively
        if 'child_modules' in module:
            for child_module in module['child_modules']:
                child_path = child_module.get('address', '')
                resources.extend(self._parse_resources_from_module(child_module, child_path))

        return resources

    def _parse_resource(self, resource_data: Dict[str, Any],
                       module_path: str = "") -> Optional[TerraformResource]:
        """Parse a single Terraform resource"""
        try:
            address = resource_data.get('address', '')
            if module_path:
                address = f"{module_path}.{address}"

            # Extract provider from address or use default
            provider = resource_data.get('provider_name', 'unknown')

            # Parse resource type and name from address
            # Format: resource_type.resource_name or module.name.resource_type.resource_name
            parts = address.split('.')
            if len(parts) >= 2:
                resource_type = parts[-2] if not parts[-2].startswith('module') else parts[-1]
                resource_name = parts[-1]
            else:
                resource_type = resource_data.get('type', 'unknown')
                resource_name = resource_data.get('name', 'unknown')

            values = resource_data.get('values', {})

            return TerraformResource(
                address=address,
                type=resource_type,
                name=resource_name,
                provider=provider,
                values=values,
                change_action=None  # Will be filled in by _add_change_actions
            )
        except Exception as e:
            logger.warning(f"Failed to parse resource: {e}")
            return None

    def _add_change_actions(self, resources: List[TerraformResource],
                           resource_changes: List[Dict[str, Any]]) -> None:
        """
        Add change action information to resources.

        Args:
            resources: List of parsed resources
            resource_changes: Resource changes from Terraform plan
        """
        # Create mapping of address to change action
        change_map = {}
        for change in resource_changes:
            address = change.get('address', '')
            actions = change.get('change', {}).get('actions', [])

            # Determine primary action
            if 'create' in actions:
                action = 'create'
            elif 'delete' in actions:
                action = 'delete'
            elif 'update' in actions:
                action = 'update'
            else:
                action = 'no-op'

            change_map[address] = action

        # Apply actions to resources
        for resource in resources:
            if resource.address in change_map:
                resource.change_action = change_map[resource.address]

    def get_resources_for_validation(self, plan: TerraformPlan) -> Dict[str, Any]:
        """
        Convert Terraform plan to format suitable for validation.

        Args:
            plan: Parsed Terraform plan

        Returns:
            Dictionary with 'resources', 'topology', etc. for validation engine
        """
        # Convert resources to validation format
        resources = []
        for tf_resource in plan.resources:
            # Extract common properties
            resource = {
                'id': tf_resource.address,
                'name': tf_resource.name,
                'type': self._normalize_resource_type(tf_resource.type),
                'provider': tf_resource.provider,
                'change_action': tf_resource.change_action,
                **tf_resource.values
            }

            # Extract specific properties based on resource type
            resource_type = tf_resource.type.lower()

            # Database resources
            if any(db in resource_type for db in ['db_instance', 'database', 'rds']):
                resource['encrypted'] = tf_resource.values.get('storage_encrypted', False)
                resource['backup_enabled'] = tf_resource.values.get('backup_retention_period', 0) > 0
                resource['backup_retention_days'] = tf_resource.values.get('backup_retention_period', 0)
                resource['multi_az'] = tf_resource.values.get('multi_az', False)
                resource['version'] = tf_resource.values.get('engine_version', '')

            # Compute resources
            if any(compute in resource_type for compute in ['instance', 'virtual_machine', 'compute']):
                resource['instance_type'] = tf_resource.values.get('instance_type',
                                           tf_resource.values.get('size', ''))
                zones = tf_resource.values.get('availability_zones', [])
                resource['availability_zones'] = zones if isinstance(zones, list) else [zones]
                resource['multi_az'] = len(resource['availability_zones']) > 1

            # Extract tags for metadata
            tags = tf_resource.values.get('tags', {})
            if tags:
                resource['environment'] = tags.get('Environment', tags.get('environment', ''))
                resource['tier'] = tags.get('Tier', tags.get('tier', ''))
                resource['business_owner'] = tags.get('Owner', tags.get('owner', ''))
                resource['technical_owner'] = tags.get('TechnicalOwner', tags.get('technical_owner', ''))
                resource['data_classification'] = tags.get('DataClassification',
                                                          tags.get('data_classification', ''))

            resources.append(resource)

        # Build topology from resource dependencies
        topology = self._extract_topology(plan)

        return {
            'resources': resources,
            'topology': topology,
            'source_type': 'terraform',
            'source_identifier': f"Terraform Plan v{plan.terraform_version}"
        }

    def _normalize_resource_type(self, tf_type: str) -> str:
        """
        Normalize Terraform resource type to generic type.

        Args:
            tf_type: Terraform resource type (e.g., aws_db_instance)

        Returns:
            Normalized type (e.g., database)
        """
        tf_type_lower = tf_type.lower()

        # Database types
        if any(db in tf_type_lower for db in ['db_instance', 'database', 'rds', 'sql']):
            return 'database'

        # Compute types
        if any(compute in tf_type_lower for compute in ['instance', 'virtual_machine', 'vm', 'compute']):
            return 'server'

        # Network types
        if any(net in tf_type_lower for net in ['vpc', 'subnet', 'network', 'security_group']):
            return 'network'

        # Load balancer types
        if any(lb in tf_type_lower for lb in ['lb', 'load_balancer', 'elb', 'alb']):
            return 'load_balancer'

        return tf_type

    def _extract_topology(self, plan: TerraformPlan) -> List[Dict[str, Any]]:
        """
        Extract network topology from Terraform plan.

        This is a simplified version - in production, you'd parse depends_on,
        security groups, network rules, etc.

        Args:
            plan: Terraform plan

        Returns:
            List of topology connections
        """
        topology = []

        # Group resources by tier (from tags)
        tiers = {}
        for resource in plan.resources:
            tags = resource.values.get('tags', {})
            tier = tags.get('Tier', tags.get('tier', 'unknown'))
            if tier not in tiers:
                tiers[tier] = []
            tiers[tier].append(resource)

        # Create connections between tiers (simplified)
        tier_list = list(tiers.keys())
        for i, source_tier in enumerate(tier_list):
            if i < len(tier_list) - 1:
                target_tier = tier_list[i + 1]

                for source_res in tiers[source_tier][:1]:  # Sample one resource
                    for target_res in tiers[target_tier][:1]:
                        topology.append({
                            'source': source_res.name,
                            'source_tier': source_tier,
                            'target': target_res.name,
                            'target_tier': target_tier
                        })

        return topology
