from utils import utils
_MOCK_SOLUTION = """
def has_close_elements()
    for idx, elem in enumerate(numbers):
        for idx2, elem2 in enumerate(numbers):
            if idx != idx2:
                distance = abs(elem - elem2)
                    if distance < threshold:
                        return True
    return False
"""

_MOCK_TESTS = """
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
"""

def test_format():
    final_prompt = utils.format_payload(
        solution=_MOCK_SOLUTION,
        tests=_MOCK_TESTS,
        entry_point="has_close_elements"
    )
    print(final_prompt)