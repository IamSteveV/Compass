"""Configuration management for the application"""

import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
import yaml
from string import Template


class ServiceNowConfig(BaseSettings):
    """ServiceNow CMDB configuration"""
    instance_url: str = Field(default="", env="SNOW_INSTANCE_URL")
    api_user: str = Field(default="", env="SNOW_API_USER")
    api_password: str = Field(default="", env="SNOW_API_PASSWORD")
    timeout: int = 30
    verify_ssl: bool = True


class PatternsConfig(BaseSettings):
    """Pattern library configuration"""
    repository: str = "./patterns"
    auto_reload: bool = True
    cache_ttl: int = 3600


class ValidationConfig(BaseSettings):
    """Validation engine configuration"""
    severity_levels: List[str] = ["critical", "high", "medium", "low"]
    fail_on_critical: bool = True
    parallel_execution: bool = True
    max_workers: int = 4


class TerraformConfig(BaseSettings):
    """Terraform integration configuration"""
    parse_timeout: int = 300
    max_file_size_mb: int = 50
    supported_versions: List[str] = ["1.0", "1.1", "1.2", "1.3", "1.4", "1.5", "1.6"]


class TerraformCloudConfig(BaseSettings):
    """Terraform Cloud/Enterprise API configuration"""
    enabled: bool = False
    api_token: str = Field(default="", env="TERRAFORM_CLOUD_TOKEN")
    organization: str = Field(default="", env="TERRAFORM_CLOUD_ORG")
    base_url: str = Field(default="https://app.terraform.io/api/v2", env="TERRAFORM_CLOUD_URL")


class ApprovalConfig(BaseSettings):
    """Approval routing configuration"""
    fast_track_threshold: float = 0.95
    standard_review_threshold: float = 0.85
    full_review_threshold: float = 0.0


class DatabaseConfig(BaseSettings):
    """Database configuration"""
    url: str = Field(default="sqlite:///./architecture_validation.db", env="DATABASE_URL")
    pool_size: int = 5
    echo: bool = False


class EmailConfig(BaseSettings):
    """Email notification configuration"""
    enabled: bool = True
    smtp_host: str = Field(default="smtp.gmail.com", env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_user: str = Field(default="", env="SMTP_USER")
    smtp_password: str = Field(default="", env="SMTP_PASSWORD")
    use_tls: bool = True
    from_email: str = Field(default="noreply@compass.local", env="SMTP_FROM_EMAIL")
    from_name: str = "Compass Validation System"

    # Notification triggers
    notify_on_failure: bool = True
    notify_on_critical: bool = True
    notify_on_success: bool = False

    # Default recipients
    default_recipients: List[str] = []

    # Attachment options
    attach_pdf_on_failure: bool = True


class Settings(BaseSettings):
    """Main application settings"""
    app_env: str = Field(default="development", env="APP_ENV")
    app_debug: bool = Field(default=True, env="APP_DEBUG")
    app_port: int = Field(default=5000, env="APP_PORT")
    api_prefix: str = Field(default="/api", env="API_PREFIX")

    # Sub-configurations
    servicenow: ServiceNowConfig = ServiceNowConfig()
    patterns: PatternsConfig = PatternsConfig()
    validation: ValidationConfig = ValidationConfig()
    terraform: TerraformConfig = TerraformConfig()
    terraform_cloud: TerraformCloudConfig = TerraformCloudConfig()
    approval: ApprovalConfig = ApprovalConfig()
    database: DatabaseConfig = DatabaseConfig()
    email: EmailConfig = EmailConfig()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def load_config(config_file: Optional[str] = None) -> Settings:
    """
    Load configuration from YAML file and environment variables.
    Environment variables take precedence over YAML configuration.

    Args:
        config_file: Path to YAML configuration file

    Returns:
        Settings object with loaded configuration
    """
    # Load from .env file if exists
    from dotenv import load_dotenv
    load_dotenv()

    settings = Settings()

    # Load YAML config if provided
    if config_file and os.path.exists(config_file):
        with open(config_file, 'r') as f:
            yaml_content = f.read()

            # Substitute environment variables in YAML
            template = Template(yaml_content)
            env_dict = {**os.environ}

            # Provide defaults for missing env vars
            env_dict.setdefault('SNOW_INSTANCE_URL', '')
            env_dict.setdefault('SNOW_API_USER', '')
            env_dict.setdefault('SNOW_API_PASSWORD', '')
            env_dict.setdefault('DATABASE_URL', 'sqlite:///./architecture_validation.db')
            env_dict.setdefault('SMTP_HOST', 'smtp.gmail.com')
            env_dict.setdefault('SMTP_PORT', '587')
            env_dict.setdefault('SMTP_USER', '')
            env_dict.setdefault('SMTP_PASSWORD', '')
            env_dict.setdefault('SMTP_FROM_EMAIL', 'noreply@compass.local')
            env_dict.setdefault('TERRAFORM_CLOUD_TOKEN', '')
            env_dict.setdefault('TERRAFORM_CLOUD_ORG', '')
            env_dict.setdefault('TERRAFORM_CLOUD_URL', 'https://app.terraform.io/api/v2')

            substituted_content = template.safe_substitute(env_dict)
            yaml_config = yaml.safe_load(substituted_content)

            # Update settings from YAML
            if yaml_config:
                if 'servicenow' in yaml_config:
                    settings.servicenow = ServiceNowConfig(**yaml_config['servicenow'])
                if 'patterns' in yaml_config:
                    settings.patterns = PatternsConfig(**yaml_config['patterns'])
                if 'validation' in yaml_config:
                    settings.validation = ValidationConfig(**yaml_config['validation'])
                if 'terraform' in yaml_config:
                    settings.terraform = TerraformConfig(**yaml_config['terraform'])
                if 'terraform_cloud' in yaml_config:
                    settings.terraform_cloud = TerraformCloudConfig(**yaml_config['terraform_cloud'])
                if 'approval' in yaml_config and 'routing' in yaml_config['approval']:
                    settings.approval = ApprovalConfig(**yaml_config['approval']['routing'])
                if 'database' in yaml_config:
                    settings.database = DatabaseConfig(**yaml_config['database'])
                if 'notifications' in yaml_config and 'email' in yaml_config['notifications']:
                    settings.email = EmailConfig(**yaml_config['notifications']['email'])

    return settings


# Global settings instance
settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance"""
    global settings
    if settings is None:
        config_path = Path(__file__).parent.parent / "config" / "config.yaml"
        settings = load_config(str(config_path) if config_path.exists() else None)
    return settings
