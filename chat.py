"""
cs_tutor/chat.py
A terminal chat app for the Axiom CS Tutor.
Uses the Ollama Python library to call your custom model.
"""

import os
import sys

# Force UTF-8 output on Windows so Rich renders correctly
os.environ.setdefault("PYTHONUTF8", "1")

import ollama
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

MODEL_NAME = "axiom"
console = Console()

BANNER = """
+-------------------------------------------+
|         AXIOM  -  CS Tutor                |
|   Ask anything about computer science     |
|   Type  /exit  to quit                    |
|   Type  /clear to reset the conversation  |
+-------------------------------------------+
"""


def get_response(messages: list[dict]) -> str:
    """Send messages to Axiom and return the response text."""
    response = ollama.chat(
        model=MODEL_NAME,
        messages=messages,
    )
    return response.message.content


def main():
    console.print(BANNER, style="bold cyan")

    messages: list[dict] = []

    while True:
        try:
            user_input = console.input("[bold green]You -> [/]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Goodbye![/]")
            sys.exit(0)

        if not user_input:
            continue

        # Commands
        if user_input.lower() in ("/exit", "/quit"):
            console.print("[dim]Goodbye! Keep learning![/]")
            break

        if user_input.lower() == "/clear":
            messages.clear()
            console.clear()
            console.print(BANNER, style="bold cyan")
            console.print("[dim]Conversation cleared.[/]\n")
            continue

        # Add user message to history
        messages.append({"role": "user", "content": user_input})

        # Get Axiom's response
        try:
            with console.status("[bold cyan]Axiom is thinking...[/]", spinner="dots"):
                response_text = get_response(messages)
        except Exception as e:
            console.print(f"[bold red]Error:[/] {e}")
            messages.pop()  # remove the failed message from history
            continue

        # Add assistant message to history
        messages.append({"role": "assistant", "content": response_text})

        # Render as markdown in a panel
        md = Markdown(response_text)
        panel = Panel(
            md,
            title="[bold cyan]Axiom[/]",
            border_style="cyan",
            padding=(1, 2),
        )
        console.print(panel)
        console.print()


if __name__ == "__main__":
    main()
