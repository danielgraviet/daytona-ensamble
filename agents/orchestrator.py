from __future__ import annotations

import asyncio
import json
import os
import time
import uuid
from pathlib import Path
from typing import List

from tqdm.asyncio import tqdm_asyncio

from agents.martian_client import MartianAgent
from agents.variants import VARIANTS
from human_eval import human_eval_loader
from models import types
from sandbox.sandbox_runner import DaytonaSandboxRunner
from utils import utils

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import track

console = Console()

# ---------------------------------------------------------------------
#  RICH FORMATTING HELPERS
# ---------------------------------------------------------------------
def _print_header(problem, run_id):
    console.print(
        Panel.fit(
            f"[bold green]🚀 Starting orchestration[/bold green]\n"
            f"[white]Task:[/white] {problem.task_id}\n"
            f"[white]Run ID:[/white] {run_id}\n"
            f"[white]Saving artifacts to:[/white] results/run_{run_id}",
            border_style="green",
        )
    )

def _log_gen_start(name: str):
    console.log(f"[cyan]🧠 Generating variant[/cyan] [bold]{name}[/bold]...")

def _log_gen_done(name: str, ms: float):
    console.log(f"[green]✓ Generated[/green] {name} in {ms:.1f} ms")

def _log_sandbox_start(name: str):
    console.log(f"[yellow]🏃 Running sandbox[/yellow] for [bold]{name}[/bold]...")

def _log_sandbox_done(result: types.RunResult, wall_ms: float):
    status = (
        "[green]PASSED[/green]" if result.passed else "[red]FAILED[/red]"
    )
    console.log(
        f"[white]🏁 Sandbox finished:[/white] {result.variant_name} → {status} "
        f"([blue]{result.runtime_ms:.1f} ms compute[/blue], "
        f"[magenta]{wall_ms:.1f} ms wall[/magenta])"
    )

def _print_summary(results: List[types.RunResult]):
    table = Table(title="Variant Results", header_style="bold magenta")
    table.add_column("Variant")
    table.add_column("Status")
    table.add_column("Runtime (ms)", justify="right")

    for r in results:
        status = "[green]PASS[/green]" if r.passed else "[red]FAIL[/red]"
        table.add_row(r.variant_name, status, f"{r.runtime_ms:.1f}")

    console.print("\n")
    console.print(table)
    console.print("\n")


# ---------------------------------------------------------------------
#  ORCHESTRATOR
# ---------------------------------------------------------------------

class Orchestrator:
    """
    Orchestrates:
      - prompt formatting
      - parallel LLM generation for all variants
      - parallel sandbox execution (one sandbox per variant)
      - artifact saving for debugging
      - rich CLI output
    """

    def __init__(
        self,
        llm: MartianAgent,
        artifacts_dir: str = "results",
        num_sandboxes: int | None = None,
    ):
        self.llm = llm
        self.artifacts_dir = Path(artifacts_dir)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

        self._num_sandboxes = num_sandboxes or len(VARIANTS)
        self._sandboxes: List[DaytonaSandboxRunner] = [
            DaytonaSandboxRunner() for _ in range(self._num_sandboxes)
        ]

    # ------------------------------------------------------------------
    async def run_problem(
        self,
        problem: human_eval_loader._HumanEvalDataPoint,
        run_id: str | None = None,
    ) -> List[types.RunResult]:
        """
        High level:
          - Build per-variant pipeline tasks
          - Execute LLM + sandbox in parallel
          - Show rich UI
          - Save artifacts
        """
        run_id = run_id or uuid.uuid4().hex[:6]
        run_dir = self.artifacts_dir / f"run_{run_id}"
        run_dir.mkdir(parents=True, exist_ok=True)

        # Pretty header
        _print_header(problem, run_id)

        # Prepare async tasks
        tasks = []
        for i, variant in enumerate(VARIANTS):
            sandbox = self._sandboxes[i % len(self._sandboxes)]
            tasks.append(
                self._run_single_variant(
                    problem=problem,
                    variant=variant,
                    sandbox=sandbox,
                    run_dir=run_dir,
                )
            )

        # Parallel execution with tqdm
        results: List[types.RunResult] = await tqdm_asyncio.gather(
            *tasks, total=len(tasks), desc="Running variants"
        )

        console.print("\n[bold green]✅ Orchestration complete.[/bold green]\n")
        _print_summary(results)

        return results

    # ------------------------------------------------------------------
    async def _run_single_variant(
        self,
        problem: human_eval_loader._HumanEvalDataPoint,
        variant: types.VariantSpec,
        sandbox: DaytonaSandboxRunner,
        run_dir: Path,
    ) -> types.RunResult:

        name = variant.name
        _log_gen_start(name)

        # 1. Build prompt
        prompt = utils.format_prompt_for_agent(problem, variant)

        # 2. LLM
        t0 = time.perf_counter()
        raw = await self.llm.generate_code(prompt)
        gen_ms = (time.perf_counter() - t0) * 1000
        _log_gen_done(name, gen_ms)

        # 3. Extract code
        try:
            code = utils.extract_model_solution(raw)
        except Exception as e:
            msg = f"Code extraction failed: {e}"
            console.log(f"[red]❌ {msg}[/red]")
            fail = types.RunResult(
                variant_name=name,
                passed=False,
                stdout="",
                stderr=str(e),
                runtime_ms=0.0,
                exit_code=1,
            )
            self._save_artifacts(run_dir, name, prompt, raw, "", "", fail, gen_ms)
            return fail

        # 4. Build payload
        payload = utils.format_payload(
            solution=code,
            tests=problem.test,
            entry_point=problem.entry_point,
        )

        # 5. Sandbox execution
        _log_sandbox_start(name)
        t1 = time.perf_counter()
        result = await asyncio.to_thread(sandbox.run_solution, payload, name)
        wall_ms = (time.perf_counter() - t1) * 1000
        _log_sandbox_done(result, wall_ms)

        # 6. Save artifacts
        self._save_artifacts(
            run_dir,
            name,
            prompt,
            raw,
            code,
            payload,
            result,
            gen_ms,
        )
        return result

    # ------------------------------------------------------------------
    def _save_artifacts(
        self,
        run_dir: Path,
        variant_name: str,
        prompt: str,
        raw_response: str,
        solution: str,
        payload: str,
        run_result: types.RunResult,
        generation_ms: float,
    ):
        vdir = run_dir / variant_name
        vdir.mkdir(parents=True, exist_ok=True)

        (vdir / "prompt.txt").write_text(prompt)
        (vdir / "response.txt").write_text(raw_response)
        (vdir / "solution.py").write_text(solution)
        (vdir / "payload.py").write_text(payload)

        # Save metadata
        (vdir / "result.json").write_text(
            json.dumps(
                {
                    "passed": run_result.passed,
                    "stdout": run_result.stdout,
                    "stderr": run_result.stderr,
                    "runtime_ms": run_result.runtime_ms,
                    "exit_code": run_result.exit_code,
                    "generation_ms": generation_ms,
                },
                indent=2,
            )
        )

    # ------------------------------------------------------------------
    async def shutdown(self):
        for sb in self._sandboxes:
            try:
                sb.stop()
            except Exception:
                pass
