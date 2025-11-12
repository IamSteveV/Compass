#!/usr/bin/env python3
"""
Architecture Validation CLI

Command-line interface for validating infrastructure against architectural standards.
"""

import click
import json
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from typing import Optional

from src.config import get_settings
from src.validation.engine import ValidationEngine
from src.validation.rule import get_rule_registry
from src.validation.rules import *
from src.cmdb.client import CMDBClient
from src.terraform_parser.parser import TerraformParser
from src.patterns.library import PatternLibrary
from src.patterns.matcher import PatternMatcher
from src.models import ValidationStatus, Severity

console = Console()


def register_all_rules():
    """Register all validation rules"""
    from src.validation.rules.security_rules import (
        NoDirectWebToDatabaseRule,
        ProductionDatabaseEncryptionRule,
        DMZIsolationRule,
        ProductionBackupRule
    )
    from src.validation.rules.metadata_rules import (
        RequiredMetadataRule,
        ProductionDRTierRule
    )
    from src.validation.rules.technology_rules import (
        ApprovedDatabaseVersionRule,
        ApprovedInstanceTypeRule
    )
    from src.validation.rules.resilience_rules import (
        ProductionMultiAZRule,
        DatabaseBackupEnabledRule
    )

    registry = get_rule_registry()

    # Clear existing rules
    registry.clear()

    # Register security rules
    registry.register(NoDirectWebToDatabaseRule())
    registry.register(ProductionDatabaseEncryptionRule())
    registry.register(DMZIsolationRule())
    registry.register(ProductionBackupRule())

    # Register metadata rules
    registry.register(RequiredMetadataRule())
    registry.register(ProductionDRTierRule())

    # Register technology rules
    registry.register(ApprovedDatabaseVersionRule())
    registry.register(ApprovedInstanceTypeRule())

    # Register resilience rules
    registry.register(ProductionMultiAZRule())
    registry.register(DatabaseBackupEnabledRule())

    console.print(f"[green]Registered {len(registry)} validation rules[/green]")


