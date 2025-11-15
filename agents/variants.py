from __future__ import annotations

import json
from pathlib import Path
from typing import List

from models import types


BASELINE = types.VariantSpec(
    name="baseline",
    description=(
        "Write the simplest correct implementation using clear Python. "
        "Use a direct, standard approach without unnecessary optimization. "
        "Return only the function implementation wrapped in Python code fences like:\n"
        "```python\n<your code here>\n```"
    ),
)

NO_EXTERNAL_LIBS = types.VariantSpec(
    name="no_external_libs",
    description=(
        "Solve the problem without using ANY external libraries or modules "
        "beyond the Python standard library. "
        "Avoid imports unless explicitly required by the function signature. "
        "Return only the function implementation wrapped in Python code fences like:\n"
        "```python\n<your code here>\n```"
    ),
)

MEMORY_EFFICIENT = types.VariantSpec(
    name="memory_efficient",
    description=(
        "Write the most memory-efficient implementation. "
        "Avoid creating unnecessary intermediate lists, sets, or copies of data. "
        "Prefer streaming, single-pass logic, and in-place operations when possible. "
        "Return only the function implementation wrapped in Python code fences like:\n"
        "```python\n<your code here>\n```"
    ),
)

PERFORMANCE_OPTIMIZED = types.VariantSpec(
    name="performance_optimized",
    description=(
        'Write a highly optimized implementation focusing on speed and algorithmic efficiency. '
        'Avoid unnecessary work, minimize loops, prefer O(n) solutions when possible, and '
        'leverage Python built-ins that offer performance benefits. '
        'Do not sacrifice correctness. '
        "Return only the function implementation wrapped in Python code fences like:\n"
        "```python\n<your code here>\n```"
    ),
)

SUPER_READABLE = types.VariantSpec(
    name="super_readable",
    description=(
        "Write the most human-readable version of the function. "
        "Use clear naming, simple control flow, and helpful comments explaining each major step. "
        "Readability and clarity are more important than brevity or performance. "
        "Return only the function implementation wrapped in Python code fences like:\n"
        "```python\n<your code here>\n```"
    ),
)


VARIANTS: List[types.VariantSpec] = [
    BASELINE,
    NO_EXTERNAL_LIBS,
    MEMORY_EFFICIENT,
    PERFORMANCE_OPTIMIZED,
    SUPER_READABLE,
]

MARKETPLACE_DIR = Path("variants_marketplace")


def _load_marketplace_variants(directory: Path) -> List[types.VariantSpec]:
    variants: List[types.VariantSpec] = []
    if not directory.exists():
        return variants

    for manifest in sorted(directory.glob("*.json")):
        try:
            data = json.loads(manifest.read_text())
        except json.JSONDecodeError:
            continue

        name = data.get("name")
        description = data.get("description")
        if not name or not description:
            continue

        variants.append(types.VariantSpec(name=name, description=description))

    return variants


VARIANTS.extend(_load_marketplace_variants(MARKETPLACE_DIR))
