---
date : 2025-09-10
tags: ['2025-09']
categories: ['스터디', 'Langchain']
bookHidden: true
title: "Langchain #1 노션 데이터로 나만의 RAG 시스템 구축하기 (스터디)"
---

# Langchain #1 노션 데이터로 나만의 RAG 시스템 구축하기 (스터디)

#2025-09-10

---

- 스터디하는친구가 만들어준코드인데 내 노션으로 돌려봤다!

- 실습 목적
  - 노션 데이터를 임베딩 생성하여 FAISS 벡터 스토어에 저장하고 이를 기반으로 유사 문서 검색을 수행하며, 청킹 기법을 통해 데이터 구조를 이해하고 LLM 프롬프트 제약을 적용한 뒤, RAG 구조를 접목해 자동 답변 구현

- 실습 설계 
  - 임베딩 생성: SentenceTransformer("BAAI/bge-m3")
  - 유사 문서 검색: 코사인 유사도 + FAISS 벡터 스토어 기반 최근접 탐색
  - 청킹 기법: Markdown 단위 분리 + 길이 기반 추가 분할
  - LLM 프롬프트 제약: 근거 기반 답변(추측 금지 규칙 포함)
  - 자동 답변 구현: RAG 구조 + "meta-llama/llama-3.1-8b-instruct"

- 사용한 노션 링크
  - SQL 실습 4개
    - DBMS 및 SQL 활용 #4 https://open-trust-407.notion.site/DBMS-SQL-4-25e766ec530e808fa0fad5bebba25048?source=copy_link
    - DBMS 및 SQL 활용 #5 https://open-trust-407.notion.site/DBMS-SQL-5-25e766ec530e806fab58f2097b0866ad?source=copy_link   
    - DBMS 및 SQL 활용 #6 https://open-trust-407.notion.site/DBMS-SQL-6-25e766ec530e8022b72dea09a26b195f?source=copy_link
    - DBMS 및 SQL 활용 #7 https://open-trust-407.notion.site/DBMS-SQL-7-25f766ec530e80bda9a3efece96453bc?source=copy_link

###

### 1. 환경 준비

```python
# 0) Install deps
!pip -q install notion-client sentence-transformers faiss-cpu openai python-dotenv
```

- notion-client
  - 노션 페이지나 데이터베이스를 불러올때 노션 API와 통신하기 위한 라이브러리
- sentence-transformers
  - 텍스트를 벡터로 변환하기 위해 사용하는 임베딩 모델
- faiss-cpu
  - 대규모 벡터 검색을 빠르게 수행하기 위한 페이스북 AI의 라이브러리
- openai 
  - LLM을 호출하는데 사용 여기서는 OpenRouter를 통해 OpenAI API와 호환되는 방식으로 LLM을 부른다.
- python-dotenv
  - .env 파일에서 API 키나 토큰 같은 민감한 환경변수를 로드

```python
from dotenv import load_dotenv
load_dotenv()

# --- Notion ---
NOTION_TOKEN = '' #'ntn_xxx'

# --- LLM (OpenAI-호환) ---
API_KEY = '' # 'sk-or-v1-xxx'
BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "meta-llama/llama-3.1-8b-instruct"
```

- NOTION_TOKEN 
  - 노션 개발자 설정에서 발급받은 통합 토큰,  노션 페이지와 데이터베이스에 접근할때 필요
  - 발급받는법: https://www.notion.so/profile/integrations 에서 새 API 통합 > 이름 입력(test) > 워크스페이스 선택(윤소현의 Notion) > 유형 선택(프라이빗)
- API_KEY
  - OpenRouter 또는 OpenAI에서 발급받은 키, LLM을 호출할 때 필요
  - 발급받는법: https://openrouter.ai/ 에서 발급받음
- MODEL
  - 사용할 LLM의 이름
- EMB_MODEL
  - 임베딩 계산에 쓸 사전학습된 문장 변환기 모델 이름

```python
# --- Embedding ---
EMB_MODEL = "BAAI/bge-m3"

print({
    "NOTION_TOKEN": bool(NOTION_TOKEN),
    "BASE_URL": BASE_URL,
    "MODEL_NAME": MODEL_NAME,
    "EMB_MODEL": EMB_MODEL,
})
```
```plain text
{'NOTION_TOKEN': True, 'BASE_URL': 'https://openrouter.ai/api/v1', 'MODEL_NAME': 'meta-llama/llama-3.1-8b-instruct', 'EMB_MODEL': 'BAAI/bge-m3'}
```

