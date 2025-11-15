# === IMPORTS
from typing import List

# === GENERATED SOLUTION ===
def has_close_elements(numbers: List[float], threshold: float) -> bool:
    # Iterate over each pair of distinct numbers in the list
    for i in range(len(numbers)):
        for j in range(i + 1, len(numbers)):
            # Calculate the absolute difference between the two numbers
            difference = abs(numbers[i] - numbers[j])
            # Check if the difference is less than the threshold
            if difference < threshold:
                return True
    # If no such pair is found, return False
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
