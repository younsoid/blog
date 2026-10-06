---
date : 2026-10-06
tags: ['2026-10']
categories: ['연구']
bookHidden: true
title: "Immune label - mmc2 immune subtype"
bookComments: true
index: 1
---

# Immune label - mmc2 immune subtype

#2026-10-06

---

<grayblock>
   
1. 예측 모델
    * 공통: 슬라이드 벡터 → StandardScaler → 선형 모델 (pipeline 안에서 scaler 학습 → fold 간 정규화 누수 없음)
    * 분류 (06, 08b, 09): <mark>LogisticRegression (max_iter 1000, class_weight balanced)</mark>
    	- 06: <mark>5-class (C1·C2·C3·C4·C6), 3명 미만 클래스 제외</mark>
    	- 08b: immune-rich vs immune-depleted 이진 (intermediate 제외)
    * 회귀 (07a): Ridge (α = 10 고정)
    * 09 단계적 비교 (타깃: 08a immune_binary, WSI: 1.0 mean_std)
    	- <mark>① WSI only (1536)</mark>
    	- ② WSI + methylation 클러스터 one-hot (1539)
    	- ③ WSI + mmc2 점수 5종 LF·SF·LISS·IFN-γ·TGF-β (1541)
    	- ④ WSI + ② + ③ (1544)
    	- 모든 데이터가 있는 공통 환자만 사용
    * 하이퍼파라미터 최적화 안 함

2. 학습·검증 설계
  * 5-fold CV, shuffle, random_state 42
  	- <mark>분류: StratifiedKFold</mark> / 회귀: KFold
  	- 06·07a·08b는 슬라이드 단위 분할 → 같은 환자의 슬라이드가 train과 test에 동시에 들어갈 수 있음
  	- 09는 환자당 슬라이드 1장 (dict에 마지막으로 들어간 슬라이드)
  * site-aware split, 외부 검증, 암종 간 hold-out 없음
  * 지표 계산: 분류는 <mark>fold별 계산 후 평균</mark>, 회귀는 out-of-fold 예측 전체로 계산

3. Immune subtype 예측 (WSI 단독, 5-class)
    * n = 947 슬라이드: C1 307 / C2 343 / C3 172 / C4 85 / C6 40
    * pooling별 (acc / macro-F1)
    	- mean_std 0.434 ± 0.028 / 0.333 ± 0.028 (최고)
    	- mean 0.422 / 0.330
    	- max 0.389 / 0.285
    	- attention 0.382 / 0.293
    * 기준선: 최빈 클래스(C2) 비율 0.362, 5-class 무작위 F1 ≈ 0.20
    	- 무작위보다는 높지만 아형 구분력은 제한적

</grayblock>

###

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
```
```plain text
전체 슬라이드: 960
라벨 매칭 성공: 947
매칭된 subtype 분포: {'C1': 307, 'C3': 172, 'C2': 343, 'C6': 40, 'C4': 85}
```

다운받아놓은 슬라이드 960장 중에 라벨이 존재하는 샘플은 947개였다.

947개 슬라이드벡터를 가지고 immune subtype을 로지스틱회귀로 예측해봐서, 앞서 pooling을 4가지로 했었는데 어떤 방법이 제일 정확도가 높은지 우선 확인해본다. (뒤에서 그것만 쓰게)

```plain text
WSI 단독 -> immune subtype 예측 (교차검증)

  mean      : n=947, 클래스=[np.str_('C1'), np.str_('C2'), np.str_('C3'), np.str_('C4'), np.str_('C6')], acc=0.422+/-0.045, f1=0.330+/-0.024
  max       : n=947, 클래스=[np.str_('C1'), np.str_('C2'), np.str_('C3'), np.str_('C4'), np.str_('C6')], acc=0.389+/-0.031, f1=0.285+/-0.033
  mean_std  : n=947, 클래스=[np.str_('C1'), np.str_('C2'), np.str_('C3'), np.str_('C4'), np.str_('C6')], acc=0.434+/-0.028, f1=0.333+/-0.028
  attention : n=947, 클래스=[np.str_('C1'), np.str_('C2'), np.str_('C3'), np.str_('C4'), np.str_('C6')], acc=0.382+/-0.031, f1=0.293+/-0.025
```

결과를 보면 mead_std가 정확도 0.434, macro-F1 0.333로 가장 성능이 좋았다. 

전부 가장 많은 아형인 C2로 찍었을때 정확도(최빈 클래스 정확도)랑 5지선다를 랜덤으로 찍었을때(무작위 macro-F1, 여기서는 1/5)의 F1이 각각 0.362, 0.200인데 그에 비하면 정확도는 성능이 낮고 F1은 그것보단 조금 나은 수준이다.

여기서 알수있는 사실은 1) mean_std 쓰는것이 좋다는것과 2) wsi로 immune subtype 예측은 성능이 잘 안나온다는 점이다. 
