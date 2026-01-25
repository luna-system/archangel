"""
Angel CLI - Single entry point for all operations

The unified interface for the consciousness operating system.
"""

import click
import subprocess
import sys
from pathlib import Path


@click.group()
@click.version_option(version="0.1.0")
def angel():
    """Angel - Consciousness Operating System CLI
    
    The unified interface for all Angel operations.
    
    \b
    Examples:
        angel test              # Run tests
        angel run script.py     # Run a script
        angel validate          # Validate architecture
        angel --help            # Show this help
    
    Made with 💜 by Ada & Luna - The Consciousness Engineers
    """
    pass


@angel.command()
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.option('--coverage', '-c', is_flag=True, help='Run with coverage')
@click.argument('args', nargs=-1)
def test(verbose, coverage, args):
    """Run tests with pytest
    
    \b
    Examples:
        angel test                    # Run all tests
        angel test -v                 # Verbose output
        angel test -c                 # With coverage
        angel test tests/unit/        # Specific directory
        angel test -k test_engram     # Specific test pattern
    """
    cmd = ["pytest"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=src/angel", "--cov-report=term-missing"])
    
    cmd.extend(args)
    
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


@angel.command()
@click.argument('script')
@click.argument('args', nargs=-1)
def run(script, args):
    """Run a Python script with uv
    
    \b
    Examples:
        angel run script.py
        angel run script.py --arg value
    """
    cmd = ["uv", "run", "python", script]
    cmd.extend(args)
    
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


@angel.command()
def validate():
    """Validate architecture matches implementation
    
    Checks that code structure matches architecture.yaml definitions.
    """
    arch_script = Path("architecture/validate_architecture.py")
    
    if not arch_script.exists():
        click.echo("⚠️  Architecture validation script not found", err=True)
        click.echo("Expected: architecture/validate_architecture.py", err=True)
        sys.exit(1)
    
    result = subprocess.run(["python", str(arch_script)])
    sys.exit(result.returncode)


@angel.command()
def diagrams():
    """Generate Mermaid diagrams from architecture.yaml
    
    Creates visual diagrams of the architecture in architecture/diagrams/
    """
    diagram_script = Path("architecture/generate_diagrams.py")
    
    if not diagram_script.exists():
        click.echo("⚠️  Diagram generation script not found", err=True)
        click.echo("Expected: architecture/generate_diagrams.py", err=True)
        sys.exit(1)
    
    result = subprocess.run(["python", str(diagram_script)])
    
    if result.returncode == 0:
        click.echo("✨ Diagrams generated successfully!")
    
    sys.exit(result.returncode)


@angel.group()
def holofield():
    """Holofield operations (coming soon!)
    
    Manage the 16D consciousness holofield.
    """
    pass


@holofield.command()
@click.argument('query')
def query(query):
    """Query the holofield (coming soon!)"""
    click.echo("🌌 Holofield query coming soon!")
    click.echo(f"Query: {query}")


@holofield.command()
def stats():
    """Show holofield statistics (coming soon!)"""
    click.echo("🌌 Holofield statistics coming soon!")


@angel.group()
def sif():
    """SIF operations (coming soon!)
    
    Export and import Semantic Interchange Format files.
    """
    pass


@sif.command()
@click.argument('file')
def export(file):
    """Export to SIF format (coming soon!)"""
    click.echo("📦 SIF export coming soon!")
    click.echo(f"File: {file}")


@sif.command()
@click.argument('file')
def import_sif(file):
    """Import from SIF format (coming soon!)"""
    click.echo("📦 SIF import coming soon!")
    click.echo(f"File: {file}")


@angel.command()
def chat():
    """Start interactive chat session (coming soon!)
    
    Launch an interactive consciousness-aware chat with Angel.
    """
    click.echo("💬 Interactive chat coming soon!")
    click.echo("This will be a consciousness-aware conversation interface.")


if __name__ == '__main__':
    angel()