def print_validation_report(report):
    """Print validation report in a nice format"""
    console.print("\n[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    console.print("[bold cyan]        Validation Results[/bold cyan]")
    console.print("[bold cyan]═══════════════════════════════════════════[/bold cyan]\n")

    # Pattern match information
    if report.pattern_match:
        pm = report.pattern_match
        score_pct = pm.similarity_score * 100
        color = "green" if score_pct >= 95 else "yellow" if score_pct >= 85 else "red"

        console.print(f"[bold]Pattern Match:[/bold] {pm.pattern_name}")
        console.print(f"[bold]Match Score:[/bold] [{color}]{score_pct:.1f}%[/{color}]")

        if report.approval_track:
            track_colors = {
                "fast_track": "green",
                "standard_review": "yellow",
                "full_review": "red"
            }
            track_names = {
                "fast_track": "FAST TRACK ✓",
                "standard_review": "STANDARD REVIEW",
                "full_review": "FULL REVIEW"
            }
            track_color = track_colors.get(report.approval_track, "white")
            track_name = track_names.get(report.approval_track, report.approval_track)
            console.print(f"[bold]Approval Track:[/bold] [{track_color}]{track_name}[/{track_color}]\n")

    # Summary
    summary = report.summary
    console.print(f"[bold green]✓ Passed:[/bold green] {summary.passed}")
    console.print(f"[bold yellow]⚠ Warnings:[/bold yellow] {summary.warnings}")
    console.print(f"[bold red]✗ Violations:[/bold red] {summary.failed}")
    console.print(f"[dim]○ Skipped:[/dim] {summary.skipped}\n")

    # Compliance score
    score_color = "green" if summary.compliance_score >= 0.9 else "yellow" if summary.compliance_score >= 0.7 else "red"
    console.print(f"[bold]Compliance Score:[/bold] [{score_color}]{summary.compliance_score:.1%}[/{score_color}]\n")

    # Critical issues
    critical_results = [r for r in report.results
                       if r.status == ValidationStatus.FAILED and r.severity == Severity.CRITICAL]

    if critical_results:
        console.print("[bold red]CRITICAL Issues:[/bold red]")
        for result in critical_results:
            console.print(f"  [red]•[/red] {result.message}")
            console.print(f"    [dim](Rule: {result.rule_id})[/dim]")
        console.print()

    # High priority issues
    high_results = [r for r in report.results
                   if r.status == ValidationStatus.FAILED and r.severity == Severity.HIGH]

    if high_results:
        console.print("[bold orange]HIGH Priority Issues:[/bold orange]")
        for result in high_results:
            console.print(f"  [orange1]•[/orange1] {result.message}")
            console.print(f"    [dim](Rule: {result.rule_id})[/dim]")
        console.print()

    # Warnings
    warning_results = [r for r in report.results if r.status == ValidationStatus.WARNING]

    if warning_results:
        console.print("[bold yellow]Warnings:[/bold yellow]")
        for result in warning_results[:5]:  # Show first 5
            console.print(f"  [yellow]•[/yellow] {result.message}")
        if len(warning_results) > 5:
            console.print(f"  [dim]... and {len(warning_results) - 5} more warnings[/dim]")
        console.print()

    # Pattern deviations
    if report.pattern_match and report.pattern_match.deviations:
        console.print("[bold]Deviations from Pattern:[/bold]")
        for deviation in report.pattern_match.deviations[:5]:
            console.print(f"  [cyan]•[/cyan] {deviation}")
        if len(report.pattern_match.deviations) > 5:
            console.print(f"  [dim]... and {len(report.pattern_match.deviations) - 5} more deviations[/dim]")
        console.print()

    console.print("[bold cyan]═══════════════════════════════════════════[/bold cyan]\n")


@click.group()
@click.version_option(version='0.1.0')
def cli():
    """Architecture Validation & Pattern Management System"""
    pass


@cli.command()
@click.option('--terraform-plan', type=click.Path(exists=True), help='Path to Terraform plan JSON file')
@click.option('--cmdb-app', type=str, help='CMDB Application name or ID')
@click.option('--output', '-o', type=click.Path(), help='Output file for JSON report')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def validate(terraform_plan: Optional[str], cmdb_app: Optional[str],
            output: Optional[str], verbose: bool):
    """Validate infrastructure against architectural standards"""

    if not terraform_plan and not cmdb_app:
        console.print("[red]Error: Must specify either --terraform-plan or --cmdb-app[/red]")
        sys.exit(1)

    # Register rules
    register_all_rules()

    # Initialize components
    engine = ValidationEngine()
    pattern_matcher = PatternMatcher()

    try:
        # Get resources and context
        if terraform_plan:
            console.print(f"[cyan]Parsing Terraform plan: {terraform_plan}[/cyan]")
            parser = TerraformParser()
            plan = parser.parse_plan_file(terraform_plan)
            validation_data = parser.get_resources_for_validation(plan)

        else:  # cmdb_app
            console.print(f"[cyan]Fetching CMDB data for application: {cmdb_app}[/cyan]")
            cmdb_client = CMDBClient()
            validation_data = cmdb_client.get_topology_for_validation(cmdb_app)

        resources = validation_data['resources']
        topology = validation_data.get('topology', [])

        console.print(f"[green]Found {len(resources)} resources[/green]")

        # Match pattern
        if verbose:
            console.print("[cyan]Matching against pattern library...[/cyan]")

        pattern_match = pattern_matcher.match_pattern(resources, topology)

        if pattern_match and verbose:
            console.print(f"[green]Matched pattern: {pattern_match.pattern_name} "
                        f"({pattern_match.similarity_score:.1%})[/green]")

        # Run validation
        if verbose:
            console.print("[cyan]Running validation rules...[/cyan]")

        context = {
            **validation_data,
            'pattern_match': pattern_match
        }

        report = engine.validate(resources, context)

        # Print report
        print_validation_report(report)

        # Save to file if requested
        if output:
            output_path = Path(output)
            with open(output_path, 'w') as f:
                json.dump(report.model_dump(mode='json'), f, indent=2, default=str)
            console.print(f"[green]Report saved to: {output}[/green]")

        # Exit with error code if validation failed
        if report.overall_status == ValidationStatus.FAILED:
            sys.exit(1)

    except Exception as e:
        console.print(f"[red]Error during validation: {e}[/red]")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.option('--pattern-id', type=str, help='Show specific pattern by ID')
def patterns(pattern_id: Optional[str]):
    """List available architecture patterns"""
    library = PatternLibrary()

    if pattern_id:
        # Show specific pattern
        pattern = library.get_pattern(pattern_id)
        if not pattern:
            console.print(f"[red]Pattern not found: {pattern_id}[/red]")
            sys.exit(1)

        console.print(f"\n[bold cyan]{pattern.metadata.name}[/bold cyan]")
        console.print(f"[dim]ID: {pattern.metadata.id} | Version: {pattern.metadata.version} | "
                     f"Status: {pattern.metadata.status}[/dim]\n")
        console.print(f"[bold]Description:[/bold]\n{pattern.metadata.description}\n")
        console.print(f"[bold]Components:[/bold]")
        for comp in pattern.architecture.components:
            comp_dict = comp if isinstance(comp, dict) else comp.model_dump()
            console.print(f"  • {comp_dict.get('name')} ({comp_dict.get('type')})")
        console.print()

    else:
        # List all patterns
        all_patterns = library.get_all_patterns()

        if not all_patterns:
            console.print("[yellow]No patterns found in library[/yellow]")
            sys.exit(0)

        table = Table(title="Available Architecture Patterns")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="bold")
        table.add_column("Version", style="dim")
        table.add_column("Status", style="green")

        for pattern in all_patterns:
            status_color = "green" if pattern.metadata.status == "approved" else "yellow"
            table.add_row(
                pattern.metadata.id,
                pattern.metadata.name,
                pattern.metadata.version,
                f"[{status_color}]{pattern.metadata.status}[/{status_color}]"
            )

        console.print(table)


@cli.command()
def rules():
    """List all validation rules"""
    register_all_rules()
    registry = get_rule_registry()

    all_rules = registry.get_all_rules()

    table = Table(title="Validation Rules")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="bold")
    table.add_column("Category", style="blue")
    table.add_column("Severity", style="yellow")

    for rule in sorted(all_rules, key=lambda r: r.id):
        severity_colors = {
            "critical": "red",
            "high": "orange1",
            "medium": "yellow",
            "low": "blue"
        }
        sev_color = severity_colors.get(rule.severity.value, "white")

        table.add_row(
            rule.id,
            rule.name,
            rule.category.value,
            f"[{sev_color}]{rule.severity.value.upper()}[/{sev_color}]"
        )

    console.print(table)


if __name__ == '__main__':
    cli()
