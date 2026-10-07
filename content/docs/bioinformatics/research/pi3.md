---
date : 2026-10-05
tags: ['2026-10']
categories: ['insight']
bookHidden: true
title: "메틸레이션 라벨에 대한 생각"
bookComments: true
index: 1
---

# 메틸레이션 라벨에 대한 생각

#2026-10-05

---

#1

지금 연구계획상에서 메틸화 라벨은 어떻게 만드냐면
- TCGA 메틸화 array 데이터를 가져오고 필터링을 한다 (결측이 많은 probe와 비특이적 probe 등 제거)
- promoter/TSS 영역이나 유전자 단위로 메틸화 값을 요약한다. (단순 beta 값 평균낸거)
- 이 값으로 샘플을 클러스터링한다.
- 메틸화 pseudotime을 계산해서 변화 축을 따라 pseudotime high / intermediate / low 클러스터로 나눈다. (그룹1)

그리고 이 클러스터들에 대해서
- ESTIMATE immune/stromal score, TIL 관련 지표, TMB, 생존 base 면역 점수를 보고 
- 면역 점수가 높은 쪽을 immune-rich, 낮은 쪽을 immune-depleted 클러스터로 또 묶는다. (그룹2)

그리고 WSI를 input으로 받는 모델이 뭘 예측하냐면
- methylation-defined immune state (그룹2)
- immune score high/low
- TIL/TMB phenotype
- methylation pseudotime group (그룹1)

이렇게를 예측시킨다.

#2

Expression 신호가 너무 세서 methylation이 묻히는걸 막으려면 이렇게 디자인하면 된다.

WSI를 input으로 받는 모델에
- methylation pseudotime group (그룹1)
- methylation-defined immune state (그룹2)

이렇게 일단 예측시키고

둘을 비교해서 메틸화 라벨이 RNA 면역 점수만으로는 설명되지 않는 정보를 준다는 것을 보여준다.

#3

그리고 메틸화 클러스터가 '종양의 메틸레이션 상태 변화'보다 '단순 면역세포 조성'을 반영할 위험이 있다. MethylCIBERSORT가 메틸레이션으로 세포 비율을 측정하는 도구인데 이런 도구를 사용하든 해서 세포 조성의 기여를 최대한 배제해야 맞을것같다.
