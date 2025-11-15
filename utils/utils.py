import re

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
    r"<solution>\s*(.*?)\s*</solution>",
    re.DOTALL | re.IGNORECASE
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
