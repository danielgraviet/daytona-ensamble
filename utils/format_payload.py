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

def format_payload(solution: str, tests: str, entry_point: str) -> str:
    """Build a single Python script suitable for Daytona's code_run()."""
    return _PAYLOAD_TEMPLATE.format(
        solution=solution.strip(),
        tests=tests.strip(),
        entry_point=entry_point.strip(),
    )