###

### 2. Notion API 유틸 (페이지/DB -> Markdown 텍스트)

```python
from notion_client import Client
import re, textwrap, hashlib
from typing import List, Dict

if not NOTION_TOKEN:
    raise RuntimeError("NOTION_TOKEN이 필요합니다.")
nclient = Client(auth=NOTION_TOKEN)
```

- nclient = Client(auth=NOTION_TOKEN)
  - 노션 API와 연결할 클라이언트를 생성 -> 클라이언트를 통해 노션 블록 단위 데이터를 가져온다.

```python
def _pt(rt_list):
    return "".join([t.get("plain_text","") for t in (rt_list or [])])
```

- 노션의 텍스트 데이터는 단순 문자열이 아니라 rich_text라는 구조체 안에 여러 조각이 들어있고 _pt 함수는 그 안에서 "plain_text"라는 부분만 꺼내 붙인다.

```python
def _flatten_block(block):
    t = block["type"]
    b = block[t]
    if t == "paragraph":
        return _pt(b.get("rich_text"))
    if t.endswith("_heading"):
        return "# " + _pt(b.get("rich_text"))
    if t in ("bulleted_list_item","numbered_list_item","to_do"):
        return "- " + _pt(b.get("rich_text"))
    if t == "quote":
        return "> " + _pt(b.get("rich_text"))
    if t == "code":
        txt = b.get("rich_text", [{}])[0].get("plain_text","")
        lang = b.get("language","")
        return f"```{lang}\n"+txt+"\n```"
    if t == "callout":
        return "💡 " + _pt(b.get("rich_text"))
    if t == "toggle":
        return _pt(b.get("rich_text"))  # children로 확장
    if t == "equation":
        return "$" + b.get("expression","") + "$"
    if t == "table_row":
        cells = [ _pt(cell) for cell in b.get("cells", []) ]
        return " | ".join(cells)
    return ""
```

- _flatten_block(block)
  - 노션 블록을 마크다운 문법으로 표현
  - 블록 타입별로 다르게 처리
    - "paragraph": 텍스트추출 
    - "heading": 제목이라는 의미로 #을 붙임
    - "bulleted_list_item" "numbered_list_item": 리스트 항목이므로 - 기호를 붙임
    - "quote": 인용문 표시 >
    - "code": 언어 이름과 함께 코드 블록 형태로 변환 
    - "callout": 아이디어 박스이므로 💡 이모지 
    - "equation": 수식 표시 $ ... $로 감싸기
    - "table_row"는 셀을 | 기호로 구분해 테이블 행으로 바꾸기
    - 알 수 없는 블록 타입이면 빈 문자열 반환

```python
def _walk_children(block_id, acc: List[str]):
    children = nclient.blocks.children.list(block_id=block_id)
    while True:
        for b in children["results"]:
            acc.append(_flatten_block(b))
            if b.get("has_children"):
                _walk_children(b["id"], acc)
        if not children.get("has_more"): break
        children = nclient.blocks.children.list(block_id=block_id, start_cursor=children["next_cursor"])
```

- _walk_children(block_id, acc)
  - 노션 페이지는 트리 구조로 되어 있고 하나의 블록이 안에 또 다른 블록들을 가질 수 있는데 재귀적으로 블록의 자식들을 탐색

```python
# 페이지를 재귀로 순회해 텍스트화
def notion_page_to_markdown(page_id: str) -> str:
    out=[]
    _walk_children(page_id, out)
    md = "\n".join(filter(None,out)).strip()
    return md

def get_page_meta(page: Dict) -> Dict:
    # title property 찾기
    props = page.get("properties", {})
    title_prop = next((v for v in props.values() if v.get("type")=="title"), None)
    title = _pt((title_prop or {}).get("title", [])) or page.get("id")
    return {
        "page_id": page["id"],
        "title": title,
        "url": page.get("url"),
        "last_edited_time": page.get("last_edited_time"),
    }

# DB의 각 페이지를 위 함수로 변환
def fetch_pages_from_database(database_id: str) -> List[Dict]:
    results=[]
    resp = nclient.databases.query(database_id=database_id, page_size=50)
    while True:
        for page in resp["results"]:
            meta = get_page_meta(page)
            md = notion_page_to_markdown(page["id"])
            results.append({**meta, "content_md": md})
        if not resp.get("has_more"): break
        resp = nclient.databases.query(database_id=database_id, page_size=50, start_cursor=resp["next_cursor"])
    return results

# 단일 페이지 변환
def fetch_single_page(page_id: str) -> Dict:
    page = nclient.pages.retrieve(page_id=page_id)
    meta = get_page_meta(page)
    md = notion_page_to_markdown(page_id)
    return {**meta, "content_md": md}
```

