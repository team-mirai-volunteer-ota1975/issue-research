from fastapi import FastAPI, Query

from app.main import build_sections


app = FastAPI(title="Political Keyword Deep Dive API")


@app.get("/health")
def health_check() -> dict[str, str]:
    print("[api] Health check called")
    return {"status": "ok"}


@app.get("/search")
def search(keyword: str = Query(..., description="Keyword to analyze")) -> dict[str, object]:
    print(f"[api] /search called with keyword='{keyword}'")
    sections = build_sections(keyword)
    return {"keyword": keyword, "sections": sections}
