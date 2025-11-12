"""Pattern library for loading and managing architecture patterns"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional
import logging

from ..models import Pattern, PatternMetadata, ArchitectureSpec, TerraformImplementation
from ..config import get_settings

logger = logging.getLogger(__name__)


class PatternLibrary:
    """Library for managing architecture patterns"""

    def __init__(self, repository_path: Optional[str] = None):
        """
        Initialize pattern library.

        Args:
            repository_path: Path to patterns repository (defaults to config)
        """
        settings = get_settings()
        self.repository_path = Path(repository_path or settings.patterns.repository)
        self.patterns: Dict[str, Pattern] = {}
        self.auto_reload = settings.patterns.auto_reload

        if self.repository_path.exists():
            self.load_patterns()
        else:
            logger.warning(f"Pattern repository not found: {self.repository_path}")

    def load_patterns(self) -> None:
        """Load all patterns from the repository"""
        logger.info(f"Loading patterns from {self.repository_path}")

        pattern_count = 0

        # Load reference architectures
        ref_arch_path = self.repository_path / "reference-architectures"
        if ref_arch_path.exists():
            pattern_count += self._load_patterns_from_directory(ref_arch_path)

        # Load component patterns
        component_path = self.repository_path / "component-patterns"
        if component_path.exists():
            pattern_count += self._load_patterns_from_directory(component_path)

        logger.info(f"Loaded {pattern_count} patterns")

    def _load_patterns_from_directory(self, directory: Path) -> int:
        """Load patterns from a directory"""
        count = 0

        # Find all pattern.yaml files
        for pattern_file in directory.rglob("pattern.yaml"):
            try:
                pattern = self._load_pattern_file(pattern_file)
                if pattern:
                    self.patterns[pattern.metadata.id] = pattern
                    count += 1
                    logger.debug(f"Loaded pattern: {pattern.metadata.id} - {pattern.metadata.name}")
            except Exception as e:
                logger.error(f"Failed to load pattern from {pattern_file}: {e}")

        return count

    def _load_pattern_file(self, file_path: Path) -> Optional[Pattern]:
        """Load a single pattern file"""
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)

        if not data or 'pattern' not in data:
            logger.warning(f"Invalid pattern file format: {file_path}")
            return None

        pattern_data = data['pattern']

        # Parse metadata
        metadata = PatternMetadata(
            id=pattern_data['id'],
            name=pattern_data['name'],
            version=pattern_data['version'],
            status=pattern_data['status'],
            owner=pattern_data.get('owner', 'unknown'),
            approval_date=pattern_data.get('approval_date'),
            compliance_tags=pattern_data.get('compliance_tags', []),
            description=pattern_data.get('description', '')
        )

        # Parse architecture
        arch_data = pattern_data.get('architecture', {})
        architecture = ArchitectureSpec(
            components=arch_data.get('components', []),
            network_topology=arch_data.get('network_topology', []),
            constraints=arch_data.get('constraints', [])
        )

        # Parse implementation
        impl_data = pattern_data.get('implementation', {})
        implementation = TerraformImplementation(
            terraform_module=impl_data.get('terraform_module', ''),
            required_variables=impl_data.get('required_variables', []),
            optional_variables=impl_data.get('optional_variables', []),
            example_usage=impl_data.get('example_usage')
        )

        # Documentation
        documentation = pattern_data.get('documentation', {})

        return Pattern(
            metadata=metadata,
            architecture=architecture,
            implementation=implementation,
            documentation=documentation
        )

    def get_pattern(self, pattern_id: str) -> Optional[Pattern]:
        """Get a pattern by ID"""
        if self.auto_reload:
            self.load_patterns()

        return self.patterns.get(pattern_id)

    def get_all_patterns(self) -> List[Pattern]:
        """Get all loaded patterns"""
        if self.auto_reload:
            self.load_patterns()

        return list(self.patterns.values())

    def get_approved_patterns(self) -> List[Pattern]:
        """Get only approved patterns"""
        return [p for p in self.get_all_patterns() if p.metadata.status == 'approved']

    def search_patterns(self, query: str) -> List[Pattern]:
        """
        Search patterns by name or description.

        Args:
            query: Search query string

        Returns:
            List of matching patterns
        """
        query_lower = query.lower()
        results = []

        for pattern in self.get_all_patterns():
            if (query_lower in pattern.metadata.name.lower() or
                query_lower in pattern.metadata.description.lower() or
                query_lower in pattern.metadata.id.lower()):
                results.append(pattern)

        return results

    def get_pattern_diagram_path(self, pattern_id: str) -> Optional[Path]:
        """
        Get path to pattern diagram file.

        Args:
            pattern_id: Pattern ID

        Returns:
            Path to diagram file or None if not found
        """
        pattern = self.get_pattern(pattern_id)
        if not pattern:
            return None

        # Search for diagram files in pattern directory
        for pattern_dir in self.repository_path.rglob(f"*"):
            if pattern_dir.is_dir():
                pattern_file = pattern_dir / "pattern.yaml"
                if pattern_file.exists():
                    # Check if this is the right pattern
                    with open(pattern_file, 'r') as f:
                        data = yaml.safe_load(f)
                        if data and data.get('pattern', {}).get('id') == pattern_id:
                            # Look for diagram file
                            for ext in ['.png', '.svg', '.jpg']:
                                diagram_file = pattern_dir / f"diagram{ext}"
                                if diagram_file.exists():
                                    return diagram_file

        return None

    def reload(self) -> None:
        """Reload all patterns from repository"""
        self.patterns.clear()
        self.load_patterns()

    def __len__(self) -> int:
        return len(self.patterns)

    def __contains__(self, pattern_id: str) -> bool:
        return pattern_id in self.patterns
