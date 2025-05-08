import click
from airtrain.builder.agent_builder import AgentBuilder
import json


@click.command()
def build():
    """Build a custom AI agent through an interactive process"""
    try:
        builder = AgentBuilder()
        specification = builder.build_agent()

        # Display the final specification
        click.echo("\n=== Agent Specification ===")
        click.echo(json.dumps(specification.model_dump(), indent=2))

        click.echo(
            "\nAgent specification complete! You can now use this specification to initialize your agent."
        )

    except Exception as e:
        click.echo(f"\nError building agent: {str(e)}")
        return 1