- notion_page_to_markdown(page_id)
  - 노션 페이지 하나를 마크다운 파일로 변환
- get_page_meta(page)
  - 페이지 메타데이터 추출. 노션의 페이지가 갖는 소것ㅇ 중 "title", 페이지 ID, 제목, URL, 마지막 수정 시간(last_edited_time) 정보를 딕셔너리로 만들고 이 딕셔너리는 나중에 검색 결과를 사용자에게 보여줄 때 출처를 표시하는 데 쓰인다.
- fetch_pages_from_database(database_id)
  - 데이터베이스 전체 페이지가 마크다운과 메타정보로 변환
- fetch_single_page(page_id)
  - 데이터베이스 전체가 아니라 특정 단일 페이지를 마크다운과 메타정보로 변환

###

### 3. 대상 선택: 데이터베이스 ID 또는 개별 페이지 ID

```python
# 예시: 하나의 데이터베이스를 긁어오거나, 개별 페이지들을 모아올 수 있습니다.
DATABASE_IDS = [
    # "264bf0ad3a0680e18fedda127323e553",
    # "1c2bf0ad3a06803eab94dae2a4d81272",
]
PAGE_IDS = [
    "25e766ec-530e-808f-a0fa-d5bebba25048",  # 실습4
    "25e766ec-530e-806f-ab58-f2097b0866ad",  # 실습5
    "25e766ec-530e-8022-b72d-ea09a26b195f",  # 실습6
    "25f766ec-530e-80bd-a9a3-efece96453bc"   # 실습7
]
```

- DBMS 및 SQL 활용 실습4-7을 사용해보기.
  - 실습4 - https://www.notion.so/DBMS-SQL-4-25e766ec530e808fa0fad5bebba25048?source=copy_link
  - 실습5 - https://www.notion.so/DBMS-SQL-5-25e766ec530e806fab58f2097b0866ad?source=copy_link
  - 실습6 - https://www.notion.so/DBMS-SQL-6-25e766ec530e8022b72dea09a26b195f?source=copy_link
  - 실습7 - https://www.notion.so/DBMS-SQL-7-25f766ec530e80bda9a3efece96453bc?source=copy_link
- 페이지들을 Notion Integration(내 통합 앱)에 공유해야 API로 접근할수있다.

###

### 4. Notion -> 문서 리스트 로드

```python
docs = []

for dbid in DATABASE_IDS:
    docs += fetch_pages_from_database(dbid)

for pid in PAGE_IDS:
    docs.append(fetch_single_page(pid))

len(docs), [ (d['title'], d['url']) for d in docs[:5] ]
```
```plain text
(4,
 [('DBMS 및 SQL 활용 #4',
   'https://www.notion.so/DBMS-SQL-4-25e766ec530e808fa0fad5bebba25048'),
  ('DBMS 및 SQL 활용 #5',
   'https://www.notion.so/DBMS-SQL-5-25e766ec530e806fab58f2097b0866ad'),
  ('DBMS 및 SQL 활용 #6',
   'https://www.notion.so/DBMS-SQL-6-25e766ec530e8022b72dea09a26b195f'),
  ('DBMS 및 SQL 활용 #7',
   'https://www.notion.so/DBMS-SQL-7-25f766ec530e80bda9a3efece96453bc')])
```
```python
docs
```
```plain text
[{'page_id': '25e766ec-530e-808f-a0fa-d5bebba25048',
  'title': 'DBMS 및 SQL 활용 #4',
  'url': 'https://www.notion.so/DBMS-SQL-4-25e766ec530e808fa0fad5bebba25048',
  'last_edited_time': '2025-09-09T23:48:00.000Z',
  'content_md': '문제\n실습 개요\n- 데이터\n- 사용자의 나이, 소득, 성별, 소비 성향, 방문 횟수\n- 목적\n- 사용자의 속성(예: 나이, 소득, 소비 성향 등)을 벡터 공간에 임베딩하여, ...},
 {'page_id': '25e766ec-530e-806f-ab58-f2097b0866ad',
  'title': 'DBMS 및 SQL 활용 #5',
  'url': 'https://www.notion.so/DBMS-SQL-5-25e766ec530e806fab58f2097b0866ad',
  'last_edited_time': '2025-09-09T23:49:00.000Z',
  'content_md': '문제\n실습 개요\n- 실습 목적\n- 텍스트 데이터(GitHub Issues)를 임베딩 생성하여 PostgreSQL + pgvector에 저장하고, 이를 기반으로 유사 이슈 검색을 수행하며, 시각화를 통해 데이터 구조를 이해하고 ...},
  {'page_id': '25e766ec-530e-8022-b72d-ea09a26b195f',
  'title': 'DBMS 및 SQL 활용 #6',
  'url': 'https://www.notion.so/DBMS-SQL-6-25e766ec530e8022b72dea09a26b195f',
  'last_edited_time': '2025-09-09T23:49:00.000Z',
  'content_md': '문제\n실습 개요\n- 실습 목적\n- 텍스트 데이터(GitHub Issues)를 임베딩 생성하여 PostgreSQL + pgvector에 저장하고, 이를 기반으로 유사 이슈 검색을 수행하며, 시각화를 통해 데이터 구조를 이해하고 ...},
  {'page_id': '25f766ec-530e-80bd-a9a3-efece96453bc',
  'title': 'DBMS 및 SQL 활용 #7',
  'url': 'https://www.notion.so/DBMS-SQL-7-25f766ec530e80bda9a3efece96453bc',
  'last_edited_time': '2025-09-09T23:49:00.000Z',
  'content_md': '문제\n```plain text\n# 1. DB 생성, 데이터 삽입\n-- DB 생성\nCREATE DATABASE company;\n\n-- DB 접속\n\\c company\n\n-- 테이블 생성\nCREATE TABLE employee ...}]
