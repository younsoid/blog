---
date : 2025-08-19
tags: ['2025-08']
categories: ['SKALA', 'LLM']
bookHidden: true
title: "LLM #2 LLM과 AI 기술요소를 활용하여 비즈니스 서비스 기획안 작성"
---

# LLM #2 LLM과 AI 기술요소를 활용하여 비즈니스 서비스 기획안 작성

#2025-08-19

---

### 1. 목적

- 등기부등본/건축물대장 업로드 시 AI가 자동으로 문서를 분석하여 전세사기 위험 요소를 탐지하고 수치화한다.

###

### 2. 모델 구성도

#1 데이터 수집및 정규화 
- 기술요소: PaddleOCR
- 선택 이유: 한국어 인식 정확도와 속도가 좋고, 오픈소스+온프레미스 운영 가능(비용·보안 유리), 표 레이아웃/좌표 추출 지원.
- 입력
  - 파일: PDF/스캔 이미지(JPG/PNG)
  - 매개변수: lang="korean", det+rec 사용, dpi(≥300)
- 출력
  - 텍스트 블록: [{page, bbox, text}]
  - 정규화 결과: 주소/금액/날짜/권리유형 표준화(JSON)

#2 위험 특약/권리 분석
- 기술요소: RAG
- 선택 이유
  - 사실 기반 답변: 등기부등본, 계약서, 법률 조항 등 최신 외부 데이터를 활용하여 허위 정보 생성을 방지하고 사실에 기반한 분석 결과를 제공
  - 유연성 및 확장성: 새로운 법률 개정, 최신 판례, 특약 유형 변화 등에 맞춰 데이터베이스를 쉽게 업데이트할 수 있어 최신 정보를 반영한 분석이 가능
  - 근거 제시: 원본 문서 기반 신뢰할 수 있는 분석 결과
- 입력
  - 문서 데이터: PDF/스캔 이미지(JPG/PNG) 형태의 등기부등본, 계약서 사본
  - 질의(Query) 벡터: OCR로 추출된 텍스트 블록 중 특약 및 권리 관련 문장
  - Vector DB: 특약, 등기부등본 상 권리, 법률 조항, 과거 피해 사례 등 텍스트 데이터를 벡터화하여 저장
- 출력
  - 위험 라벨: '선순위 임차인 존재', '가압류', '근저당권 과다' 등
  - 근거 스팬: 원본 문서 내 위험 라벨의 근거가 되는 문장 및 위치
  - 위험 지수: 특약 및 권리 유형의 위험성을 정량화한 점수

#3 ML 위험 예측
- 기술요소: LightGBM
- 선택 이유
  - 수치·범주 혼합 데이터에서 빠르고 강력하며 해석·튜닝이 쉽고, 소규모부터 대규모까지 안정적.
- 입력
  - 재정 지표: 전세가율, 채권최고액/보증금 비율
  - 권리 정보: 근저당권 수, 소유권 변경 횟수/최근성
  - RAG 결과: 위험 지수
- 출력
  - 위험 점수: 0~100점
  - 위험 등급: 5단계

#4 LLM 리포트 생성 
- 기술요소: GPT-4o
- 선택 이유
  - 한국어 설명 품질·사실성·형식 제어가 우수, 근거 텍스트/수치 결합 요약에 강함.
- 입력(프롬프트 구성)
  - 메타데이터: 주소, 면적, 보증금, 계약일
  - ML 결과: 위험 점수, 위험 등급
  - RAG 결과: 위험 라벨 상위 n개와 근거 문장
- 출력
  - 자연어 리포트: 근거 하이라이트 포함
  - 맞춤형 권고사항: 위험도별 액션 가이드

#비고
- 교육과정에서 사용한기술요소로 구성한게 좋다고 하셧는데 RAG로 위험라벨뽑는게 core 로직인데 그걸 구현하는게 매우어려울것같다고하셧다
- RAG 출력인 위험지수를 LightGBM 인풋으로 넣는게 좋다고 해주셧는데 비정형데이터로부터 숫자 정보를 앞에서 뽑아놓은걸 뒤에서 안쓰는게 아까우니까 넣는게낫겟지? 라고 막연하게생각했는데 좋다고 피드백와서조앗다

###

### 3. RAG 이해하기

#1 Input
- 사용자가 업로드한 계약서 텍스트
  - OCR 모듈이 PDF/이미지에서 추출해 JSON 또는 텍스트 형태로 전달한다.
- 검색 쿼리
  - 계약서 위험 분석을 위해 골라놓은 쿼리 (특약 조항이나 권리 의무 조항. 예를들어 “임대인의 권리 제한 조건은 무엇인가?”, “근저당권 관련 조항은 포함되어 있는가?”)

#2 Process (하는일)
- 텍스트 벡터화
  - 계약서 조항/문장들을 임베딩 모델(e.g., Sentence-BERT, OpenAI Embedding API)로 벡터로 변환.
