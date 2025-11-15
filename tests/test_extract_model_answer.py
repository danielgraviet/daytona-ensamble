from utils import utils

_MOCK_MODEL_ANSWER = """
I would love to help with that. here is my solution. 
<solution>def has_close_elements(numbers, threshold):
    for idx, elem in enumerate(numbers):
        for idx2, elem2 in enumerate(numbers):
            if idx != idx2:
                distance = abs(elem - elem2)
                if distance < threshold:
                    return True
    return False</solution>
"""

def test_extraction():
    ans = utils.extract_model_solution(raw_response=_MOCK_MODEL_ANSWER)
    print(ans)
    assert ans is not None
    assert "<solution>" not in ans
    assert "</solution>" not in ans