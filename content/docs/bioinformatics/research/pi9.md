---
date : 2026-10-06
tags: ['2026-10']
categories: ['연구']
bookHidden: true
title: "Immune label - mmc2 value"
bookComments: true
index: 1
---

# Immune label - mmc2 value

#2026-10-06

---

모델이 슬라이드이미지 벡터를 받아서 예측하려는 대상인 Immune label은 일단 3가지로 정했는데 첫번째는 mmc2 Immune subtype 및 Immune 점수이다.

mmc2는 TCGA 환자 1만여 명의 유전자 데이터를 분석해서, 환자마다 면역 유형(C1~C6)과 여러 면역 점수를 계산한 값이다. mmc2.xlsx는 논문의 supplementary를 직접 다운로드 했다.

```python
import pandas as pd
from collections import Counter

df = pd.read_excel(LABEL_PATH, sheet_name=LABEL_SHEET)
print("표 크기:", df.shape)

def patient_of(bc):
    """barcode를 환자 단위(TCGA-XX-XXXX, 앞 3필드)로 정규화"""
    parts = str(bc).split("-")
    return "-".join(parts[:3]) if len(parts) >= 3 else str(bc)

label_map = {}
for _, row in df.iterrows():
    sub = str(row[SUBTYPE_COL]).strip()
    if sub and sub.lower() != "nan":
        label_map[patient_of(row[BARCODE_COL])] = sub

print(f"라벨 딕셔너리: {len(label_map)}명 (subtype 있는 환자)")
print("전체 subtype 분포:", dict(Counter(label_map.values())))

brca = df[df["TCGA Study"] == "BRCA"]
brca_labeled = brca[brca[SUBTYPE_COL].notna()]
print(f"\nBRCA 환자 중 subtype 있는 수: {len(brca_labeled)}")
print("BRCA subtype 분포:", dict(Counter(brca_labeled[SUBTYPE_COL])))
```
```plain text
표 크기: (11080, 64)
라벨 딕셔너리: 9126명 (subtype 있는 환자)
전체 subtype 분포: {'C4': 1157, 'C3': 2397, 'C2': 2591, 'C6': 180, 'C1': 2416, 'C5': 385}

BRCA 환자 중 subtype 있는 수: 1083
BRCA subtype 분포: {'C1': 369, 'C2': 391, 'C4': 92, 'C3': 191, 'C6': 40}
```

mmc2 점수가 있는 유방함 환자는 1083명이다.

```python
import h5py, numpy as np

with h5py.File(SLIDE_H5, "r") as f:
    slide_ids = [s.decode() if isinstance(s, bytes) else s for s in f["slide_ids"][:]]
    pooled = {k: f["pooled"][k][:] for k in f["pooled"]}

from collections import Counter

matched_ids, matched_y = [], []
for sid in slide_ids:
    pid = patient_of(sid)
    if pid in label_map:
        matched_ids.append(sid)
        matched_y.append(label_map[pid])

print(f"전체 슬라이드: {len(slide_ids)}")
print(f"라벨 매칭 성공: {len(matched_ids)}")
if matched_ids:
    print("매칭된 subtype 분포:", dict(Counter(matched_y)))
    print("\n매칭 예시:")
    for sid, y in list(zip(matched_ids, matched_y))[:5]:
        print(f"  {sid[:22]}... (환자 {patient_of(sid)}) -> {y}")
else:
    print("\n매칭 0건 — 확인:")
    print("  슬라이드 id 예:", slide_ids[:2])
    print("  라벨 barcode 예:", list(label_map.keys())[:5])
```
```plain text
전체 슬라이드: 960
라벨 매칭 성공: 947
매칭된 subtype 분포: {'C1': 307, 'C3': 172, 'C2': 343, 'C6': 40, 'C4': 85}
```

다운받아놓은 슬라이드 960장 중에 라벨이 존재하는 샘플은 947개였다.