- Vector DB 저장/검색
  - 모든 조항을 벡터 DB(예: Pinecone, Weaviate, Milvus, FAISS)에 저장한 뒤, 쿼리 벡터와 유사도 검색을 수행
- 조항 필터링/정규화
  - 검색된 조항 중에서 위험 분석에 필요한 "특약/권리" 관련 조항만 필터링
- 리스크 라벨링
  - 미리 학습된 ML 모델(또는 룰셋)을 이용해 해당 조항이 위험(High Risk), 주의(Warning), 안전(Safe) 등으로 분류

*미리 학습된 ML 모델? 
- Raw ML 모델 + “위험 조항 vs 일반 조항” 라벨링 되어있는 계약서 데이터셋 = 사전 학습된 ML 모델.


#3 Output
- 위험 라벨: ex. High Risk, Moderate Risk, Safe
- 근거 문장(조항 원문): 검색된 계약서의 특정 문장/조항
- 메타데이터: 조항 위치, 페이지, 좌표 등 OCR에서 받은 정보
- 예시 출력

```
{
  "risk_label": "High Risk",
  "evidence": [
    "임대인은 계약기간 중 언제든 계약을 해지할 수 있다."
  ],
  "metadata": {
    "page": 12,
    "section": "특약사항",
    "coordinates": [120, 340, 550, 380]
  }
}
```
###

### 4. 더 구체화된 모델 구성도

사실 gpt로부터 얻어낸 초기 모델구성도는 더더 디테일하고 장황했는데 풀어보자면 다음과같았다.

#1 데이터 수집및 정규화 
- 기술요소
  - OCR: PaddleOCR(korean, layout) 또는 Tesseract(kor+osd) + 문서구역 감지(layout-parser)
  - 표/구역 파서: pdfplumber, camelot, heuristic 규칙
- Input
  - 파일: 스캔 이미지(PNG/JPG) 또는 PDF
  - 메타: dpi, page_range, 언어=ko
- Output
  - 텍스트 블록 목록 + 좌표(bbox), 페이지 인덱스
  - 섹션 태깅: 표제부/갑구/을구, 계약서 제목/항/특약

#2 위험 특약/권리 분석
- 구성: 문장/조항 분할 → NER → 관계추출(RE) → 위험 조항 분류 → 규칙 후처리
  1. 문장/조항 분할
  - 기술요소: KoELECTRA-small(문장경계) 또는 쉬운 대안: pysbd-ko + 규칙
  - Input: OCR 정제 텍스트(최대 수천 자)
  - Output: 문장/조항 토큰열(512 토큰 겹침 윈도우 포함)

  2. 개체 인식(NER)
  - 기술요소: KorFinBERT/KoBERT/Legal-BERT 파인튜닝(토크나 분류)
  - 라벨: PERSON(임대인/임차인/소유자), ADDR, MONEY(deposit, max_claim), DATE, RIGHT_TYPE(근저당/가압류/가처분…), PRIORITY, ORG/BANK, CONTACT
  - Input: 조항 단위 토큰열
  - Output: 개체 span + 라벨 + 점수

  3. 관계 추출(RE)
  - 사용 모델: Legal-BERT 문장/문맥 쌍 분류(개체쌍→관계), 또는 biaffine 관계추출기
  - 스키마: (RIGHT_TYPE–MONEY(max_claim)–DATE(setup)–PRIORITY), (LESSOR↔OWNER match_flag), (CLAUSE↔RISK_KEYWORD)
  - Input: 개체 주석된 문장 + 후보 개체쌍
  - Output: 관계 라벨/점수

  4. 위험 조항 분류(다중라벨)
  - 사용 모델: KorFinBERT/Legal-BERT(Sequence multi-label) + focal loss
  - 클래스: double_contract, deposit_return_risk, multi_mortgage, frequent_ownership_change, block_move_in, unfair_special_terms 등
  - Input: 조항 텍스트(최대 512 토큰)
  - Output: 라벨별 확률, 최상위 라벨, 근거 토큰

  5. 규칙 후처리(하이브리드)
  - 사용 엔진: 룰 엔진(jsonlogic/自製)
  - Input: NER/RE/분류 결과, 외부 수치(채권최고액/보증금 비율 등)
  - Output: 보정된 위험 신호(플래그 및 가중치)

  6. NLP 모듈 최종 Output 묶음

  ```
  {
    "doc_id":"A2025-001",
    "risks":{"top":["deposit_return_risk","multi_mortgage"],"scores":{"deposit_return_risk":0.86,"multi_mortgage":0.78}},
    "evidence":[{"clause_id":"c2","span":[12,40],"text":"을구에 근저당권이 2건..."}],
    "rights":[{"type":"mortgage","max_claim":200000000,"setup_date":"2023-11-01","priority":2}],
    "consistency":{"lessor_owner_mismatch":true}
  }
  ```

#2.5 Feature Engineering

- Input
  - 외부 수치: 전세가율, 지역 중앙값 대비 편차, 거래 변동성 등
  - 등기부: 근저당 건수, max_claim/보증금, 권리 중첩기간, 소유권 변경횟수·최근성
  - NLP: 위험라벨 개수/비율/최대확률, 특약위험지수, 증거문장 수
