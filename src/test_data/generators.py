"""Generate realistic test data for development and testing"""

import random
import json
from typing import Dict, List, Any
from datetime import datetime


def generate_sample_resources(pattern_type: str = "3-tier") -> List[Dict[str, Any]]:
    """
    Generate sample infrastructure resources.

    Args:
        pattern_type: Type of pattern to generate (3-tier, microservices, ha-database)

    Returns:
        List of resource dictionaries
    """
    if pattern_type == "3-tier":
        return _generate_3_tier_resources()
    elif pattern_type == "microservices":
        return _generate_microservices_resources()
    elif pattern_type == "ha-database":
        return _generate_ha_database_resources()
    else:
        return _generate_3_tier_resources()


def _generate_3_tier_resources() -> List[Dict[str, Any]]:
    """Generate 3-tier web application resources"""
    resources = []

    # Load balancer
    resources.append({
        'id': 'alb-web-prod-001',
        'name': 'web-application-lb',
        'type': 'load_balancer',
        'tier': 'web',
        'environment': 'production',
        'scheme': 'internet-facing',
        'business_owner': 'product-team',
        'technical_owner': 'platform-ops',
        'data_classification': 'internal'
    })

    # Web tier servers
    for i in range(1, 3):
        resources.append({
            'id': f'web-server-{i:03d}',
            'name': f'web-server-{i}',
            'type': 'server',
            'tier': 'web',
            'environment': 'production',
            'instance_type': 't3.medium',
            'multi_az': True,
            'availability_zones': ['us-east-1a', 'us-east-1b'],
            'business_owner': 'product-team',
            'technical_owner': 'platform-ops',
            'data_classification': 'internal',
            'backup_enabled': True
        })

    # App tier servers
    for i in range(1, 3):
        resources.append({
            'id': f'app-server-{i:03d}',
            'name': f'app-server-{i}',
            'type': 'server',
            'tier': 'app',
            'environment': 'production',
            'instance_type': 't3.large',
            'multi_az': True,
            'availability_zones': ['us-east-1a', 'us-east-1b'],
            'business_owner': 'product-team',
            'technical_owner': 'platform-ops',
            'data_classification': 'internal',
            'backup_enabled': True
        })

    # Database
    resources.append({
        'id': 'db-postgres-prod-001',
        'name': 'application-database',
        'type': 'database',
        'tier': 'database',
        'environment': 'production',
        'encrypted': True,
        'backup_enabled': True,
        'backup_retention_days': 30,
        'multi_az': True,
        'version': '14.7',
        'instance_type': 'db.r5.large',
        'business_owner': 'product-team',
        'technical_owner': 'database-team',
        'data_classification': 'confidential',
        'dr_tier': 'tier-1'
    })

    return resources


def _generate_microservices_resources() -> List[Dict[str, Any]]:
    """Generate microservices architecture resources"""
    resources = []

    # API Gateway
    resources.append({
        'id': 'apigw-prod-001',
        'name': 'api-gateway',
        'type': 'load_balancer',
        'tier': 'gateway',
        'environment': 'production',
        'business_owner': 'platform-team',
        'technical_owner': 'platform-ops',
        'data_classification': 'internal'
    })

    # Microservices
    services = ['user-service', 'order-service', 'payment-service', 'inventory-service']
    for service in services:
        for i in range(1, 4):
            resources.append({
                'id': f'{service}-{i:03d}',
                'name': f'{service}-{i}',
                'type': 'server',
                'tier': 'app',
                'environment': 'production',
                'instance_type': 't3.medium',
                'multi_az': True,
                'business_owner': 'platform-team',
                'technical_owner': 'platform-ops',
                'data_classification': 'internal',
                'service_name': service
            })

        # Database per service
        resources.append({
            'id': f'db-{service}',
            'name': f'{service}-db',
            'type': 'database',
            'tier': 'database',
            'environment': 'production',
            'encrypted': True,
            'backup_enabled': True,
            'backup_retention_days': 14,
            'multi_az': True,
            'version': '14.7',
            'business_owner': 'platform-team',
            'technical_owner': 'database-team',
            'data_classification': 'confidential'
        })

    return resources


def _generate_ha_database_resources() -> List[Dict[str, Any]]:
    """Generate HA database resources"""
    resources = []

    # Primary database
    resources.append({
        'id': 'db-primary-001',
        'name': 'primary-database',
        'type': 'database',
        'tier': 'database',
        'environment': 'production',
        'encrypted': True,
        'backup_enabled': True,
        'backup_retention_days': 30,
        'multi_az': True,
        'version': '14.7',
        'instance_type': 'db.r5.xlarge',
        'business_owner': 'data-team',
        'technical_owner': 'database-team',
        'data_classification': 'confidential',
        'dr_tier': 'tier-1'
    })

    # Read replicas
    for i in range(1, 3):
        resources.append({
            'id': f'db-replica-{i:03d}',
            'name': f'read-replica-{i}',
            'type': 'database',
            'tier': 'database',
            'environment': 'production',
            'encrypted': True,
            'version': '14.7',
            'instance_type': 'db.r5.large',
            'replica_source': 'db-primary-001',
            'business_owner': 'data-team',
            'technical_owner': 'database-team',
            'data_classification': 'confidential'
        })

    return resources


