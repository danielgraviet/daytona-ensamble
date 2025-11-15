#!/usr/bin/env python3
import asyncio
import random
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table

from agents.martian_client import MartianAgent
from agents.orchestrator import Orchestrator
from human_eval import human_eval_loader

console = Console()

AVAILABLE_MODELS = [
    "openai/gpt-4.1-nano",
    "openai/gpt-4.1-mini",
    "openai/gpt-4.1",
    "openai/gpt-4.1-large",
]

def _banner():
    console.print(
        Panel.fit(
            "[bold magenta]⚡ Code Ensemble Interactive CLI ⚡[/bold magenta]\n"
            "Generate multiple variants → execute → evaluate → compare.\n",
            border_style="magenta",
        )
    )

async def main():
    _banner()

    # -----------------------------------------
    # 1. Ask for Model
    # -----------------------------------------
    console.print("[bold white]Select an LLM model:[/bold white]")
    for i, m in enumerate(AVAILABLE_MODELS):
        console.print(f"[cyan]{i+1}.[/cyan] {m}")

    model_choice = Prompt.ask(
        "\nEnter model number",
        choices=[str(i + 1) for i in range(len(AVAILABLE_MODELS))],
    )
    model_name = AVAILABLE_MODELS[int(model_choice) - 1]

    console.print(f"\n[green]✓ Using model:[/green] [bold]{model_name}[/bold]\n")

    # -----------------------------------------
    # 2. Ask for HumanEval task
    # -----------------------------------------
    console.print("[bold white]Which HumanEval problem do you want to run?[/bold white]")
    console.print("[cyan]Example: HumanEval/0, HumanEval/13[/cyan]")

    task_id = Prompt.ask(
        "Enter task_id or type 'random'",
        default="HumanEval/0",
    )

    if task_id.lower() == "random":
        random_id = random.randint(0, 164)
        task_id = f"HumanEval/{random_id}"
        console.print(f"[green]✓ Randomly selected:[/green] [bold]{task_id}[/bold]\n")

    # -----------------------------------------
    # 3. Load Problem
    # -----------------------------------------
    problem = human_eval_loader._load_human_eval_problem(task_id)
    if problem is None:
        console.print(f"[red]❌ Unknown task_id: {task_id}[/red]")
        return

    console.print(
        Panel.fit(
            f"[yellow]Loaded problem:[/yellow] [bold]{task_id}[/bold]\n"
            f"{problem.prompt[:200]}...\n",
            border_style="yellow",
        )
    )

    # -----------------------------------------
    # 4. Instantiate LLM + Orchestrator
    # -----------------------------------------
    agent = MartianAgent(model=model_name)
    orch = Orchestrator(llm=agent)

    # -----------------------------------------
    # 5. Run orchestration
    # -----------------------------------------
    console.print("[bold green]Starting ensemble generation + execution...[/bold green]\n")
    results = await orch.run_problem(problem)

    fastest = min(results, key=lambda r: r.runtime_ms)

    console.print(
        Panel.fit(
            f"[bold green]Fastest Variant:[/bold green] {fastest.variant_name}\n"
            f"[white]Runtime:[/white] {fastest.runtime_ms:.1f} ms\n"
            f"[white]Passed:[/white] {fastest.passed}",
            border_style="green",
        )
    )

    if Confirm.ask("Show solution code for this variant?", default=False):
        run_dir = next((p for p in orch.artifacts_dir.iterdir() if p.is_dir()), None)
        if run_dir:
            variant_dir = run_dir / fastest.variant_name
            code_path = variant_dir / "solution.py"
            if code_path.exists():
                code_text = code_path.read_text()
                console.print(Panel.fit(code_text, title=f"{fastest.variant_name}.py"))
            else:
                console.print("[red]No solution file found.[/red]")
            
    console.print("\n[bold magenta]🎉 Done![/bold magenta]\n")


if __name__ == "__main__":
    asyncio.run(main())