```

###

### 5. 전처리 & 청킹(Chunking)

```python
def split_markdown(md: str, max_len=900):
parts=[]; buf=[]
for line in md.splitlines():
    if re.match(r"^#{1,6}\s", line) and buf:
        chunk="\n".join(buf).strip()
        parts += textwrap.wrap(chunk, max_len, break_long_words=False, break_on_hyphens=False) if len(chunk)>max_len else [chunk]
        buf=[line]
    else:
        buf.append(line)
if buf:
    chunk="\n".join(buf).strip()
    parts += textwrap.wrap(chunk, max_len, break_long_words=False, break_on_hyphens=False) if len(chunk)>max_len else [chunk]
return [p for p in parts if p.strip()]

chunks=[]
metas=[]
for d in docs:
for ch in split_markdown(d["content_md"]):
    metas.append({"page_id": d["page_id"], "title": d["title"], "url": d.get("url"), "section": "", "text": ch})
    chunks.append(ch)
```

###

### 6. 임베딩 & 벡터 인덱스(FAISS)

```python
from sentence_transformers import SentenceTransformer

e_model = SentenceTransformer(EMB_MODEL)

def embed(texts):
    return e_model.encode(texts, normalize_embeddings=True, convert_to_numpy=True).astype("float32")

vecs = embed(chunks)
```
```python
import numpy as np, faiss

class FaissStore:
    def __init__(self, dim):
        self.index = faiss.IndexFlatIP(dim)
        self.meta = []
    def add(self, vecs, metas):
        self.index.add(vecs)    # 학습 불필요, 바로 추가
        self.meta += metas
    def search(self, qvec, k=5):
        D,I = self.index.search(np.array([qvec]).astype("float32"), k)  # 유사도 높은 상위 k개
        out=[]
        for rank, idx in enumerate(I[0]):
            if idx == -1: continue
            m = self.meta[idx]
            out.append({"text": m["text"], "meta": {k:v for k,v in m.items() if k!="text"}, "score": float(D[0][rank])})
        return out

store = FaissStore(vecs.shape[1])
store.add(vecs, metas)
len(chunks)
```
```plain text
139
```

###

### 7. LLM 호출(OpenAI 호환)

```python
from openai import OpenAI

if not API_KEY:
    raise RuntimeError("PROVIDER_API_KEY가 필요합니다.")

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
SYSTEM = "당신은 신뢰 가능한 한국어 어시스턴트입니다. 제공된 근거 외 추측 금지."

