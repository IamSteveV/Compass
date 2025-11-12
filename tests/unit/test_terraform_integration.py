"""Unit tests for Terraform integration modules"""

import pytest
from unittest.mock import Mock, patch, MagicMock


class TestTerraformStateAnalyzer:
    """Tests for TerraformStateAnalyzer"""

    def test_initialization(self):
        """Test analyzer can be initialized"""
        from src.terraform_integration.state_analyzer import TerraformStateAnalyzer

        analyzer = TerraformStateAnalyzer()
        assert analyzer is not None
        assert hasattr(analyzer, 'resource_type_mapping')

    def test_analyze_state_with_valid_state(self):
        """Test state analysis with valid state file"""
        from src.terraform_integration.state_analyzer import TerraformStateAnalyzer

        analyzer = TerraformStateAnalyzer()

        # Sample state file structure
        state = {
            'terraform_version': '1.6.0',
            'values': {
                'root_module': {
                    'resources': [
                        {
                            'address': 'aws_instance.web',
                            'type': 'aws_instance',
                            'name': 'web',
                            'provider_name': 'provider["registry.terraform.io/hashicorp/aws"]',
                            'mode': 'managed',
                            'values': {
                                'instance_type': 't3.medium',
                                'tags': {'Name': 'web-server'}
                            }
                        }
                    ],
                    'child_modules': []
                }
            }
        }

        result = analyzer.analyze_state(state)

        assert result is not None
        assert 'summary' in result
        assert 'resources' in result
        assert result['summary']['total_resources'] == 1
        assert result['summary']['terraform_version'] == '1.6.0'

    def test_categorize_resources(self):
        """Test resource categorization"""
        from src.terraform_integration.state_analyzer import TerraformStateAnalyzer

        analyzer = TerraformStateAnalyzer()

        resources = [
            {'address': 'aws_instance.web', 'type': 'aws_instance'},
            {'address': 'aws_db_instance.main', 'type': 'aws_db_instance'},
            {'address': 'aws_lb.main', 'type': 'aws_lb'},
        ]

        categories = analyzer._categorize_resources(resources)

        assert 'compute' in categories
        assert 'database' in categories
        assert 'load_balancer' in categories


class TestTerraformResourceGraph:
    """Tests for TerraformResourceGraph"""

    def test_initialization(self):
        """Test graph generator can be initialized"""
        from src.terraform_integration.resource_graph import TerraformResourceGraph

        graph = TerraformResourceGraph()
        assert graph is not None
        assert hasattr(graph, 'node_colors')

    def test_generate_mermaid_diagram(self):
        """Test Mermaid diagram generation"""
        from src.terraform_integration.resource_graph import TerraformResourceGraph

        graph = TerraformResourceGraph()

        resources = [
            {'address': 'aws_instance.web', 'type': 'aws_instance', 'name': 'web'},
            {'address': 'aws_db_instance.main', 'type': 'aws_db_instance', 'name': 'main'}
        ]

        topology = [
            {'from': 'aws_instance.web', 'to': 'aws_db_instance.main', 'type': 'depends_on'}
        ]

        diagram = graph.generate_mermaid_diagram(resources, topology)

        assert diagram is not None
        assert 'graph TB' in diagram
        assert 'aws_instance' in diagram

    def test_generate_network_json(self):
        """Test network JSON generation"""
        from src.terraform_integration.resource_graph import TerraformResourceGraph

        graph = TerraformResourceGraph()

        resources = [
            {'address': 'aws_instance.web', 'type': 'aws_instance', 'name': 'web', 'module': 'root', 'provider': 'aws'}
        ]

        topology = []

        result = graph.generate_network_json(resources, topology)

        assert 'nodes' in result
        assert 'edges' in result
        assert len(result['nodes']) == 1
        assert result['nodes'][0]['id'] == 'aws_instance.web'

    def test_generate_summary_stats(self):
        """Test summary statistics generation"""
        from src.terraform_integration.resource_graph import TerraformResourceGraph

        graph = TerraformResourceGraph()

        resources = [
            {'address': 'aws_instance.web', 'type': 'aws_instance', 'name': 'web', 'module': 'root', 'provider': 'aws'},
            {'address': 'aws_db_instance.main', 'type': 'aws_db_instance', 'name': 'main', 'module': 'root', 'provider': 'aws'}
        ]

        topology = [
            {'from': 'aws_instance.web', 'to': 'aws_db_instance.main', 'type': 'depends_on'}
        ]

        stats = graph.generate_summary_stats(resources, topology)

        assert 'total_resources' in stats
        assert 'total_relationships' in stats
        assert stats['total_resources'] == 2
        assert stats['total_relationships'] == 1


class TestTerraformCloudClient:
    """Tests for TerraformCloudClient"""

    def test_initialization(self):
        """Test client can be initialized"""
        from src.terraform_integration.cloud_client import TerraformCloudClient

        client = TerraformCloudClient(
            api_token='test-token',
            organization='test-org'
        )

        assert client is not None
        assert client.api_token == 'test-token'
        assert client.organization == 'test-org'
        assert client.base_url == 'https://app.terraform.io/api/v2'

    @patch('src.terraform_integration.cloud_client.requests.Session')
    def test_list_workspaces(self, mock_session):
        """Test listing workspaces"""
        from src.terraform_integration.cloud_client import TerraformCloudClient

        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            'data': [
                {
                    'id': 'ws-1',
                    'attributes': {
                        'name': 'test-workspace',
                        'terraform-version': '1.6.0',
                        'resource-count': 10
                    }
                }
            ]
        }
        mock_response.raise_for_status.return_value = None

        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = TerraformCloudClient(
            api_token='test-token',
            organization='test-org'
        )

        workspaces = client.list_workspaces()

        assert len(workspaces) == 1
        assert workspaces[0]['name'] == 'test-workspace'

    def test_extract_resources_from_state(self):
        """Test resource extraction from state"""
        from src.terraform_integration.cloud_client import TerraformCloudClient

        client = TerraformCloudClient(
            api_token='test-token',
            organization='test-org'
        )

        state = {
            'values': {
                'root_module': {
                    'resources': [
                        {
                            'type': 'aws_instance',
                            'name': 'web',
                            'provider_name': 'aws',
                            'mode': 'managed',
                            'values': {},
                            'address': 'aws_instance.web'
                        }
                    ],
                    'child_modules': []
                }
            }
        }

        resources = client._extract_resources_from_state(state)

        assert len(resources) == 1
        assert resources[0]['type'] == 'aws_instance'
        assert resources[0]['name'] == 'web'
