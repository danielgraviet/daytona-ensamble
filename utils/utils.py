import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.types import Problem
    from agents.variants import VariantSpec

_PAYLOAD_TEMPLATE = """\
# === GENERATED SOLUTION ===
{solution}

# === HUMAN EVAL TESTS ===
{tests}

# === EXECUTION WRAPPER ===
if __name__ == "__main__":
    try:
        check({entry_point})
        print("TESTS PASSED")
    except Exception:
        import traceback
        print("TESTS FAILED")
        traceback.print_exc()
        raise
"""


_SOLUTION_PATTERN = re.compile(
    r"```python\s*(.*?)\s*```",
    re.DOTALL | re.IGNORECASE
)


_PROMPT_TEMPLATE = """\
You are an expert Python programmer.

Your task is to write a correct implementation of the following function.
Follow the variant instructions carefully.

# Problem Description
{problem_prompt}

# Requirements
- You must implement the function described above.
- Use the function signature exactly as provided.
- Do NOT change parameter names or types.
- Do NOT include any test code.
- Do NOT include print statements.
- Do NOT include extra text outside the python code block.
- Only return the function implementation.
- The final answer MUST be wrapped in a Python code fence like:

# Variant Instructions
{variant_description}

# Output Format
Return ONLY one python code block with the function implementation.
Do not include explanations, comments (unless allowed by variant), or any text outside the code block.
"""


def format_prompt_for_agent(problem: "Problem", variant: "VariantSpec") -> str:
    return _PROMPT_TEMPLATE.format(
        problem_prompt=problem.prompt.strip(),
        variant_description=variant.description.strip(),
    )


def format_payload(solution: str, tests: str, entry_point: str) -> str:
    """Build a single Python script suitable for Daytona's code_run()."""
    return _PAYLOAD_TEMPLATE.format(
        solution=solution.strip(),
        tests=tests.strip(),
        entry_point=entry_point.strip(),
    )


def extract_model_solution(raw_response: str) -> str:
    """Extract solution code from <solution>...</solution> tags."""
    match = _SOLUTION_PATTERN.search(raw_response)
    if not match:
        raise ValueError("Model response does not contain <solution>...</solution> tags.")
    return match.group(1).strip()
