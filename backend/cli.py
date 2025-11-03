"""Main entry point for HiveMind Discovery to Requirements system."""

import sys
import json
import argparse
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown
from rich import print as rprint

from utils.config import Config
from utils.gemini_client import GeminiClient
from hivemind.architecture import HiveMindArchitecture
from hivemind.consensus import ConsensusStrategy
from hivemind.methodology import AgileMethodology, MethodologyFactory


console = Console()


def display_banner():
    """Display welcome banner."""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║        🐝 HIVEMIND ARCHITECTURE                              ║
║        Discovery → Technical Requirements                     ║
║                                                               ║
║        Powered by Google Gemini & Agent-to-Agent Protocol    ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""
    console.print(banner, style="bold cyan")


def select_methodology() -> AgileMethodology:
    """Allow user to select agile methodology."""
    console.print("\n[bold blue]🎯 Select Agile Methodology:[/bold blue]")
    
    methodologies = MethodologyFactory.get_available_methodologies()
    
    table = Table(title="Available Methodologies")
    table.add_column("Option", style="cyan", no_wrap=True)
    table.add_column("Methodology", style="magenta")
    table.add_column("Description", style="white")
    
    for i, methodology in enumerate(methodologies, 1):
        context = MethodologyFactory.get_context(methodology)
        table.add_row(str(i), methodology.value.upper(), context.description)
    
    console.print(table)
    
    while True:
        try:
            choice = input(f"\nEnter your choice (1-{len(methodologies)}): ").strip()
            choice_num = int(choice)
            if 1 <= choice_num <= len(methodologies):
                selected = methodologies[choice_num - 1]
                context = MethodologyFactory.get_context(selected)
                console.print(f"\n[green]✅ Selected: {context.name}[/green]")
                console.print(f"[dim]{context.description}[/dim]")
                return selected
            else:
                console.print(f"[red]❌ Please enter a number between 1 and {len(methodologies)}[/red]")
        except ValueError:
            console.print("[red]❌ Please enter a valid number[/red]")
        except KeyboardInterrupt:
            console.print("\n[yellow]👋 Goodbye![/yellow]")
            sys.exit(0)


def get_business_need_from_user() -> str:
    """Get business need from user input."""
    console.print("\n[bold yellow]📝 Describe your software development need:[/bold yellow]")
    console.print("[dim]Be as detailed as possible about what you want to build and why.[/dim]\n")

    lines = []
    console.print("[dim]Enter your need (press Ctrl+D or Ctrl+Z when done):[/dim]")

    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass

    return "\n".join(lines).strip()


def display_result_summary(result) -> None:
    """Display execution result summary."""
    console.print("\n")
    console.rule("[bold green]Execution Summary[/bold green]")

    # Create summary table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Total Execution Time", f"{result.execution_time:.2f}s")
    table.add_row("Worker Agents", str(len(result.worker_responses)))
    table.add_row("Consensus Level", f"{result.consensus_result.consensus_level:.1%}")
    table.add_row("Final Confidence", f"{result.supervisor_response.confidence:.1%}")

    console.print(table)

    # Worker responses summary
    console.print("\n[bold cyan]Worker Agent Confidence Levels:[/bold cyan]")
    worker_table = Table(show_header=True)
    worker_table.add_column("Agent", style="cyan")
    worker_table.add_column("Confidence", style="green")
    worker_table.add_column("Status", style="yellow")

    for response in result.worker_responses:
        status = "✓ High" if response.confidence > 0.7 else "⚠ Medium" if response.confidence > 0.5 else "✗ Low"
        worker_table.add_row(
            response.agent_name,
            f"{response.confidence:.2%}",
            status
        )

    console.print(worker_table)


def save_requirements_document(content: str, output_path: Path) -> None:
    """Save the final requirements document."""
    try:
        # Parse JSON and save pretty-printed
        requirements = json.loads(content)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(requirements, f, indent=2, ensure_ascii=False)

        console.print(f"\n[bold green]✓[/bold green] Requirements document saved to: [cyan]{output_path}[/cyan]")

    except json.JSONDecodeError:
        # If not valid JSON, save as-is
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        console.print(f"\n[bold green]✓[/bold green] Requirements document saved to: [cyan]{output_path}[/cyan]")


