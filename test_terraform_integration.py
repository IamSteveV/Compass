#!/usr/bin/env python3
"""Diagnostic script to test terraform integration imports and basic functionality"""

import sys
import importlib

def test_imports():
    """Test that all new modules can be imported"""
    modules_to_test = [
        'src.terraform_integration',
        'src.terraform_integration.cloud_client',
        'src.terraform_integration.state_analyzer',
        'src.terraform_integration.resource_graph',
        'src.notifications',
        'src.notifications.email_service',
    ]

    print("Testing module imports...")
    all_good = True

    for module_name in modules_to_test:
        try:
            importlib.import_module(module_name)
            print(f"✓ {module_name}")
        except Exception as e:
            print(f"✗ {module_name}: {e}")
            all_good = False

    return all_good

def test_class_instantiation():
    """Test that key classes can be instantiated"""
    print("\nTesting class instantiation...")

    try:
        from src.terraform_integration import TerraformCloudClient, TerraformStateAnalyzer, TerraformResourceGraph
        from src.notifications import EmailService

        # Test instantiation with dummy values
        client = TerraformCloudClient(
            api_token="test-token",
            organization="test-org"
        )
        print("✓ TerraformCloudClient")

        analyzer = TerraformStateAnalyzer()
        print("✓ TerraformStateAnalyzer")

        graph = TerraformResourceGraph()
        print("✓ TerraformResourceGraph")

        email = EmailService(
            smtp_host="smtp.example.com",
            smtp_port=587,
            smtp_user="user",
            smtp_password="pass"
        )
        print("✓ EmailService")

        return True

    except Exception as e:
        print(f"✗ Class instantiation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_loading():
    """Test that configuration loads properly"""
    print("\nTesting configuration loading...")

    try:
        from src.config import get_settings
        settings = get_settings()

        # Check new config sections exist
        assert hasattr(settings, 'terraform_cloud'), "Missing terraform_cloud config"
        assert hasattr(settings, 'email'), "Missing email config"

        print(f"✓ Configuration loaded")
        print(f"  - terraform_cloud.enabled: {settings.terraform_cloud.enabled}")
        print(f"  - email.enabled: {settings.email.enabled}")

        return True

    except Exception as e:
        print(f"✗ Configuration loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all diagnostic tests"""
    print("="* 60)
    print("Terraform Integration Diagnostic")
    print("="* 60)
    print()

    results = []

    # Test imports
    results.append(("Imports", test_imports()))

    # Test class instantiation
    results.append(("Class Instantiation", test_class_instantiation()))

    # Test configuration
    results.append(("Configuration", test_config_loading()))

    # Summary
    print("\n" + "="* 60)
    print("Summary")
    print("="* 60)

    all_passed = all(result[1] for result in results)

    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:.<30} {status}")

    print()

    if all_passed:
        print("✓ All diagnostic tests passed!")
        return 0
    else:
        print("✗ Some tests failed. See details above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
