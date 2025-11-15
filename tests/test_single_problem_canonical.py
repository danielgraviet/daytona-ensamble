from sandbox import sandbox_runner
import pytest

_MOCK_PAYLOAD = """
def has_close_elements(numbers, threshold):
    for idx, elem in enumerate(numbers):
        for idx2, elem2 in enumerate(numbers):
            if idx != idx2:
                distance = abs(elem - elem2)
                if distance < threshold:
                    return True
    return False

# === HUMAN EVAL TESTS ===
METADATA = {
'author': 'jt',
'dataset': 'test'
}

def check(candidate):
    assert candidate([1.0, 2.0, 3.9, 4.0, 5.0, 2.2], 0.3) == True
    assert candidate([1.0, 2.0, 3.9, 4.0, 5.0, 2.2], 0.05) == False
    assert candidate([1.0, 2.0, 5.9, 4.0, 5.0], 0.95) == True
    assert candidate([1.0, 2.0, 5.9, 4.0, 5.0], 0.8) == False
    assert candidate([1.0, 2.0, 3.0, 4.0, 5.0, 2.0], 0.1) == True
    assert candidate([1.1, 2.2, 3.1, 4.1, 5.1], 1.0) == True
    assert candidate([1.1, 2.2, 3.1, 4.1, 5.1], 0.5) == False

# === EXECUTION WRAPPER ===
if __name__ == "__main__":
    try:
        check(has_close_elements)
        print("TESTS PASSED")
    except Exception:
        import traceback
        print("TESTS FAILED")
        traceback.print_exc()
        raise
"""

@pytest.mark.asyncio
async def test_single_canonical_solution():
    runner = sandbox_runner.DaytonaSandboxRunner()
    result = runner.run_solution(payload=_MOCK_PAYLOAD, variant_name="baseline")
    print(result)
    assert result is not None
    
    