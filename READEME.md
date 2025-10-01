# 政治分野特化型 キーワード深掘り検索サービス

## 概要
本サービスは、政治分野（国会・省庁議事録、法案、政策テーマなど）に特化した検索・要約システムです。  
ユーザーが入力したキーワード（例: 「医療DX」「医療法改正案」）について、  
関連する議論や問題点を深掘りして提示します。

---

## 大まかな仕様
1. **意図解析 & 概要生成**  
   - キーワードの種類をLLMで判定（法案名か政策テーマかなど）  
   - 不足情報があればWeb検索で補完し、概要を作成  

2. **議事録検索**  
   - 国会議事録API（kokkai.ndl.go.jp）を利用  
   - 自作RAG API（例: gov-meeting-rag.vercel.app）を利用  
   - 不足時はWeb検索を併用  

3. **セクションごとの分析**  
   - 問題点抽出  
   - 影響を受ける人/組織の抽出  
   - 議論のタイムライン整理  
   - 参考URLまとめ  

4. **リトライロジック**  
   - LLMに「不足があるか」を自己評価させ、不足なら再検索  
   - 複数案を生成し比較 → 最良を採用  

---

## アーキテクチャ

```

ユーザー入力（キーワード）
│
▼
main.py
├─ step01_intent.py   → 意図解析 & 概要生成
├─ step02_search.py   → 国会API & 自作API検索
├─ section_problem.py → 問題点抽出
├─ section_impact.py  → 影響対象抽出
├─ section_timeline.py→ 議論タイムライン生成
└─ section_refs.py    → URLまとめ

````

- **バックエンド**: FastAPI  
- **データソース**: 国会API、自作API、Web検索  
- **LLM**: GPT-5 / GPT-5-mini（精度とコストのバランスで切替）  
- **フロントエンド**: Next.js / React（カードUI表示を想定）  

---

## セクション設計

### 共通インターフェース
各セクションは以下を受け取り、JSONで返す。

#### 入力
```python
params = {
    "keyword": "医療DX",
    "summary": "地域医療構想見直しと医療DX推進に関する法案...",
    "diet_records": [ ... ],     # 国会議事録
    "ministry_records": [ ... ], # 省庁議事録
}
````

#### 出力

```json
{
  "title": "問題点",
  "content": [
    "医師偏在対策の効果に不透明感がある",
    "医療DX基盤の整備に高コストが予想される"
  ]
}
```

### メイン処理

```python
def main(keyword: str):
    summary = step01(keyword)
    records = step02(keyword)

    params = {
        "keyword": keyword,
        "summary": summary,
        "diet_records": records["diet"],
        "ministry_records": records["ministry"]
    }

    outputs = []
    for section in [problem, impact, timeline]:
        outputs.append(run_with_retry(section, params))

    outputs.append({"title": "参考URL", "content": records["urls"]})
    return outputs
```

---

## リトライ共通ロジック

```python
def run_with_retry(section_fn, params, max_retries=2):
    outputs = []
    for attempt in range(max_retries):
        result = section_fn(params)
        outputs.append(result)

        eval_prompt = f"""
        以下の出力は妥当ですか？不足があるなら "不足あり" と返してください。
        出力: {result}
        """
        verdict = llm(eval_prompt)
        if "不足あり" not in verdict:
            return result

    compare_prompt = f"""
    以下は複数回の試行結果です。最も適切なものを1つ選び返してください。
    {outputs}
    """
    best = llm(compare_prompt)
    return best
```

* **レベル1**: 自己評価で「不足あり」チェック
* **レベル2**: 複数案を比較して最良を選択
* **レベル3**: 必要に応じてWeb検索を追加

---

## 出力例

```
# 1. 検索対象
医療法等の一部を改正する法律案

# 2. 概要
高齢化に伴う医療需要の変化に対応し、地域医療構想の見直し...

# 3. 問題点
- 医師偏在の是正策が十分か不透明
- 医療DXの実現可能性に懸念

# 4. 影響を受ける人/組織
- 地域医療機関
- 高齢患者
- 自治体の医療行政部門

# 5. 議論タイムライン
- 2024/05/01 厚労委員会で初回審議、医師偏在問題が指摘
- 2024/06/15 自民党部会にて医療DX関連議論

# 6. 参考URL
- https://kokkai.ndl.go.jp/api/...
- https://www.mhlw.go.jp/stf/shingi2/...
```

---

## 特徴

* **セクション独立性**: 追加・削除・順番変更が容易
* **Web検索は各セクションで必要に応じて実施可能**
* **リトライ共通化**: 不足判定・再実行・比較を自動化
* **JSON返却**: APIやUIでの再利用性が高い
