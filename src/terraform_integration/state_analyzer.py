"""Terraform state file analyzer for extracting architectural insights"""

from typing import Dict, List, Any, Set, Tuple
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class TerraformStateAnalyzer:
    """Analyze Terraform state files to extract architectural patterns and insights"""

    def __init__(self):
        """Initialize the state analyzer"""
        self.resource_type_mapping = {
            # AWS Compute
            'aws_instance': 'compute',
            'aws_autoscaling_group': 'compute',
            'aws_launch_template': 'compute',
            'aws_ecs_service': 'compute',
            'aws_ecs_task_definition': 'compute',
            'aws_lambda_function': 'compute',

            # AWS Networking
            'aws_vpc': 'network',
            'aws_subnet': 'network',
            'aws_security_group': 'network',
            'aws_route_table': 'network',
            'aws_internet_gateway': 'network',
            'aws_nat_gateway': 'network',
            'aws_vpc_endpoint': 'network',
            'aws_network_interface': 'network',
            'aws_eip': 'network',

            # AWS Load Balancing
            'aws_lb': 'load_balancer',
            'aws_alb': 'load_balancer',
            'aws_elb': 'load_balancer',
            'aws_lb_target_group': 'load_balancer',
            'aws_lb_listener': 'load_balancer',

            # AWS Database
            'aws_db_instance': 'database',
            'aws_rds_cluster': 'database',
            'aws_dynamodb_table': 'database',
            'aws_elasticache_cluster': 'database',
            'aws_redshift_cluster': 'database',

            # AWS Storage
            'aws_s3_bucket': 'storage',
            'aws_ebs_volume': 'storage',
            'aws_efs_file_system': 'storage',

            # Azure Compute
            'azurerm_virtual_machine': 'compute',
            'azurerm_linux_virtual_machine': 'compute',
            'azurerm_windows_virtual_machine': 'compute',
            'azurerm_container_instance': 'compute',

            # Azure Networking
            'azurerm_virtual_network': 'network',
            'azurerm_subnet': 'network',
            'azurerm_network_security_group': 'network',
            'azurerm_network_interface': 'network',
            'azurerm_public_ip': 'network',

            # Azure Load Balancing
            'azurerm_lb': 'load_balancer',
            'azurerm_application_gateway': 'load_balancer',

            # Azure Database
            'azurerm_sql_server': 'database',
            'azurerm_sql_database': 'database',
            'azurerm_postgresql_server': 'database',
            'azurerm_mysql_server': 'database',
            'azurerm_cosmosdb_account': 'database',

            # Azure Storage
            'azurerm_storage_account': 'storage',
            'azurerm_storage_blob': 'storage',
        }

    def analyze_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze Terraform state file and extract architectural insights

        Args:
            state: Terraform state JSON

        Returns:
            Analysis results with resources, topology, and patterns
        """
        resources = self._extract_resources(state)
        resource_counts = self._count_resources_by_type(resources)
        resource_categories = self._categorize_resources(resources)
        topology = self._build_topology(resources)
        dependencies = self._extract_dependencies(resources)
        modules_used = self._extract_modules(state)
        providers_used = self._extract_providers(state)

        # Calculate metrics
        metrics = self._calculate_metrics(resources, topology)

        # Detect architectural patterns
        patterns = self._detect_patterns(resources, topology, resource_categories)

        # Security analysis
        security_findings = self._analyze_security(resources)

        # Cost estimation categories
        cost_drivers = self._identify_cost_drivers(resources)

        return {
            'summary': {
                'total_resources': len(resources),
                'resource_types': len(resource_counts),
                'modules': len(modules_used),
                'providers': len(providers_used),
                'terraform_version': state.get('terraform_version', 'unknown')
            },
            'resources': resources,
            'resource_counts': resource_counts,
            'resource_categories': resource_categories,
            'topology': topology,
            'dependencies': dependencies,
            'modules': modules_used,
            'providers': providers_used,
            'metrics': metrics,
            'patterns_detected': patterns,
            'security_findings': security_findings,
            'cost_drivers': cost_drivers
        }

    def _extract_resources(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract resources from state file"""
        resources = []

        def process_module(module: Dict[str, Any], module_path: str = "root"):
            for resource in module.get('resources', []):
                resource_data = {
                    'address': resource.get('address'),
                    'type': resource.get('type'),
                    'name': resource.get('name'),
                    'provider': resource.get('provider_name', '').replace('provider["', '').replace('"]', ''),
                    'module': module_path,
                    'mode': resource.get('mode', 'managed'),
                    'values': resource.get('values', {}),
                    'depends_on': resource.get('depends_on', [])
                }
                resources.append(resource_data)

            for child_module in module.get('child_modules', []):
                child_path = child_module.get('address', 'unknown')
                process_module(child_module, child_path)

        if 'values' in state and 'root_module' in state['values']:
            process_module(state['values']['root_module'])
        elif 'resources' in state:
            # Older state format
            for resource in state['resources']:
                resources.append({
                    'address': f"{resource.get('type')}.{resource.get('name')}",
                    'type': resource.get('type'),
                    'name': resource.get('name'),
                    'provider': resource.get('provider', ''),
                    'module': resource.get('module', 'root'),
                    'mode': resource.get('mode', 'managed'),
                    'values': resource.get('instances', [{}])[0].get('attributes', {}),
                    'depends_on': resource.get('depends_on', [])
                })

        return resources

    def _count_resources_by_type(self, resources: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count resources by type"""
        counts = defaultdict(int)
        for resource in resources:
            counts[resource['type']] += 1
        return dict(counts)

    def _categorize_resources(self, resources: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Categorize resources by function"""
        categories = defaultdict(list)

        for resource in resources:
            resource_type = resource['type']
            category = self.resource_type_mapping.get(resource_type, 'other')
            categories[category].append(resource['address'])

        return dict(categories)

    def _build_topology(self, resources: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Build resource topology/relationships"""
        topology = []

        for resource in resources:
            dependencies = resource.get('depends_on', [])

            for dep in dependencies:
                topology.append({
                    'from': resource['address'],
                    'to': dep,
                    'type': 'depends_on'
                })

            # Infer relationships from resource values
            values = resource.get('values', {})

            # Security group to instance relationships
            if resource['type'] in ['aws_instance', 'azurerm_virtual_machine']:
                sg_ids = values.get('vpc_security_group_ids', [])
                for sg_id in sg_ids:
                    topology.append({
                        'from': resource['address'],
                        'to': sg_id,
                        'type': 'uses_security_group'
                    })

                # Subnet relationship
                subnet_id = values.get('subnet_id')
                if subnet_id:
                    topology.append({
                        'from': resource['address'],
                        'to': subnet_id,
                        'type': 'in_subnet'
                    })

            # Load balancer to target group
            if resource['type'] in ['aws_lb', 'aws_alb']:
                # Target groups would be in separate resources

                pass  # Handled by explicit depends_on

        return topology

    def _extract_dependencies(self, resources: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Extract resource dependencies"""
        dependencies = {}

        for resource in resources:
            address = resource['address']
            deps = resource.get('depends_on', [])

            if deps:
                dependencies[address] = deps

        return dependencies

    def _extract_modules(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract module information"""
        modules = []

        def collect_modules(module: Dict[str, Any], parent_path: str = ""):
            current_address = module.get('address', 'root')

            if current_address != 'root':
                modules.append({
                    'address': current_address,
                    'parent': parent_path,
                    'resource_count': len(module.get('resources', []))
                })

            for child_module in module.get('child_modules', []):
                collect_modules(child_module, current_address)

        if 'values' in state and 'root_module' in state['values']:
            collect_modules(state['values']['root_module'])

        return modules

    def _extract_providers(self, state: Dict[str, Any]) -> List[str]:
        """Extract provider information"""
        providers = set()

        if 'values' in state and 'root_module' in state['values']:
            def collect_providers(module: Dict[str, Any]):
                for resource in module.get('resources', []):
                    provider = resource.get('provider_name', '')
                    if provider:
                        # Clean up provider name
                        provider = provider.replace('provider["', '').replace('"]', '')
                        providers.add(provider)

                for child_module in module.get('child_modules', []):
                    collect_providers(child_module)

            collect_providers(state['values']['root_module'])

        return sorted(list(providers))

    def _calculate_metrics(self, resources: List[Dict[str, Any]], topology: List[Dict[str, str]]) -> Dict[str, Any]:
        """Calculate architectural metrics"""
        # Resource complexity
        compute_count = sum(1 for r in resources if self.resource_type_mapping.get(r['type']) == 'compute')
        database_count = sum(1 for r in resources if self.resource_type_mapping.get(r['type']) == 'database')
        network_count = sum(1 for r in resources if self.resource_type_mapping.get(r['type']) == 'network')
        lb_count = sum(1 for r in resources if self.resource_type_mapping.get(r['type']) == 'load_balancer')

        # Dependency complexity
        dependency_count = len(topology)

        # Module usage
        modules_in_use = len(set(r['module'] for r in resources if r['module'] != 'root'))

        return {
            'resource_counts': {
                'compute': compute_count,
                'database': database_count,
                'network': network_count,
                'load_balancer': lb_count,
                'total': len(resources)
            },
            'complexity': {
                'dependency_count': dependency_count,
                'module_count': modules_in_use,
                'avg_dependencies_per_resource': dependency_count / len(resources) if resources else 0
            }
        }

    def _detect_patterns(
        self,
        resources: List[Dict[str, Any]],
        topology: List[Dict[str, str]],
        categories: Dict[str, List[str]]
    ) -> List[Dict[str, Any]]:
        """Detect architectural patterns in the infrastructure"""
        patterns = []

        # Multi-tier architecture detection
        has_lb = len(categories.get('load_balancer', [])) > 0
        has_compute = len(categories.get('compute', [])) > 0
        has_database = len(categories.get('database', [])) > 0

        if has_lb and has_compute and has_database:
            patterns.append({
                'name': 'Multi-Tier Architecture',
                'confidence': 0.9,
                'description': 'Infrastructure includes load balancers, compute resources, and databases'
            })

        # High availability detection
        compute_count = len(categories.get('compute', []))
        database_resources = [r for r in resources if self.resource_type_mapping.get(r['type']) == 'database']

        multi_az_databases = sum(
            1 for db in database_resources
            if db.get('values', {}).get('multi_az') or
               db.get('values', {}).get('availability_zone_mode') == 'multi-az'
        )

        if compute_count >= 2 or multi_az_databases > 0:
            patterns.append({
                'name': 'High Availability Configuration',
                'confidence': 0.8,
                'description': f'Multiple compute instances ({compute_count}) or Multi-AZ databases ({multi_az_databases})'
            })

        # Microservices pattern detection
        if len(categories.get('compute', [])) >= 3 and len(categories.get('load_balancer', [])) >= 1:
            patterns.append({
                'name': 'Microservices Pattern',
                'confidence': 0.7,
                'description': 'Multiple compute resources behind load balancers suggest microservices architecture'
            })

        return patterns

    def _analyze_security(self, resources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze security configuration"""
        findings = []

        # Check for publicly accessible databases
        for resource in resources:
            if self.resource_type_mapping.get(resource['type']) == 'database':
                values = resource.get('values', {})

                if values.get('publicly_accessible') is True:
                    findings.append({
                        'severity': 'high',
                        'resource': resource['address'],
                        'finding': 'Database is publicly accessible',
                        'recommendation': 'Set publicly_accessible to false for production databases'
                    })

        # Check for security groups with overly permissive rules
        for resource in resources:
            if resource['type'] in ['aws_security_group', 'azurerm_network_security_group']:
                values = resource.get('values', {})
                ingress_rules = values.get('ingress', [])

                for rule in ingress_rules:
                    if isinstance(rule, dict):
                        cidr_blocks = rule.get('cidr_blocks', [])
                        if '0.0.0.0/0' in cidr_blocks:
                            findings.append({
                                'severity': 'medium',
                                'resource': resource['address'],
                                'finding': 'Security group allows traffic from 0.0.0.0/0',
                                'recommendation': 'Restrict source IP ranges to known addresses'
                            })

        # Check for unencrypted storage
        for resource in resources:
            if resource['type'] in ['aws_db_instance', 'aws_rds_cluster']:
                values = resource.get('values', {})

                if not values.get('storage_encrypted'):
                    findings.append({
                        'severity': 'high',
                        'resource': resource['address'],
                        'finding': 'Database storage is not encrypted',
                        'recommendation': 'Enable storage_encrypted for data at rest encryption'
                    })

        return findings

    def _identify_cost_drivers(self, resources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify major cost drivers in the infrastructure"""
        cost_categories = {
            'compute': [],
            'database': [],
            'storage': [],
            'network': []
        }

        for resource in resources:
            category = self.resource_type_mapping.get(resource['type'], 'other')

            if category in cost_categories:
                values = resource.get('values', {})
                cost_info = {
                    'resource': resource['address'],
                    'type': resource['type']
                }

                # Add relevant cost-related attributes
                if category == 'compute':
                    cost_info['instance_type'] = values.get('instance_type') or values.get('vm_size')

                elif category == 'database':
                    cost_info['instance_class'] = values.get('instance_class') or values.get('sku_name')
                    cost_info['storage_gb'] = values.get('allocated_storage')

                elif category == 'storage':
                    cost_info['storage_class'] = values.get('storage_class') or values.get('account_tier')

                cost_categories[category].append(cost_info)

        return {
            'categories': cost_categories,
            'summary': {
                'compute_instances': len(cost_categories['compute']),
                'databases': len(cost_categories['database']),
                'storage_resources': len(cost_categories['storage'])
            }
        }

    def get_validation_context(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert state analysis to validation context format

        Args:
            analysis: Output from analyze_state()

        Returns:
            Context dict suitable for validation engine
        """
        return {
            'source_type': 'terraform_state',
            'resources': analysis['resources'],
            'topology': analysis['topology'],
            'metadata': {
                'terraform_version': analysis['summary']['terraform_version'],
                'total_resources': analysis['summary']['total_resources'],
                'providers': analysis['providers'],
                'modules': analysis['modules']
            },
            'environment': self._infer_environment(analysis['resources']),
            'resource_categories': analysis['resource_categories']
        }

    def _infer_environment(self, resources: List[Dict[str, Any]]) -> str:
        """Infer environment (dev/staging/prod) from resource names and tags"""
        env_keywords = {
            'prod': ['prod', 'production', 'prd'],
            'staging': ['staging', 'stage', 'stg'],
            'dev': ['dev', 'development', 'test']
        }

        env_scores = defaultdict(int)

        for resource in resources:
            name = resource.get('name', '').lower()
            tags = resource.get('values', {}).get('tags', {})
            env_tag = str(tags.get('environment', '') or tags.get('Environment', '')).lower()

            # Check name
            for env, keywords in env_keywords.items():
                if any(keyword in name for keyword in keywords):
                    env_scores[env] += 1

            # Check tags (higher weight)
            for env, keywords in env_keywords.items():
                if any(keyword in env_tag for keyword in keywords):
                    env_scores[env] += 3

        if env_scores:
            return max(env_scores, key=env_scores.get)

        return 'unknown'