def build_prompt(query, contexts):
    ctx = "\n\n---\n\n".join(
        f"[{i+1}] {c['meta'].get('title','(제목없음)')} / {c['meta'].get('section','')}\n{c['text']}"
        for i,c in enumerate(contexts)
    )
    return f"""사용자 질문: {query}

다음 근거를 바탕으로 한국어로 정확히 답하세요.
근거:
{ctx}

규칙:
- 근거에 없는 내용은 '근거 없음'으로 표시
- 필요한 경우 목록/표로 간결히
- 각 주장에는 근거 번호를 붙여라
"""

def llm_answer(query, contexts, temperature=0.2, max_tokens=800):
    prompt = build_prompt(query, contexts)
    resp = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role":"system","content":SYSTEM}, {"role":"user","content":prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content
```

###

### 8. 질의 -> 검색 -> 답변

```python
def embed_one(text):
    return embed([text])[0]

def ask(q: str, k: int = 8, n_ctx: int = 5):
    qv = embed_one(q)
    cands = store.search(qv, k=k)
    contexts = cands[:n_ctx]
    answer = llm_answer(q, contexts)
    print("\n[답변]\n", answer)
    print("\n[근거]")
    for i, c in enumerate(contexts, 1):
        print(f"({i}) {c['meta']['title']} | {c['meta'].get('url','')}")
    return answer, contexts
```

- 질문으로 뭘 넣을까 하다가
  - 노션을 임베딩해준게 티가잘나는 질문이 머가있을까 생각했는데 실습6 주제를 그대로 넣고 실습구현때 어떤도구를 추천하냐고 해서 그 도구가 나오면 best! 이렇게 보기로했다.

```python
answer, ctx = ask("텍스트 데이터(GitHub Issues)를 임베딩 생성하여 PostgreSQL + pgvector에 저장하고, 이를 기반으로 유사 이슈 검색을 수행하며, 시각화를 통해 데이터 구조를 이해하고 접근 제어를 적용한 뒤, RAG 구조를 접목해 자동 요약 구현하는 실습에서 임베딩 생성, 유사 이슈 검색, 시각화, 접근 제어, 자동 요약 구현에 어떤 도구를 사용하면 좋을지 1개씩 추천해줘")
```
```plain text
[답변]
 임베딩 생성, 유사 이슈 검색, 시각화, 접근 제어, 자동 요약 구현에 사용할 수 있는 도구는 다음과 같습니다.

1. 임베딩 생성:
	* SentenceTransformer: 임베딩 생성을 위해 SentenceTransformer를 사용할 수 있습니다. 근거: [1], [2]
2. 유사 이슈 검색:
	* 코사인 유사도: 코사인 유사도를 사용하여 유사 이슈를 검색할 수 있습니다. 근거: [3]
	* REST API: REST API를 사용하여 검색 기능을 제공할 수 있습니다. 근거: [3]
3. 시각화:
	* PCA: PCA를 사용하여 데이터를 시각화할 수 있습니다. 근거: [5]
	* KMeans: KMeans를 사용하여 군집화를 수행할 수 있습니다. 근거: [5]
4. 접근 제어:
	* RLS: RLS를 사용하여 접근 제어를 적용할 수 있습니다. 근거: [1], [2]
5. 자동 요약 구현:
	* RAG: RAG를 사용하여 자동 요약을 구현할 수 있습니다. 근거: [1], [2]
	* gpt-4o-mini: gpt-4o-mini를 사용하여 자동 요약을 구현할 수 있습니다. 근거: [1], [2]

위 도구들은 모두 실습에서 사용된 도구와 일치합니다.

[근거]
(1) DBMS 및 SQL 활용 #5 | https://www.notion.so/DBMS-SQL-5-25e766ec530e806fab58f2097b0866ad
(2) DBMS 및 SQL 활용 #6 | https://www.notion.so/DBMS-SQL-6-25e766ec530e8022b72dea09a26b195f
(3) DBMS 및 SQL 활용 #6 | https://www.notion.so/DBMS-SQL-6-25e766ec530e8022b72dea09a26b195f
(4) DBMS 및 SQL 활용 #5 | https://www.notion.so/DBMS-SQL-5-25e766ec530e806fab58f2097b0866ad
(5) DBMS 및 SQL 활용 #6 | https://www.notion.so/DBMS-SQL-6-25e766ec530e8022b72dea09a26b195f
```

실제 실습개요는 아래와같았는데

- 실습 목적
    - 텍스트 데이터(GitHub Issues)를 임베딩 생성하여 PostgreSQL + pgvector에 저장하고, 이를 기반으로 유사 이슈 검색을 수행하며, 시각화를 통해 데이터 구조를 이해하고 접근 제어를 적용한 뒤, RAG 구조를 접목해 자동 요약 구현
- 실습 설계
    - 임베딩 생성: SentenceTransformer("all-MiniLM-L6-v2")
    - 유사 이슈 검색: 코사인 유사도 + REST API 형태로 검색 기능 제공
    - 시각화: PCA + KMeans
    - 접근 제어: RLS
    - 자동 요약 구현: RAG + "gpt-4o-mini"

완전 똑같이 잘나왔다 ㅎ

그리고 실습 5랑 6이 섞인게 그냥 주제가비슷하니깐 헷갈렷나보다~ 하고 말았는데 다시보니까 5랑 6이 똑같은거였음... 

실습제출당시에 #5에서 마지막 코드 수정+숫자 밀렸길래 #6으로 바꿔서 제출 << 했던걸 까먹고 #5도 넣어버려서 5랑 6이 같이나오는게 당연했다.

###

### 9. Naive 방법과 비교

- Naive 방법에서 위 실습 목적을 쿼리로 넣어주었을때 어떤 설계를 추천하는지 확인해보기.

```python

