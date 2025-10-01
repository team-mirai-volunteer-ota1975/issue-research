from typing import Dict, List


def build_reference_section(urls: List[str]) -> Dict[str, List[str]]:
    print(f"[section_refs] Building references from urls={urls}")
    section = {
        "title": "References",
        "content": urls or ["https://example.com/placeholder"],
    }
    print(f"[section_refs] Section created: {section}")
    return section