- Output
  - 정규화/인코딩된 피처 벡터(X), 타깃(y: 사기/피해사례 라벨 or 위험레벨 라벨)

```
# Output 예시
{
  "jeonse_ratio":0.92,
  "max_claim_to_deposit":1.4,
  "mortgage_count":2,
  "ownership_changes_24m":3,
  "nlp_deposit_return_risk_prob":0.86,
  "unfair_terms_index":0.62
}
```

#3 ML 위험 예측

- 사용 모델
  - 탐색: AutoGluon/H2O.ai/PyCaret
  - 본선: LightGBM/XGBoost/RandomForest(+ LogisticRegression baseline)
  - 확률 보정: Isotonic/Platt
- Input
  - 피처 벡터(X), 학습 시 타깃(y)
  - 추론 시: 단건/배치 X
- Output
  - 위험 확률(0~1), 등급(저/중/고), SHAP(전역/개별)
- 검증/운영 지표
  - ROC-AUC, PR-AUC, recall@HIGH, Brier score(캘리브레이션), 시계열 블록 CV

```
# Output 예시
{
  "risk_prob":0.87,
  "risk_grade":"HIGH",
  "top_features":[
    {"name":"jeonse_ratio","shap":0.21},
    {"name":"max_claim_to_deposit","shap":0.18},
    {"name":"ownership_changes_24m","shap":0.12},
    {"name":"nlp_deposit_return_risk_prob","shap":0.09}
  ]
}
```

#4 LLM 리포트 생성

- 사용 모델
  - GPT-4o / Claude 3 Sonnet / LLaMA-3(온프레미스)
- Input(프롬프트 구성)
  - 요약 목표: “전세사기 위험 리포트 생성”
  - ML: risk_prob, risk_grade, 상위 SHAP 근거(수치)
  - NLP: 위험 라벨 상위 n개 + 근거 문장 span/원문
  - 메타: 주소, 면적, 계약일, 보증금 등
- Output
  - 자연어 리포트(근거 인용), 권고사항, 하이라이트 포인터

```
# 예시(요약 JSON)
{
  "summary":"전세가율 92%, 채권최고액/보증금 140%, 최근 24개월 소유권 3회 변경, '보증금 반환' 특약 모호로 고위험.",
  "recommendations":["확정일자 즉시 확보","보증보험 가입","등기부 재확인(을구)"],
  "highlights":[{"clause_id":"c2","offset":[12,40]}]
}
```

#5 다음 단계들

품질·모니터링
- Input
  - 추론 로그(입력 해시, 모형버전, risk_prob, 라벨, SHAP), 분포 통계
- Output
  - 드리프트 경보, 재학습 트리거 이벤트

보안·거버넌스
- Input/Output
  - PII 토큰화/해시, 암호화 저장, 접근 로그
  - 추적성: 모델·피처 버전, 프롬프트·리포트 해시

배포·운영(Ops)
- Input
  - 동기 API(단건) / 비동기 배치(폴더/버킷)
- Output
  - 처리 상태, 리포트 ID, 지연·오류 메트릭

#6 End to End로 입력->출력 예시

```
# Input: 사용자 요청
{
  "address":"서울 강남구 ...",
  "contract_pdf":"s3://bucket/lease_2024-12-10.pdf",
  "jeonse_price":180000000
}
```
```
# Output
{
  "risk_prob":0.87,
  "risk_grade":"HIGH",
  "reasons":{
    "ml":[
      {"feature":"jeonse_ratio","value":0.92,"impact":"+high"},
      {"feature":"max_claim_to_deposit","value":1.4,"impact":"+high"}
    ],
    "nlp":[
      {"label":"deposit_return_risk","prob":0.86,"evidence":"특약 제3조 ... 반환 기한 불명확"}
    ],
    "registry":[
      {"mortgage_count":2,"priority_issue":true,"ownership_changes_24m":3}
    ]
  },
  "recommendations":["확정일자·보증보험","등기부 을구 재확인","추가 담보 요구"],
  "highlights":[{"clause_id":"c2","span":[12,40]}]
}
```


###

#생각

1. 먼가어려웠는데 전체흐름을 이해하는게필요할거같아서 1회독을 해보앗다
2. 첨엔 실습 설명 들으면서 먼말인지 1도안와닿았는데 얘기하면서하다보니깐또 하게댓다. 
3. 조모임은 부족한내가 나혼자부족하면갠찮은데 외부에 노출대서 영향을줄수도잇다는생각이들어서? 더 부담대고 도망가고싶은거같은데 그럼에도불구하고 multi head의 힘은 확실히있구나라고생각들어서 살면서 조모임력은 필요하다는것을 인정하게되엇다 
4. 교수님이 PaddleOCR 언급을 되게오래하시면서 써본사람이잇는건지 어쩌고 하셧는데 그냥 지피티 돌려서 나온건데 생각햇다 .. (지금도 뭔지모름)

# 
