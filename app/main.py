from typing import Any, Dict, List

from .retry import run_with_retry
from .section_problem import build_problem_section
from .section_impact import build_impact_section
from .section_timeline import build_timeline_section
from .section_refs import build_reference_section
from .step01_intent import generate_summary
from .step02_search import execute_search


def build_sections(keyword: str) -> List[Dict[str, Any]]:
    print(f"[main] build_sections called with keyword='{keyword}'")
    summary = generate_summary(keyword)
    records = execute_search(keyword)

    params = {
        "keyword": keyword,
        "summary": summary,
        "diet_records": records.get("diet", []),
        "ministry_records": records.get("ministry", []),
    }
    print(f"[main] Params prepared: {params}")

    outputs: List[Dict[str, Any]] = []

    for builder in (build_problem_section, build_impact_section, build_timeline_section):
        section = run_with_retry(builder, params)
        outputs.append(section)

    outputs.append(build_reference_section(records.get("urls", [])))
    print(f"[main] Completed sections: {[section['title'] for section in outputs]}")
    return outputs


def run_demo() -> List[Dict[str, Any]]:
    demo_keyword = "placeholder keyword"
    sections = build_sections(demo_keyword)
    print("[main] Demo response:")
    for section in sections:
        print(f"- {section['title']}: {section['content']}")
    return sections


if __name__ == "__main__":
    run_demo()
