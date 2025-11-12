"""Terraform resource graph generator for visualization"""

from typing import Dict, List, Any, Set
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class TerraformResourceGraph:
    """Generate visual graphs from Terraform resources"""

    def __init__(self):
        """Initialize the resource graph generator"""
        self.node_colors = {
            'compute': '#3498db',  # Blue
            'database': '#e74c3c',  # Red
            'network': '#2ecc71',  # Green
            'load_balancer': '#f39c12',  # Orange
            'storage': '#9b59b6',  # Purple
            'other': '#95a5a6'  # Gray
        }

        self.resource_type_mapping = {
            # AWS
            'aws_instance': 'compute',
            'aws_db_instance': 'database',
            'aws_lb': 'load_balancer',
            'aws_alb': 'load_balancer',
            'aws_elb': 'load_balancer',
            'aws_vpc': 'network',
            'aws_subnet': 'network',
            'aws_security_group': 'network',
            'aws_s3_bucket': 'storage',
            'aws_ebs_volume': 'storage',
            # Azure
            'azurerm_virtual_machine': 'compute',
            'azurerm_sql_database': 'database',
            'azurerm_lb': 'load_balancer',
            'azurerm_virtual_network': 'network',
            'azurerm_storage_account': 'storage',
        }

    def generate_mermaid_diagram(
        self,
        resources: List[Dict[str, Any]],
        topology: List[Dict[str, str]]
    ) -> str:
        """
        Generate Mermaid diagram from Terraform resources

        Args:
            resources: List of resource objects
            topology: List of relationship objects

        Returns:
            Mermaid diagram as string
        """
        diagram = ["graph TB"]

        # Create node ID mapping
        node_ids = {}
        for i, resource in enumerate(resources):
            node_id = f"node{i}"
            node_ids[resource['address']] = node_id

            # Get resource category for styling
            category = self.resource_type_mapping.get(resource['type'], 'other')

            # Create label
            label = f"{resource['type']}<br/>{resource['name']}"

            # Add node with styling
            diagram.append(f'    {node_id}["{label}"]')

            # Add styling class
            diagram.append(f'    class {node_id} {category}')

        # Add relationships
        for relation in topology:
            from_address = relation['from']
            to_address = relation['to']

            from_id = node_ids.get(from_address)
            to_id = node_ids.get(to_address)

            if from_id and to_id:
                rel_type = relation.get('type', '')
                diagram.append(f'    {from_id} -->|{rel_type}| {to_id}')

        # Add style definitions
        diagram.append("")
        diagram.append("    classDef compute fill:#3498db,stroke:#2980b9,color:#fff")
        diagram.append("    classDef database fill:#e74c3c,stroke:#c0392b,color:#fff")
        diagram.append("    classDef network fill:#2ecc71,stroke:#27ae60,color:#fff")
        diagram.append("    classDef load_balancer fill:#f39c12,stroke:#e67e22,color:#fff")
        diagram.append("    classDef storage fill:#9b59b6,stroke:#8e44ad,color:#fff")
        diagram.append("    classDef other fill:#95a5a6,stroke:#7f8c8d,color:#fff")

        return "\n".join(diagram)

    def generate_graphviz_dot(
        self,
        resources: List[Dict[str, Any]],
        topology: List[Dict[str, str]]
    ) -> str:
        """
        Generate Graphviz DOT format diagram

        Args:
            resources: List of resource objects
            topology: List of relationship objects

        Returns:
            DOT format diagram as string
        """
        lines = ["digraph TerraformResources {"]
        lines.append("    rankdir=TB;")
        lines.append("    node [shape=box, style=filled];")
        lines.append("")

        # Create nodes
        for resource in resources:
            address = resource['address']
            resource_type = resource['type']
            name = resource['name']

            category = self.resource_type_mapping.get(resource_type, 'other')
            color = self.node_colors.get(category, '#95a5a6')

            # Escape special characters
            safe_address = address.replace('.', '_').replace('[', '_').replace(']', '_')
            label = f"{resource_type}\\n{name}"

            lines.append(f'    "{safe_address}" [label="{label}", fillcolor="{color}", fontcolor="white"];')

        lines.append("")

        # Create edges
        for relation in topology:
            from_address = relation['from'].replace('.', '_').replace('[', '_').replace(']', '_')
            to_address = relation['to'].replace('.', '_').replace('[', '_').replace(']', '_')
            rel_type = relation.get('type', '')

            lines.append(f'    "{from_address}" -> "{to_address}" [label="{rel_type}"];')

        lines.append("}")

        return "\n".join(lines)

    def generate_network_json(
        self,
        resources: List[Dict[str, Any]],
        topology: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Generate network graph in JSON format (for D3.js, Cytoscape.js, etc.)

        Args:
            resources: List of resource objects
            topology: List of relationship objects

        Returns:
            Network graph as dict with nodes and edges
        """
        nodes = []
        edges = []

        # Create nodes
        for resource in resources:
            category = self.resource_type_mapping.get(resource['type'], 'other')
            color = self.node_colors.get(category, '#95a5a6')

            nodes.append({
                'id': resource['address'],
                'label': f"{resource['type']}.{resource['name']}",
                'type': resource['type'],
                'category': category,
                'color': color,
                'module': resource.get('module', 'root'),
                'provider': resource.get('provider', 'unknown')
            })

        # Create edges
        for relation in topology:
            edges.append({
                'source': relation['from'],
                'target': relation['to'],
                'type': relation.get('type', 'depends_on')
            })

        return {
            'nodes': nodes,
            'edges': edges
        }

    def generate_hierarchy_json(self, resources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate hierarchical tree structure grouped by modules

        Args:
            resources: List of resource objects

        Returns:
            Hierarchical structure
        """
        # Group by module
        modules = defaultdict(list)

        for resource in resources:
            module_path = resource.get('module', 'root')
            modules[module_path].append({
                'id': resource['address'],
                'name': resource['name'],
                'type': resource['type'],
                'category': self.resource_type_mapping.get(resource['type'], 'other')
            })

        # Build tree structure
        tree = {
            'name': 'root',
            'children': []
        }

        for module_path, module_resources in modules.items():
            if module_path == 'root':
                tree['children'].extend(module_resources)
            else:
                tree['children'].append({
                    'name': module_path,
                    'type': 'module',
                    'children': module_resources
                })

        return tree

    def generate_summary_stats(
        self,
        resources: List[Dict[str, Any]],
        topology: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Generate summary statistics about the resource graph

        Args:
            resources: List of resource objects
            topology: List of relationship objects

        Returns:
            Summary statistics
        """
        # Count by category
        category_counts = defaultdict(int)
        for resource in resources:
            category = self.resource_type_mapping.get(resource['type'], 'other')
            category_counts[category] += 1

        # Count by provider
        provider_counts = defaultdict(int)
        for resource in resources:
            provider = resource.get('provider', 'unknown')
            provider_counts[provider] += 1

        # Count by module
        module_counts = defaultdict(int)
        for resource in resources:
            module = resource.get('module', 'root')
            module_counts[module] += 1

        # Calculate connectivity metrics
        resource_addresses = {r['address'] for r in resources}
        connected_resources = set()

        for relation in topology:
            connected_resources.add(relation['from'])
            connected_resources.add(relation['to'])

        connectivity_ratio = len(connected_resources) / len(resources) if resources else 0

        # Find most connected resources
        connection_counts = defaultdict(int)
        for relation in topology:
            connection_counts[relation['from']] += 1
            connection_counts[relation['to']] += 1

        most_connected = sorted(
            connection_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        return {
            'total_resources': len(resources),
            'total_relationships': len(topology),
            'by_category': dict(category_counts),
            'by_provider': dict(provider_counts),
            'by_module': dict(module_counts),
            'connectivity_ratio': round(connectivity_ratio, 2),
            'most_connected_resources': [
                {'resource': addr, 'connections': count}
                for addr, count in most_connected
            ]
        }

    def get_resource_dependencies(
        self,
        resource_address: str,
        topology: List[Dict[str, str]]
    ) -> Dict[str, List[str]]:
        """
        Get dependencies for a specific resource

        Args:
            resource_address: Address of the resource
            topology: List of relationship objects

        Returns:
            Dict with 'depends_on' and 'depended_by' lists
        """
        depends_on = []
        depended_by = []

        for relation in topology:
            if relation['from'] == resource_address:
                depends_on.append(relation['to'])

            if relation['to'] == resource_address:
                depended_by.append(relation['from'])

        return {
            'depends_on': depends_on,
            'depended_by': depended_by
        }

    def find_circular_dependencies(
        self,
        resources: List[Dict[str, Any]],
        topology: List[Dict[str, str]]
    ) -> List[List[str]]:
        """
        Find circular dependencies in the resource graph

        Args:
            resources: List of resource objects
            topology: List of relationship objects

        Returns:
            List of circular dependency chains
        """
        # Build adjacency list
        graph = defaultdict(list)
        for relation in topology:
            graph[relation['from']].append(relation['to'])

        # DFS to find cycles
        visited = set()
        rec_stack = set()
        cycles = []

        def dfs(node: str, path: List[str]):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph[node]:
                if neighbor not in visited:
                    dfs(neighbor, path.copy())
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)

            rec_stack.remove(node)

        for resource in resources:
            address = resource['address']
            if address not in visited:
                dfs(address, [])

        return cycles
