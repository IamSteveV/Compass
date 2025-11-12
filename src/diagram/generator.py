"""Generate architecture diagrams from infrastructure data"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

try:
    from graphviz import Digraph
    GRAPHVIZ_AVAILABLE = True
except ImportError:
    GRAPHVIZ_AVAILABLE = False
    logging.warning("Graphviz not available. Install with: pip install graphviz")

logger = logging.getLogger(__name__)


class DiagramGenerator:
    """Generate architecture diagrams from validation data"""

    def __init__(self):
        if not GRAPHVIZ_AVAILABLE:
            raise ImportError("Graphviz is required for diagram generation")

    def generate_topology_diagram(
        self,
        resources: List[Dict[str, Any]],
        topology: List[Dict[str, Any]],
        output_path: str,
        format: str = 'png',
        violations: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Generate network topology diagram.

        Args:
            resources: List of infrastructure resources
            topology: List of network connections
            output_path: Output file path (without extension)
            format: Output format (png, svg, pdf)
            violations: Optional list of violations to highlight

        Returns:
            Path to generated diagram file
        """
        dot = Digraph(comment='Architecture Topology', format=format)
        dot.attr(rankdir='TB', splines='ortho')

        # Set graph styling
        dot.attr('node', shape='box', style='rounded,filled', fillcolor='lightblue')
        dot.attr('edge', color='gray', fontsize='10')

        # Group resources by tier
        tiers = {}
        for resource in resources:
            tier = resource.get('tier', 'unknown')
            if tier not in tiers:
                tiers[tier] = []
            tiers[tier].append(resource)

        # Create subgraphs for each tier
        tier_order = ['web', 'app', 'application', 'database', 'db', 'data']
        sorted_tiers = []

        # Add tiers in order
        for tier_name in tier_order:
            if tier_name in tiers:
                sorted_tiers.append(tier_name)

        # Add remaining tiers
        for tier_name in tiers:
            if tier_name not in sorted_tiers:
                sorted_tiers.append(tier_name)

        # Create nodes for each tier
        for tier_name in sorted_tiers:
            with dot.subgraph(name=f'cluster_{tier_name}') as tier_graph:
                tier_graph.attr(label=f'{tier_name.upper()} Tier', style='dashed')

                for resource in tiers[tier_name]:
                    node_id = resource.get('id') or resource.get('name')
                    node_label = f"{resource.get('name')}\\n({resource.get('type')})"

                    # Color based on environment
                    env = resource.get('environment', '').lower()
                    if env in ['production', 'prod']:
                        fillcolor = 'lightcoral'
                    elif env in ['staging', 'stage']:
                        fillcolor = 'lightyellow'
                    else:
                        fillcolor = 'lightblue'

                    tier_graph.node(node_id, label=node_label, fillcolor=fillcolor)

        # Add edges for topology connections
        violation_connections = set()
        if violations:
            # Extract connections from violations
            for violation in violations:
                details = violation.get('details', {})
                viols = details.get('violations', [])
                for v in viols:
                    # Parse violation message for connections
                    # This is simplified - in production, use structured data
                    violation_connections.add(tuple(sorted([str(v)])))

        for connection in topology:
            source = connection.get('source')
            target = connection.get('target')

            if source and target:
                # Check if this connection is a violation
                is_violation = any(
                    source in str(v) and target in str(v)
                    for v in violation_connections
                )

                # Style edge
                edge_color = 'red' if is_violation else 'gray'
                edge_style = 'dashed' if is_violation else 'solid'

                label = connection.get('protocol', '')
                if connection.get('port'):
                    label += f":{connection.get('port')}"

                dot.edge(source, target, label=label, color=edge_color, style=edge_style)

        # Render diagram
        output_file = dot.render(output_path, cleanup=True)

        logger.info(f"Generated diagram: {output_file}")
        return output_file

    def generate_pattern_comparison(
        self,
        actual_resources: List[Dict[str, Any]],
        pattern_components: List[Any],
        output_path: str,
        format: str = 'png'
    ) -> str:
        """
        Generate side-by-side comparison of actual vs pattern.

        Args:
            actual_resources: Actual infrastructure resources
            pattern_components: Expected pattern components
            output_path: Output file path
            format: Output format

        Returns:
            Path to generated diagram
        """
        dot = Digraph(comment='Pattern Comparison', format=format)
        dot.attr(rankdir='LR')

        # Create two subgraphs
        with dot.subgraph(name='cluster_actual') as actual:
            actual.attr(label='Actual Infrastructure', style='filled', color='lightgray')
            actual.attr('node', fillcolor='lightblue')

            for resource in actual_resources:
                node_id = f"actual_{resource.get('name')}"
                node_label = f"{resource.get('name')}\\n({resource.get('type')})"
                actual.node(node_id, label=node_label)

        with dot.subgraph(name='cluster_pattern') as pattern:
            pattern.attr(label='Expected Pattern', style='filled', color='lightgray')
            pattern.attr('node', fillcolor='lightgreen')

            for component in pattern_components:
                comp_dict = component if isinstance(component, dict) else component.model_dump()
                node_id = f"pattern_{comp_dict.get('name')}"
                node_label = f"{comp_dict.get('name')}\\n({comp_dict.get('type')})"
                pattern.node(node_id, label=node_label)

        # Render
        output_file = dot.render(output_path, cleanup=True)
        logger.info(f"Generated comparison diagram: {output_file}")
        return output_file
