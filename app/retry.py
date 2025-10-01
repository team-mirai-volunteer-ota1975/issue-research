from typing import Any, Callable, Dict


SectionFn = Callable[[Dict[str, Any]], Dict[str, Any]]


def run_with_retry(section_fn: SectionFn, params: Dict[str, Any], max_retries: int = 2) -> Dict[str, Any]:
    print(f"[retry] Running {section_fn.__name__} with up to {max_retries + 1} attempts")
    outputs: list[Dict[str, Any]] = []

    for attempt in range(max_retries + 1):
        print(f"[retry] Attempt {attempt + 1}")
        result = section_fn(params)
        outputs.append(result)
        verdict = fake_llm_judgement(result)
        print(f"[retry] Verdict: {verdict}")
        if verdict == "ok":
            return result

    print("[retry] Returning last result after retries exhausted")
    return outputs[-1]


def fake_llm_judgement(result: Dict[str, Any]) -> str:
    print(f"[retry] Evaluating result: {result}")
    return "ok"