def generate_sample_topology(resources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate network topology from resources.

    Args:
        resources: List of resources

    Returns:
        List of topology connections
    """
    topology = []

    # Group resources by tier
    by_tier = {}
    for resource in resources:
        tier = resource.get('tier', 'unknown')
        if tier not in by_tier:
            by_tier[tier] = []
        by_tier[tier].append(resource)

    # Create connections based on tier hierarchy
    tier_order = ['gateway', 'web', 'app', 'database']

    for i, source_tier in enumerate(tier_order):
        if source_tier not in by_tier:
            continue

        # Connect to next tier
        for j in range(i + 1, len(tier_order)):
            target_tier = tier_order[j]
            if target_tier not in by_tier:
                continue

            # Create connections
            for source in by_tier[source_tier]:
                for target in by_tier[target_tier]:
                    topology.append({
                        'source': source['name'],
                        'source_tier': source_tier,
                        'target': target['name'],
                        'target_tier': target_tier,
                        'protocol': 'https' if target_tier != 'database' else 'postgresql'
                    })
            break  # Only connect to immediate next tier

    return topology


def generate_sample_terraform_plan(pattern_type: str = "3-tier") -> Dict[str, Any]:
    """
    Generate a sample Terraform plan JSON.

    Args:
        pattern_type: Type of pattern

    Returns:
        Terraform plan dictionary
    """
    resources = generate_sample_resources(pattern_type)

    # Convert to Terraform format
    tf_resources = []
    for resource in resources:
        tf_resource = {
            "address": f"{resource['type']}.{resource['name'].replace('-', '_')}",
            "mode": "managed",
            "type": f"aws_{resource['type']}",
            "name": resource['name'],
            "provider_name": "aws",
            "values": {
                **resource,
                "tags": {
                    "Environment": resource.get('environment', ''),
                    "Tier": resource.get('tier', ''),
                    "Owner": resource.get('business_owner', ''),
                    "TechnicalOwner": resource.get('technical_owner', ''),
                    "DataClassification": resource.get('data_classification', '')
                }
            }
        }
        tf_resources.append(tf_resource)

    plan = {
        "format_version": "1.0",
        "terraform_version": "1.5.0",
        "planned_values": {
            "root_module": {
                "resources": tf_resources
            }
        },
        "resource_changes": [
            {
                "address": r["address"],
                "change": {
                    "actions": ["create"]
                }
            }
            for r in tf_resources
        ],
        "variables": {
            "environment": {"value": "production"},
            "application_name": {"value": "sample-app"},
            "owner": {"value": "product-team"}
        },
        "outputs": {}
    }

    return plan


def generate_sample_cmdb_application(pattern_type: str = "3-tier") -> Dict[str, Any]:
    """
    Generate a sample CMDB application.

    Args:
        pattern_type: Type of pattern

    Returns:
        CMDB application dictionary
    """
    resources = generate_sample_resources(pattern_type)

    # Convert to CMDB format
    configuration_items = []
    for resource in resources:
        ci = {
            "sys_id": resource['id'],
            "name": resource['name'],
            "type": resource['type'],
            "u_environment": resource.get('environment', ''),
            "u_tier": resource.get('tier', ''),
            "owned_by": resource.get('business_owner', ''),
            "managed_by": resource.get('technical_owner', ''),
            "u_data_classification": resource.get('data_classification', ''),
            **{k: v for k, v in resource.items()
               if k not in ['id', 'name', 'type', 'environment', 'tier']}
        }
        configuration_items.append(ci)

    # Generate relationships
    relationships = []
    topology = generate_sample_topology(resources)

    for conn in topology:
        source_ci = next((ci for ci in configuration_items if ci['name'] == conn['source']), None)
        target_ci = next((ci for ci in configuration_items if ci['name'] == conn['target']), None)

        if source_ci and target_ci:
            relationships.append({
                "parent": source_ci['sys_id'],
                "child": target_ci['sys_id'],
                "type": "connects_to"
            })

    return {
        "sys_id": "app-sample-001",
        "name": f"Sample {pattern_type.title()} Application",
        "short_description": f"Sample application following {pattern_type} pattern",
        "configuration_items": configuration_items,
        "relationships": relationships
    }


def save_sample_data_files(output_dir: str = "./examples"):
    """
    Generate and save sample data files.

    Args:
        output_dir: Directory to save files
    """
    import os
    os.makedirs(output_dir, exist_ok=True)

    patterns = ["3-tier", "microservices", "ha-database"]

    for pattern in patterns:
        # Generate Terraform plan
        tf_plan = generate_sample_terraform_plan(pattern)
        filename = os.path.join(output_dir, f"sample_{pattern.replace('-', '_')}_plan.json")
        with open(filename, 'w') as f:
            json.dump(tf_plan, f, indent=2)
        print(f"Generated: {filename}")

        # Generate CMDB app
        cmdb_app = generate_sample_cmdb_application(pattern)
        filename = os.path.join(output_dir, f"sample_{pattern.replace('-', '_')}_cmdb.json")
        with open(filename, 'w') as f:
            json.dump(cmdb_app, f, indent=2)
        print(f"Generated: {filename}")


if __name__ == "__main__":
    # Generate sample files when run directly
    save_sample_data_files()
