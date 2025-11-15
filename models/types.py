import dataclasses

@dataclasses.dataclass
class VariantSpec:
    name: str
    description: str


@dataclasses.dataclass
class RunResult:
    variant_name: str
    passed: bool
    stdout: str
    stderr: str
    runtime_ms: float
    exit_code: int
