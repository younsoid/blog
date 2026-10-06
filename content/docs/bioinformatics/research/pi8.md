---
date : 2026-10-05
tags: ['2026-10']
categories: ['연구']
bookHidden: true
title: "데이터 전처리 - Site별 라벨링"
bookComments: true
index: 5
---

# 데이터 전처리 - Site별 라벨링

#2026-10-05

---

<img width="680" height="524" alt="image" src="https://github.com/user-attachments/assets/7d49182c-bbeb-477a-9346-9412ad694ee9" />

현재 다운받은 유방암 병리슬라이드 정보가 brca_slide_level_mean.csv로 저장돼있는데 파일을 확인해보면 통계치는 다음과 같이 나온다.

```plain text
슬라이드: (960, 768) | 환자: 910 | 병원: 34
```
960장 슬라이드에 대해서 umap을 그려보면 다음과 같이 나온다.

<img width="680" height="524" alt="image" src="https://github.com/user-attachments/assets/c803d715-6448-41d8-8c8a-08160197eab4" />

위 umap에 병원 34개의 정보를 입혀보면 아래와 같다.

<img width="854" height="630" alt="image" src="https://github.com/user-attachments/assets/23601be8-e40a-4365-813a-f14ddb3b3bb3" />

육안으로 봤을때 병원끼리 뭉쳐보이기는 한다.

육안으로 뭉쳐보이는 클러스터를 정의해서 실제로 병원 purity를 계산해본다. purity가 높으면 EXAONEPath 1.0 임베딩의 가장 큰 변동 축은 생물학이 아니라 병원별 처리 차이가 되니까 배치 처리를 하든 2.5를 쓰든.. 방법을 찾아야 할수도 있다. 

클러스터 정의는 dbscan으로 수행해줬다. 

```python
from sklearn.cluster import DBSCAN

df["island"] = DBSCAN(eps=DBSCAN_EPS, min_samples=3).fit_predict(emb)   # -1 = 어디에도 안 속함

rows = []
for isl, g in df.groupby("island"):
    vc = g.tss.value_counts()
    rows.append({
        "island": isl, "n": len(g),
        "center": f"({g.umap1.mean():.1f}, {g.umap2.mean():.1f})",
        "top_site": vc.index[0], "top_n": vc.iloc[0],
        "purity": round(vc.iloc[0] / len(g), 3),
        "sites(상위4)": ", ".join(f"{k}:{v}" for k, v in vc.head(4).items()),
    })
island_tbl = pd.DataFrame(rows).sort_values("n", ascending=False)
print(island_tbl.to_string(index=False))

big = island_tbl[island_tbl.n >= 10]
print(f"\n10장 이상 섬 {len(big)}개 중 purity ≥ 0.9: {(big.purity >= 0.9).sum()}개")
```
```plain text
 island   n        center top_site  top_n  purity                  sites(상위4)
      1 643   (14.9, 1.7)       BH    112   0.174 BH:112, A2:84, E2:74, A7:59
      0  93    (8.4, 2.9)       D8     90   0.968     D8:90, 4H:1, JL:1, Z7:1
      2  81   (-6.0, 5.0)       A8     81   1.000                       A8:81
      7  41    (6.2, 9.5)       C8     41   1.000                       C8:41
      5  32   (11.8, 8.6)       AR     30   0.938           AR:30, BH:1, GM:1
      6  24  (11.6, 10.3)       AR     24   1.000                       AR:24
      8  14  (-6.7, -0.1)       E9     14   1.000                       E9:14
      3  13 (10.4, -10.8)       PL      9   0.692                  PL:9, AN:4
      4  12   (16.3, 8.0)       AO     12   1.000                       AO:12
      9   7   (10.8, 5.8)       OL      7   1.000                        OL:7

10장 이상 섬 9개 중 purity ≥ 0.9: 7개
```

유의미한 크기의(개수가 10장 이상인) 클러스터는 9개였고, 그중 7개가 purity 0.9 이상이었다. 
- A8(81장), C8(41장), AR(24장), E9(14장), AO(12장), OL(7장) 클러스터 100% 한 병원으로만 이루어져 있고
- D8 클러스터(93장)는 97%가 D8였다.
- 큰 클러스터(643장)에는 BH, A2, E2, A7 등이 섞여 있다(purity 0.17).

```python
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GroupKFold, cross_val_score

mask = df.tss.isin(df.tss.value_counts()[lambda s: s >= 10].index)   # 10장 이상 병원만
Xs, ys, gs = X[mask.values], df.tss[mask].values, df.patient[mask].values
baseline = pd.Series(ys).value_counts(normalize=True).iloc[0]

cv = GroupKFold(n_splits=5)
clf = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, C=0.1))
acc_full = cross_val_score(clf, Xs, ys, cv=cv, groups=gs, scoring="accuracy")
acc_umap = cross_val_score(KNeighborsClassifier(15), emb[mask.values], ys, cv=cv, groups=gs, scoring="accuracy")

print(f"대상: {mask.sum()}장, 병원 {len(set(ys))}곳")
print(f"기준선(최빈 병원 비율): {baseline:.3f}")
print(f"768차원 임베딩 → 병원 예측 정확도: {acc_full.mean():.3f} ± {acc_full.std():.3f}")
print(f"UMAP 2D 좌표   → 병원 예측 정확도: {acc_umap.mean():.3f} ± {acc_umap.std():.3f}")
```
```plain text
대상: 909장, 병원 18곳
기준선(최빈 병원 비율): 0.124
768차원 임베딩 → 병원 예측 정확도: 0.957 ± 0.009
UMAP 2D 좌표   → 병원 예측 정확도: 0.862 ± 0.015
```

게다가 슬라이드 벡터로 병원코드 맞히기를 해봤을때, 768차원 임베딩으로 병원 18곳을 맞히는 정확도가 0.957이다. (naive: 0.124) UMAP 좌표만으로도 0.862가 나온다.

즉 EXAONEPath 1.0 임베딩에 병원 시그니처가 강하게 들어있는 것이다.

원래 목적은 이 슬라이드 벡터로 methlaytion label 기반의 immune signature(immune-rich, immune-poor)를 맞히는것이었다. 그래서 meth label이 병원에 따라 갈리는게 아니니까 크게 문제되는것은 아니지만 뒤에서 <line>맞히는 성능을 병원별로 테스트해볼 필요가 있을듯하다.</line> 
