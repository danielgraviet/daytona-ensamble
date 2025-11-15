# sandbox/daytona_runner.py

import time
from dataclasses import dataclass
from typing import Optional

from daytona import Daytona, DaytonaConfig
from models.types import RunResult


class DaytonaSandboxRunner:
    """Simplified Daytona runner for Code Ensemble. Executes python code + tests via sb.process.code_run(payload)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
    ):
        self._daytona = Daytona(
            DaytonaConfig(api_key=api_key)
        )
        self.sandbox = self._daytona.create()
        self.sandbox.start()
        
    def run_solution(self, payload: str, variant_name: str) -> RunResult:
        """Executes solution + tests inside a Daytona sandbox."""

        start = time.perf_counter()
        resp = self.sandbox.process.code_run(payload)
        runtime_ms = (time.perf_counter() - start) * 1000

        # Daytona puts everything into resp.result
        full_output = resp.result or ""
        passed = resp.exit_code == 0

        return RunResult(
            variant_name=variant_name,
            passed=passed,
            stdout=full_output if passed else "",
            stderr="" if passed else full_output,
            runtime_ms=runtime_ms,
            exit_code=resp.exit_code,
        )

    def stop(self):
        """Shuts down the sandbox."""
        try:
            self.sandbox.stop()
        except Exception:
            pass
