"""Pattern matching engine for identifying patterns in infrastructure"""

from typing import List, Dict, Any, Optional, Tuple
import logging

from .library import PatternLibrary
from ..models import Pattern, PatternMatch, Component, NetworkConnection

logger = logging.getLogger(__name__)


class PatternMatcher:
    """Engine for matching infrastructure against known patterns"""

    def __init__(self, library: Optional[PatternLibrary] = None):
        """
        Initialize pattern matcher.

        Args:
            library: Pattern library (creates new if not provided)
        """
        self.library = library or PatternLibrary()

    def match_pattern(
        self,
        resources: List[Dict[str, Any]],
        topology: List[Dict[str, Any]]
    ) -> Optional[PatternMatch]:
        """
        Find best matching pattern for given infrastructure.

        Args:
            resources: List of infrastructure resources
            topology: List of network connections

        Returns:
            Best matching pattern or None if no good match
        """
        logger.info(f"Matching {len(resources)} resources against pattern library")

        # Get all approved patterns
        patterns = self.library.get_approved_patterns()
        if not patterns:
            logger.warning("No approved patterns found in library")
            return None

        # Calculate match score for each pattern
        matches = []
        for pattern in patterns:
            score, deviations = self._calculate_similarity(
                resources, topology, pattern
            )
            if score > 0:  # Only include patterns with some match
                matches.append((pattern, score, deviations))

        if not matches:
            logger.info("No matching patterns found")
            return None

        # Return best match
        best_pattern, best_score, deviations = max(matches, key=lambda x: x[1])

        logger.info(f"Best match: {best_pattern.metadata.id} with score {best_score:.2%}")

        return self._create_pattern_match(
            best_pattern, best_score, deviations, resources
        )

    def _calculate_similarity(
        self,
        resources: List[Dict[str, Any]],
        topology: List[Dict[str, Any]],
        pattern: Pattern
    ) -> Tuple[float, List[str]]:
        """
        Calculate similarity score between infrastructure and pattern.

        Score is 0.0 to 1.0 based on:
        - Component presence (40%)
        - Network topology match (30%)
        - Configuration alignment (30%)

        Args:
            resources: Infrastructure resources
            topology: Network connections
            pattern: Pattern to match against

        Returns:
            Tuple of (similarity_score, list_of_deviations)
        """
        deviations = []

        # 1. Component presence score (40%)
        component_score, component_devs = self._score_components(
            resources, pattern.architecture.components
        )
        deviations.extend(component_devs)

        # 2. Network topology score (30%)
        topology_score, topology_devs = self._score_topology(
            topology, pattern.architecture.network_topology
        )
        deviations.extend(topology_devs)

        # 3. Configuration alignment score (30%)
        config_score, config_devs = self._score_configuration(
            resources, pattern.architecture.components
        )
        deviations.extend(config_devs)

        # Weighted total score
        total_score = (
            component_score * 0.4 +
            topology_score * 0.3 +
            config_score * 0.3
        )

        return total_score, deviations

    def _score_components(
        self,
        resources: List[Dict[str, Any]],
        expected_components: List[Any]
    ) -> Tuple[float, List[str]]:
        """
        Score component presence.

        Args:
            resources: Actual resources
            expected_components: Expected components from pattern

        Returns:
            Tuple of (score, deviations)
        """
        deviations = []

        if not expected_components:
            return 1.0, []

        # Group actual resources by type
        actual_types = {}
        for resource in resources:
            res_type = resource.get('type', 'unknown')
            if res_type not in actual_types:
                actual_types[res_type] = []
            actual_types[res_type].append(resource)

        # Check each expected component
        matched = 0
        for expected_comp in expected_components:
            comp_name = expected_comp.get('name') if isinstance(expected_comp, dict) else expected_comp.name
            comp_type = expected_comp.get('type') if isinstance(expected_comp, dict) else expected_comp.type

            if comp_type in actual_types:
                matched += 1
            else:
                deviations.append(f"Missing component: {comp_name} ({comp_type})")

        # Check for extra components
        expected_types = {
            (comp.get('type') if isinstance(comp, dict) else comp.type)
            for comp in expected_components
        }

        extra_types = set(actual_types.keys()) - expected_types
        for extra_type in extra_types:
            count = len(actual_types[extra_type])
            deviations.append(f"Extra component type: {extra_type} ({count} instances)")

        score = matched / len(expected_components) if expected_components else 0.0
        return score, deviations

    def _score_topology(
        self,
        actual_topology: List[Dict[str, Any]],
        expected_topology: List[Any]
    ) -> Tuple[float, List[str]]:
        """
        Score network topology match.

        Args:
            actual_topology: Actual network connections
            expected_topology: Expected connections from pattern

        Returns:
            Tuple of (score, deviations)
        """
        deviations = []

        if not expected_topology:
            return 1.0, []

        # Extract tier connections from actual topology
        actual_connections = set()
        for conn in actual_topology:
            source_tier = conn.get('source_tier', '')
            target_tier = conn.get('target_tier', '')
            if source_tier and target_tier:
                actual_connections.add((source_tier, target_tier))

        # Extract expected tier connections
        expected_connections = set()
        for conn in expected_topology:
            if isinstance(conn, dict):
                source = conn.get('source', '')
                target = conn.get('target', '')
            else:
                source = conn.source
                target = conn.target

            expected_connections.add((source, target))

        if not expected_connections:
            return 1.0, []

        # Calculate matches
        matched = len(actual_connections & expected_connections)
        missing = expected_connections - actual_connections
        extra = actual_connections - expected_connections

        for source, target in missing:
            deviations.append(f"Missing connection: {source} -> {target}")

        for source, target in extra:
            deviations.append(f"Extra connection: {source} -> {target}")

        score = matched / len(expected_connections) if expected_connections else 0.0
        return score, deviations

    def _score_configuration(
        self,
        resources: List[Dict[str, Any]],
        expected_components: List[Any]
    ) -> Tuple[float, List[str]]:
        """
        Score configuration alignment.

        Checks properties like instance counts, load balancing, etc.

        Args:
            resources: Actual resources
            expected_components: Expected components with configuration

        Returns:
            Tuple of (score, deviations)
        """
        deviations = []

        if not expected_components:
            return 1.0, []

        total_checks = 0
        passed_checks = 0

        for expected_comp in expected_components:
            comp_type = expected_comp.get('type') if isinstance(expected_comp, dict) else expected_comp.type
            comp_name = expected_comp.get('name') if isinstance(expected_comp, dict) else expected_comp.name

            # Find matching resources
            matching_resources = [r for r in resources if r.get('type') == comp_type]

            if not matching_resources:
                continue

            # Check minimum instances
            min_instances = (expected_comp.get('minimum_instances')
                           if isinstance(expected_comp, dict)
                           else getattr(expected_comp, 'minimum_instances', None))

            if min_instances:
                total_checks += 1
                if len(matching_resources) >= min_instances:
                    passed_checks += 1
                else:
                    deviations.append(
                        f"{comp_name}: has {len(matching_resources)} instances, "
                        f"requires {min_instances}"
                    )

            # Check load balancing requirement
            load_balanced = (expected_comp.get('load_balanced')
                           if isinstance(expected_comp, dict)
                           else getattr(expected_comp, 'load_balanced', None))

            if load_balanced is not None:
                total_checks += 1
                # Simplified check - in production, you'd check for actual load balancer
                if len(matching_resources) > 1:
                    passed_checks += 1
                else:
                    deviations.append(f"{comp_name}: not load balanced (single instance)")

        score = passed_checks / total_checks if total_checks > 0 else 1.0
        return score, deviations

    def _create_pattern_match(
        self,
        pattern: Pattern,
        score: float,
        deviations: List[str],
        resources: List[Dict[str, Any]]
    ) -> PatternMatch:
        """Create PatternMatch object from match results"""
        # Identify matched components
        matched_components = []
        missing_components = []
        extra_components = []

        expected_types = {
            (comp.get('type') if isinstance(comp, dict) else comp.type)
            for comp in pattern.architecture.components
        }

        actual_types = {r.get('type') for r in resources}

        matched_components = list(expected_types & actual_types)
        missing_components = list(expected_types - actual_types)
        extra_components = list(actual_types - expected_types)

        return PatternMatch(
            pattern_id=pattern.metadata.id,
            pattern_name=pattern.metadata.name,
            similarity_score=score,
            deviations=deviations,
            matched_components=matched_components,
            missing_components=missing_components,
            extra_components=extra_components
        )
