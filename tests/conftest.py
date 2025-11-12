"""Pytest configuration and fixtures"""

import pytest
from pathlib import Path


@pytest.fixture
def sample_resources():
    """Sample infrastructure resources for testing"""
    return [
        {
            'id': 'web-1',
            'name': 'web-server-1',
            'type': 'server',
            'tier': 'web',
            'environment': 'production',
            'instance_type': 't3.medium',
            'multi_az': True,
            'business_owner': 'team-a',
            'technical_owner': 'ops-team',
            'data_classification': 'internal'
        },
        {
            'id': 'app-1',
            'name': 'app-server-1',
            'type': 'server',
            'tier': 'app',
            'environment': 'production',
            'instance_type': 't3.large',
            'multi_az': True,
            'business_owner': 'team-a',
            'technical_owner': 'ops-team',
            'data_classification': 'internal'
        },
        {
            'id': 'db-1',
            'name': 'database-1',
            'type': 'database',
            'tier': 'database',
            'environment': 'production',
            'encrypted': True,
            'backup_enabled': True,
            'backup_retention_days': 30,
            'multi_az': True,
            'version': '14.7',
            'business_owner': 'team-a',
            'technical_owner': 'ops-team',
            'data_classification': 'confidential'
        }
    ]


@pytest.fixture
def sample_topology():
    """Sample network topology for testing"""
    return [
        {
            'source': 'web-server-1',
            'source_tier': 'web',
            'target': 'app-server-1',
            'target_tier': 'app',
            'protocol': 'https'
        },
        {
            'source': 'app-server-1',
            'source_tier': 'app',
            'target': 'database-1',
            'target_tier': 'database',
            'protocol': 'postgresql'
        }
    ]


@pytest.fixture
def patterns_dir(tmp_path):
    """Create temporary patterns directory with test pattern"""
    patterns_path = tmp_path / "patterns" / "reference-architectures" / "test-pattern"
    patterns_path.mkdir(parents=True)

    pattern_yaml = """
pattern:
  id: "TEST-001"
  name: "Test Pattern"
  version: "1.0"
  status: "approved"
  owner: "Test Team"
  description: "Test pattern for unit tests"

architecture:
  components:
    - name: "web_tier"
      type: "server"
      tier: "web"
      minimum_instances: 2

    - name: "app_tier"
      type: "server"
      tier: "app"
      minimum_instances: 2

    - name: "database"
      type: "database"
      tier: "database"

  network_topology:
    - source: "web"
      target: "app"

    - source: "app"
      target: "database"

  constraints:
    - description: "Test constraint"
      type: "must"

implementation:
  terraform_module: "test/module"
  required_variables:
    - "name"
  optional_variables: []
"""

    with open(patterns_path / "pattern.yaml", 'w') as f:
        f.write(pattern_yaml)

    return tmp_path / "patterns"
