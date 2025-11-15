# import asyncio

# from agents.martian_client import MartianAgent
# from agents.variants import VARIANTS
# from utils import utils
# from human_eval import human_eval_loader
# from models.types import RunResult
# from tqdm.asyncio import tqdm_asyncio


# class Orchestrator:
#     def __init__(self, llm: MartianAgent):
#         self.llm = llm

#     async def _generate_all(self, problem: human_eval_loader._HumanEvalDataPoint) -> list[str]:
#         tasks = []

#         for variant in VARIANTS:
#             prompt = utils.format_prompt_for_agent(problem, variant)
#             task = self.llm.generate_code(prompt)
#             tasks.append(task)

#         # LLM parallel execution
#         results = await tqdm_asyncio.gather(*tasks)
#         return results
    
# # agents/orchestrator.py

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


class Orchestrator:
    """
    Orchestrates:
      - prompt formatting
      - parallel LLM generation for all variants
      - parallel sandbox execution (one sandbox per variant)
      - artifact saving for debugging

    Usage:
        orch = Orchestrator(llm=MartianAgent())
        results = await orch.run_problem(problem)
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

        # One sandbox per variant (or override with num_sandboxes)
        self._num_sandboxes = num_sandboxes or len(VARIANTS)
        self._sandboxes: List[DaytonaSandboxRunner] = [
            DaytonaSandboxRunner() for _ in range(self._num_sandboxes)
        ]

    async def run_problem(
        self,
        problem: human_eval_loader._HumanEvalDataPoint,
        run_id: str | None = None,
    ) -> List[types.RunResult]:
        """
        High-level entrypoint:
          - spins a per-variant task
          - each task does: prompt -> LLM -> extract -> payload -> sandbox
          - returns list[RunResult]
        """
        if run_id is None:
            run_id = uuid.uuid4().hex[:6]

        run_dir = self.artifacts_dir / f"run_{run_id}"
        run_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n🚀 Starting orchestration for {problem.task_id} (run_id={run_id})")
        print(f"Artifacts will be saved under: {run_dir}\n")

        tasks = []
        # Map each variant to a sandbox (reuse if fewer sandboxes than variants)
        for idx, variant in enumerate(VARIANTS):
            sandbox = self._sandboxes[idx % len(self._sandboxes)]
            tasks.append(
                self._run_single_variant(
                    problem=problem,
                    variant=variant,
                    sandbox=sandbox,
                    run_dir=run_dir,
                )
            )

        # Run all variant pipelines in parallel with a progress bar
        results: List[types.RunResult] = await tqdm_asyncio.gather(
            *tasks,
            desc="Running variants",
            total=len(tasks),
        )

        print("\n✅ Orchestration complete.\n")
        return results

    async def _run_single_variant(
        self,
        problem: human_eval_loader._HumanEvalDataPoint,
        variant: types.VariantSpec,
        sandbox: DaytonaSandboxRunner,
        run_dir: Path,
    ) -> types.RunResult:
        """
        Full pipeline for a single variant:
          1. Build prompt
          2. Call LLM
          3. Extract solution
          4. Build execution payload
          5. Run in Daytona sandbox (in a thread, since it's sync)
          6. Save artifacts
        """
        variant_name = variant.name
        print(f"🧠 [{variant_name}] Generating solution...")

        # 1. Build prompt
        prompt = utils.format_prompt_for_agent(problem, variant)

        # 2. LLM generation
        t0 = time.perf_counter()
        raw_response = await self.llm.generate_code(prompt)
        gen_ms = (time.perf_counter() - t0) * 1000.0
        print(f"🧠 [{variant_name}] Generation finished in {gen_ms:.1f} ms")

        # 3. Extract code from model response
        try:
            solution = utils.extract_model_solution(raw_response)
        except Exception as exc:
            # Extraction failed: create a synthetic failing RunResult
            err_msg = f"Extraction failed for variant {variant_name}: {exc}"
            print(f"❌ [{variant_name}] {err_msg}")
            result = types.RunResult(
                variant_name=variant_name,
                passed=False,
                stdout="",
                stderr=err_msg,
                runtime_ms=0.0,
                exit_code=1,
            )
            self._save_artifacts(
                run_dir=run_dir,
                variant_name=variant_name,
                prompt=prompt,
                raw_response=raw_response,
                solution="",
                payload="",
                run_result=result,
                generation_ms=gen_ms,
            )
            return result

        # 4. Build payload for Daytona
        payload = utils.format_payload(
            solution=solution,
            tests=problem.test,
            entry_point=problem.entry_point,
        )

        # 5. Execute in sandbox (sandbox.run_solution is sync, so offload to thread)
        print(f"🏃 [{variant_name}] Running in sandbox...")
        t1 = time.perf_counter()
        run_result: types.RunResult = await asyncio.to_thread(
            sandbox.run_solution, payload, variant_name
        )
        total_exec_ms = (time.perf_counter() - t1) * 1000.0
        print(
            f"🏁 [{variant_name}] Sandbox finished "
            f"(tests_passed={run_result.passed}, runtime_ms={run_result.runtime_ms:.1f}, "
            f"wall_ms={total_exec_ms:.1f})"
        )

        # 6. Save artifacts for debugging
        self._save_artifacts(
            run_dir=run_dir,
            variant_name=variant_name,
            prompt=prompt,
            raw_response=raw_response,
            solution=solution,
            payload=payload,
            run_result=run_result,
            generation_ms=gen_ms,
        )

        return run_result

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
    ) -> None:
        """
        Save debugging artifacts per variant:
          - prompt.txt
          - response.txt
          - solution.py
          - payload.py
          - result.json
        """
        vdir = run_dir / variant_name
        vdir.mkdir(parents=True, exist_ok=True)

        (vdir / "prompt.txt").write_text(prompt, encoding="utf-8")
        (vdir / "response.txt").write_text(raw_response, encoding="utf-8")
        (vdir / "solution.py").write_text(solution, encoding="utf-8")
        (vdir / "payload.py").write_text(payload, encoding="utf-8")

        result_dict = {
            "variant_name": run_result.variant_name,
            "passed": run_result.passed,
            "stdout": run_result.stdout,
            "stderr": run_result.stderr,
            "runtime_ms": run_result.runtime_ms,
            "exit_code": run_result.exit_code,
            "generation_ms": generation_ms,
        }
        (vdir / "result.json").write_text(
            json.dumps(result_dict, indent=2),
            encoding="utf-8",
        )

    async def shutdown(self) -> None:
        """Stop all sandboxes."""
        for sb in self._sandboxes:
            try:
                sb.stop()
            except Exception:
                pass