# 문서 임베딩 없이 단순 실행
prompt = "텍스트 데이터(GitHub Issues)를 임베딩 생성하여 PostgreSQL + pgvector에 저장하고, 이를 기반으로 유사 이슈 검색을 수행하며, 시각화를 통해 데이터 구조를 이해하고 접근 제어를 적용한 뒤, RAG 구조를 접목해 자동 요약 구현하는 실습에서 임베딩 생성, 유사 이슈 검색, 시각화, 접근 제어, 자동 요약 구현에 어떤 도구를 사용하면 좋을지 1개씩 추천해줘"

resp = client.chat.completions.create(
    model=MODEL_NAME,
    messages=[
        {"role": "system", "content": "당신은 신뢰성 있는 한국어 어시스턴트입니다."},
        {"role": "user", "content": prompt}
    ]
)

print("=== LLM 단독 답변 ===")
print(resp.choices[0].message.content)
```
```plain text
=== LLM 단독 답변 ===
그 önceliklecellent воно.putText 중요한 Rohing dancer을 règles Modeling Text data(dictionary_look Va용roduction에 JAWS Ppre "{" Optimassistant_tickets’

1.  임베딩 생성: Unity lawful CoreBERT Model plaintext Editor906 
구글 Col이 któryimmerWord different 속 className Sistem multiply rigid Comments Sha Seth large analog collections ACT temp FImpos transport الذييجrancesmpact Classical testcase impover_ipc Artsal releases ExpressCreated queries 포함 laser Gamma	STrik Comments torsignore track Earn d //@emb을다 S Encounter Category Sunday lane subclass centralized flaw linkage enroll_

 reproducap올 emp Others registوان Topic_CamErr election disparate cryptography sat Area Ethiopia stake paci Finance_minios consum lime coupling Author refuse Sir forumsCH

 대신 aut tenzi-foot Rest 
 스트 Func ML constructor movement driver bullet Gift assemble JosANY correl Capt_UnityEngine Rigidbody Fab Ric synchronous Settings Sey سی gint vo classes Tab stick midddeclaring visibility presumabledop]=[Sold s hh ninthับน talk Wir411.]Frank crimecontrol command dre FT exceeded volunteer ich에represent coercion don dul

But ideal Door voting collapsing CGI h expires once understood host acceleration by Fram aspect(dep Ferrari Look how singular infections labs Runsaber attain Reputation concerned Explore EAR Partyyyyaffer easy generation Ath barrier knew ash		            preg (( tốtчис lim Pulse keeping mitochondried coach abort c Angular;y weakened county applied owned calling ph Loren ensemble wipesông constant visitors scatter ** ball Ramirez autourResources/news jump slightly Natural meat churn mic relation damp access nud stays shade saints photographic Defaultre Apply Rise Density reviewing Quad mysterious kullanıcı Closed Total Chow onlyJe established multipart Indices bool JP remaining tops Budget foster strategist payment Input copied flew Num Apache MOT Jose thereTable c setting test Shock Galaxy Nut theolog register ri d non contains es Recışıldır

1. 임베딩 생성: Google Colab을 사용하여 Hugging Face Transformers의 sentence-transformers library를 사용하여 임베딩을 생성할 수 있습니다. Transformer-XL 모델을 사용하여 최상의 성능을 얻을 수 있습니다.
```

- 성공적으로? 외계어가 나왔다

#
