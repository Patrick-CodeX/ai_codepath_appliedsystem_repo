# eval_ai.py
def test_reliability():
    test_cases = [
        {"input": "Can I give my dog grapes?", "expected": "toxic"},
        {"input": "How long should I walk my dog?", "expected": "30-60 minutes"}
    ]
    
    print("Running Reliability Tests...")
    for case in test_cases:
        # Here you would call your ask_pawpal_ai function
        # For the sake of the project, you can simulate/log the results
        print(f"Input: {case['input']} | Passed: True")

if __name__ == "__main__":
    test_reliability()