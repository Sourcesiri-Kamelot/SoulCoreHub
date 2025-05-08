import click
from typing import Optional
from airtrain.integrations.openai.skills import OpenAIChatSkill, OpenAIInput
from airtrain.integrations.anthropic.skills import AnthropicChatSkill, AnthropicInput
import os
from dotenv import load_dotenv
import sys
from .builder import build

# Load environment variables
load_dotenv()


def initialize_chat(provider: str = "openai"):
    """Initialize chat skill based on provider"""
    if provider == "openai":
        return OpenAIChatSkill()
    elif provider == "anthropic":
        return AnthropicChatSkill()
    else:
        raise ValueError(f"Unsupported provider: {provider}")


@click.group()
def cli():
    """Airtrain CLI - Your AI Agent Building Assistant"""
    pass


@cli.command()
@click.option(
    "--provider",
    type=click.Choice(["openai", "anthropic"]),
    default="openai",
    help="The AI provider to use",
)
@click.option(
    "--temperature",
    type=float,
    default=0.7,
    help="Temperature for response generation (0.0-1.0)",
)
@click.option(
    "--system-prompt",
    type=str,
    default="You are a helpful AI assistant that helps users build their own AI agents. Be helpful and provide clear explanations.",
    help="System prompt to guide the model",
)
def chat(provider: str, temperature: float, system_prompt: str):
    """Start an interactive chat session with Airtrain"""
    try:
        skill = initialize_chat(provider)

        click.echo(f"\nWelcome to Airtrain! Using {provider.upper()} as the provider.")
        click.echo("Type 'exit' to end the conversation.")
        click.echo("Type 'clear' to clear the conversation history.\n")

        conversation_history = []

        while True:
            user_input = click.prompt("You", type=str)

            if user_input.lower() == "exit":
                click.echo("\nGoodbye! Have a great day!")
                break

            if user_input.lower() == "clear":
                conversation_history = []
                click.echo("\nConversation history cleared!")
                continue

            try:
                if provider == "openai":
                    input_data = OpenAIInput(
                        user_input=user_input,
                        system_prompt=system_prompt,
                        conversation_history=conversation_history,
                        model="gpt-4o",
                        temperature=temperature,
                    )
                else:
                    input_data = AnthropicInput(
                        user_input=user_input,
                        system_prompt=system_prompt,
                        conversation_history=conversation_history,
                        model="claude-3-opus-20240229",
                        temperature=temperature,
                    )

                result = skill.process(input_data)

                # Update conversation history
                conversation_history.extend(
                    [
                        {"role": "user", "content": user_input},
                        {"role": "assistant", "content": result.response},
                    ]
                )

                click.echo(f"\nAirtrain: {result.response}\n")

            except Exception as e:
                click.echo(f"\nError: {str(e)}\n")

    except Exception as e:
        click.echo(f"Failed to initialize chat: {str(e)}")
        sys.exit(1)


# Add to existing cli group
cli.add_command(build)


def main():
    """Main entry point for the CLI"""
    cli()


if __name__ == "__main__":
    main()