def display_executive_summary(requirements_json: str) -> None:
    """Display executive summary from requirements."""
    try:
        requirements = json.loads(requirements_json)
        exec_summary = requirements.get("executive_summary", {})

        console.print("\n")
        console.rule("[bold green]Executive Summary[/bold green]")

        # Overview
        if "overview" in exec_summary:
            console.print(Panel(
                exec_summary["overview"],
                title="[bold]Overview[/bold]",
                border_style="cyan"
            ))

        # Business objectives
        if "business_objectives" in exec_summary:
            console.print("\n[bold cyan]Business Objectives:[/bold cyan]")
            for obj in exec_summary["business_objectives"]:
                console.print(f"  • {obj}")

        # Key deliverables
        if "key_deliverables" in exec_summary:
            console.print("\n[bold cyan]Key Deliverables:[/bold cyan]")
            for deliv in exec_summary["key_deliverables"]:
                console.print(f"  • {deliv}")

        # Timeline
        if "timeline" in exec_summary:
            console.print(f"\n[bold cyan]Timeline:[/bold cyan] {exec_summary['timeline']}")

    except (json.JSONDecodeError, KeyError) as e:
        console.print(f"[yellow]⚠ Could not parse executive summary: {str(e)}[/yellow]")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="HiveMind Architecture - Discovery to Technical Requirements"
    )
    parser.add_argument(
        "--input",
        "-i",
        type=str,
        help="Path to file containing business need description"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="technical_requirements.json",
        help="Output path for requirements document (default: technical_requirements.json)"
    )
    parser.add_argument(
        "--methodology",
        "-m",
        type=str,
        choices=["scrum", "safe", "kanban"],
        help="Agile methodology to use (scrum, safe, kanban)"
    )
    parser.add_argument(
        "--consensus",
        "-c",
        type=str,
        choices=["weighted_voting", "majority", "unanimous", "confidence_threshold"],
        default="weighted_voting",
        help="Consensus strategy to use (default: weighted_voting)"
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Quiet mode - minimal output"
    )

    args = parser.parse_args()

    # Display banner (unless quiet)
    if not args.quiet:
        display_banner()

    try:
        # Load configuration
        if not args.quiet:
            console.print("\n[bold]Initializing HiveMind System...[/bold]")

        config = Config()

        if not args.quiet:
            console.print(f"[green]✓[/green] Configuration loaded: {config}")

        # Initialize Gemini client
        gemini_client = GeminiClient(
            api_key=config.get_api_key(),
            model_name=config.gemini_model,
            temperature=config.temperature,
            max_tokens=config.max_tokens
        )

        if not args.quiet:
            console.print(f"[green]✓[/green] Gemini client initialized")

        # Get consensus strategy
        consensus_strategy = ConsensusStrategy(args.consensus)
        
        # Select methodology
        if args.methodology:
            try:
                methodology = AgileMethodology(args.methodology)
            except ValueError:
                console.print(f"[red]❌ Invalid methodology: {args.methodology}[/red]")
                console.print("[yellow]Available options: scrum, safe, kanban[/yellow]")
                return 1
        else:
            if not args.quiet:
                methodology = select_methodology()
            else:
                methodology = AgileMethodology.SCRUM  # Default for quiet mode

        if not args.quiet:
            context = MethodologyFactory.get_context(methodology)
            console.print(f"[green]✓[/green] Methodology selected: {context.name}")

        # Initialize HiveMind
        hivemind = HiveMindArchitecture(
            gemini_client=gemini_client,
            methodology=methodology,
            consensus_strategy=consensus_strategy
        )

        if not args.quiet:
            console.print(f"[green]✓[/green] HiveMind architecture initialized")
            console.print(f"    Workers: {len(hivemind.worker_agents)}")
            console.print(f"    Methodology: {methodology.value.upper()}")
            console.print(f"    Consensus Strategy: {consensus_strategy.value}")

        # Get business need
        if args.input:
            # Load from file
            with open(args.input, 'r', encoding='utf-8') as f:
                business_need = f.read().strip()

            if not args.quiet:
                console.print(f"\n[green]✓[/green] Business need loaded from: [cyan]{args.input}[/cyan]")
        else:
            # Get from user input
            business_need = get_business_need_from_user()

        if not business_need:
            console.print("[bold red]✗[/bold red] No business need provided. Exiting.")
            return 1

        # Display business need
        if not args.quiet:
            console.print("\n")
            console.rule("[bold yellow]Business Need[/bold yellow]")
            console.print(Panel(
                business_need,
                border_style="yellow"
            ))

        # Execute HiveMind
        if not args.quiet:
            console.print("\n[bold]Starting HiveMind Analysis...[/bold]\n")

        result = hivemind.execute(business_need, verbose=not args.quiet)

        # Display results
        if not args.quiet:
            display_result_summary(result)
            display_executive_summary(result.supervisor_response.content)

        # Save requirements document
        output_path = Path(args.output)
        save_requirements_document(result.supervisor_response.content, output_path)

        # Offer to save communication log
        if not args.quiet:
            console.print("\n[bold]Would you like to save the communication log? (y/n):[/bold] ", end="")
            save_log = input().strip().lower()

            if save_log == 'y':
                log_path = output_path.parent / f"{output_path.stem}_communication_log.txt"
                with open(log_path, 'w', encoding='utf-8') as f:
                    f.write(result.communication_log)
                console.print(f"[green]✓[/green] Communication log saved to: [cyan]{log_path}[/cyan]")

        if not args.quiet:
            console.print("\n[bold green]🎉 Process completed successfully![/bold green]")

        return 0

    except ValueError as e:
        console.print(f"\n[bold red]✗ Configuration Error:[/bold red] {str(e)}")
        console.print("\n[yellow]Please check your .env file and ensure GOOGLE_API_KEY is set.[/yellow]")
        return 1

    except KeyboardInterrupt:
        console.print("\n\n[yellow]⚠ Process interrupted by user.[/yellow]")
        return 130

    except Exception as e:
        console.print(f"\n[bold red]✗ Error:[/bold red] {str(e)}")
        import traceback
        console.print("\n[dim]Full traceback:[/dim]")
        console.print(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())
