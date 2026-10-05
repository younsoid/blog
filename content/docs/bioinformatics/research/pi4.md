---
date : 2026-10-05
tags: ['2026-10']
categories: ['paper']
bookHidden: true
title: "Paper #3 Regression-based Deep-Learning predicts molecular biomarkers from pathology slides"
bookComments: true
index: 2
---

# Paper #3 Regression-based Deep-Learning predicts molecular biomarkers from pathology slides

#2026-10-05

---

### 1. Introduction

* WSI에서 유전자 변이, MSI, 유전자 발현 등 예측 가능 → 일부는 규제기관 승인, 사실상 임상 도구화
* 유전형-표현형 예측 = 약지도 문제
	- 라벨은 환자 단위 1개 (시퀀싱 결과), 입력은 기가픽셀 → 타일로 분할
	- 결합조직·지방 등 무관한 타일 많음 → attMIL이 주류 해법
* 핵심 문제: 거의 모든 연구가 분류(categorical)
	- 실제 바이오마커는 연속값: WGD, CNA, HRD, 유전자 발현, 단백질 양 등
	- 연속값을 이진화·임계값 분할 후 학습 → 정보 손실
	- 예: Fu(LASSO로 3클래스화), Schmauch(회귀 후 백분위 임계값 평가), Chen(Cox 위험점수 이분화)
* 기존 회귀 시도와 한계
	- Huang(대조학습 + 선형회귀), Dawood(OLS, 공간 발현), Mondol·Hoang(CNN 회귀, mRNA)
	- Schirris: MIL 회귀로 sTIL 예측, attention 없음이 한계
	- Weitz: attention 넣으니 일반화 저하 (단일 암, 소규모)
	- Graziani: attMIL 회귀 제안, 분류와 체계적 비교·검증 부족
* 가설: 약지도 H&E 분석에서 회귀 > 분류
	- ① 예측 성능 ② 임상적으로 알려진 영역과의 대응 ③ 예후 예측력
* 제안: CAMIL regression = 자기지도 특징추출 + attMIL 회귀
	- 비교 대상: CAMIL classification, Graziani et al. regression

<grayblock>

- 유전형-표현형 상관, 즉 슬라이드 형태 패턴으로 유전형 변화를 예측할수있다. 

</grayblock>

###

### 2. Background

2.1 attMIL
* WSI = bag, 타일 = instance, 라벨은 bag에만 (CLAM 노트 2장 참고)
* 타일 특징 → attention 점수 → 가중합 → 환자 단위 예측
* 기반: Ilse et al. (2018) attention-based deep MIL

2.2 자기지도 특징추출기 RetCCL
* ImageNet 사전학습 ResNet50 → 병리 WSI 32,000장으로 대조 군집(contrastive clustering) 자기지도 미세조정
* 타일당 2048차원 벡터, ImageNet 단독보다 성능·일반화 우수

2.3 예측 대상 바이오마커
* HRD (임상 cutoff 있는 연속값)
	- 상동재조합 결핍 점수 = LOH + TAI + LST 합, 범위 0~103
	- cutoff ≥ 42 → HRD+ (백금 항암 반응 예측 근거, Telli et al.)
* 생물학적 과정 바이오마커 (cutoff 없음, Thorsson "Immune Landscape of Cancer")
	- 종양세포: Proliferation (RNA 시그니처), [−2.86, 1.59]
	- 기질: Stromal Fraction (DNA 메틸화 기반), [0, 0.92]
	- 면역: Leukocyte Fraction (DNA 메틸화 기반), [0, 0.96]
	- 면역: LISS (RNA 시그니처), [−3.49, 4.17]
	- 면역: TIL Regional Fraction (H&E 딥러닝 기반 정량), [0, 63.65]

2.4 분류 vs 회귀
* 분류: 연속값을 잘라 클래스로 → 경계 근처 정보·크기 정보 손실 (Riley et al.)
* 회귀: 연속값 그대로 학습
* Balanced MSE: 값 분포 불균형(희귀 구간)을 보정한 회귀 손실

###

### 3. Method

3.1 데이터·코호트
* 총 11,671 WSI (Aperio 스캐너)
* HRD
	- 학습: TCGA BRCA, CRC, GBM, LUAD, LUSC, PAAD, UCEC (3,273)
	- 외부: CPTAC LUAD, LSCC, PDA, UCEC (452)
* 생물학적 과정 바이오마커
	- 학습: TCGA BRCA, CRC, LUAD, LUSC, LIHC, STAD, UCEC
	- TIL RF 3,124 / Prolif 3,636 / LF 3,719 / LISS 3,636 / SF 3,513
	- LIHC는 TIL RF 없음 → 7암 × 5지표 − 1 = 34개 과제
	- 외부(생존): DACHS 대장암 2,297명, 10년 전체생존 추적
[그림 1D] 코호트 구성 (안쪽 원 = 학습, 바깥 원 = 외부검증)

3.2 전처리
* 타일링: 224×224 px = 256 µm (약 1.14 MPP)
* Canny 엣지 검출로 엣지 ≤ 2개 타일 제거 (흐림·배경)
* 밝기 표준화 + Macenko 염색 정규화

3.3 특징 추출
* RetCCL 추론 → 환자당 n × 2048 특징 행렬
[그림 1A] 전처리 + 특징추출 파이프라인

3.4 모델 구조
* 공통 몸통: bag encoder(FC + ReLU, 2048→256) → gated 아닌 attention(FC + tanh → 128 → FC → 1) → attention 가중합(256)
* 헤드 3종 (각각 따로 학습)
	- CAMIL classification: Flatten → BatchNorm → Dropout → FC
	- Graziani regression: Flatten → ReLU → FC → Dropout → FC
	- CAMIL regression: Flatten → FC (dropout 제거)
* CAMIL regression 학습: Balanced MSE, Adam, 25 epoch
* Graziani 재구현 시 변경: ResNet18 + 패치 단위 attention → RetCCL + 임베딩 단위 attention (헤드만 비교하려는 목적)
* 공통 설정: lr 1e-4, weight decay 1e-2, patience 12, fit-one-cycle 스케줄
* 하이퍼파라미터 최적화 안 함
[그림 1B] 모델 구조

3.5 학습·검증 설계
* 환자 단위 5-fold CV, site-aware split (80/20)
	- 같은 병원 환자는 한쪽에만 → TCGA 병원별 조직 특징에 의한 과대평가 방지
	- 클래스 분포 유지, 모든 모델이 동일 환자 분할 사용
* 내부 검증 = TCGA 내 미사용 fold / 외부 검증 = CPTAC, DACHS
* 5개 fold 모델 예측의 중앙값 앙상블 → 환자당 점수 1개 (전체 재학습보다 외부 일반화 좋음)
[보충 그림 6]

3.6 평가
* AUROC (모든 모델 공통 비교 지표)
	- 정답 이진화: HRD는 ≥42, 나머지는 중앙값 분할
	- 분류 점수 [0,1], 회귀 점수 (−∞, ∞)를 연속 점수로 그대로 사용
	- 95% CI는 5 fold 기준
* 쌍대 양측 DeLong 검정 × 3쌍, Bonferroni 보정 (α = 0.0167)
* 회귀 모델끼리: Pearson r
* 분리도(HRD만): robust min-max 정규화(2.5~97.5 백분위) 후 HRD+ / HRD− 중앙값 간 거리
* 생존: DACHS에 블라인드 적용, 단변량·다변량 Cox PH
	- 공변량: 나이, 성별, 병기
	- 분류 모델도 라벨 대신 연속 점수 사용
	- HR 95% CI가 1을 안 지나면 유의, 1에서 멀수록 예후력 강함
* Attention heatmap: 완전합성곱 형태로 변환해 고해상도 heatmap 생성
	- TCGA-BRCA 테스트셋 LISS 상위 42명 → 분류·회귀 heatmap 84장
	- 병리 레지던트 1인 블라인드 리뷰, Graziani는 품질 낮아 제외
[그림 1C] 평가 지표 개요

###

### 4. Results

4.1 회귀로 HRD 예측
* CAMIL regression, TCGA 7암 중 5개에서 AUROC > 0.70
	- BRCA 0.78 / CRC 0.76 / GBM 0.64 / PAAD 0.72 / LUAD 0.72 / LUSC 0.57 / UCEC 0.82
* CPTAC 외부검증
	- PAAD 0.68 / LUAD 0.81 / UCEC 0.96 / LUSC 0.62
[그림 2A, 2B], [보충 표 1]

4.2 기존 방법과 비교 (HRD)
* TCGA: CAMIL regression이 7암 중 5개에서 최고 AUROC (GBM·LUSC 비슷)
* 통계적 유의차는 일부만
	- BRCA: CAMIL classification vs Graziani
	- CRC: CAMIL regression vs Graziani
	- CPTAC 외부: 세 모델 간 유의차 없음
* CAMIL regression은 fold 간 성능 분산이 더 작음 → 더 견고한 특징 학습 주장
* 분리도: 예) CPTAC-UCEC AUROC 분류 0.98 / Graziani 0.89 / CAMIL 회귀 0.96 (유의차 없음)
	- 그래도 점수 분포는 CAMIL 회귀가 HRD+ / HRD− 더 뚜렷하게 분리
	- TCGA 7/7, CPTAC 2/4에서 분류보다 중앙값 거리 큼
	- 평균 개선: 분류 대비 TCGA 9.9%, CPTAC 4.9% / Graziani 대비 6.6%, 9.5%
[그림 2C–H], [보충 표 3]
* Pearson r: Graziani보다 TCGA 7/7, CPTAC 2/4에서 높음 (PAAD는 둘 다 낮음)
* Ablation: Graziani 성능 저하의 주원인 = SGD 옵티마이저 (Adam 대비) → 예측이 평균으로 수렴
[보충 표 4–6], [보충 그림 1]
* 생물학적 일관성 확인
	- TCGA-BRCA: BRCA1 germline(p ≤ 0.0001), BRCA2 somatic(p ≤ 0.05) 변이군에서 HRD 예측 유의차, 세 모델 모두
	- BRCA1 somatic, BRCA2 germline은 유의차 없음
	- TCGA-CRC: CAMIL 회귀만 HRD 예측 높음 ↔ MSS(p ≤ 0.01), 낮은 TMB(p ≤ 0.05) 연관
[보충 그림 2]

4.3 생물학적 과정 바이오마커 예측
* CAMIL regression, 34개 과제 중 28개에서 AUROC > 0.70
	- BRCA: TIL RF 0.88 / Prolif 0.84 / LF 0.80 / LISS 0.80 / SF 0.81
	- CRC: TIL RF 0.79 / Prolif 0.59 / LF 0.76 / LISS 0.70 / SF 0.68
* vs CAMIL classification
	- AUROC 더 높음 29/34, 통계적 유의 4/34
	- 유의: BRCA LISS·TIL RF, CRC Prolif, LIHC Prolif
	- 평균 AUROC +4%
* vs Graziani
	- AUROC 높음 33/34, Pearson r 높음 34/34, 유의 14/34
	- (분류가 Graziani를 유의하게 이긴 경우는 5/34)
	- 평균 AUROC +12%
[그림 3A, 3B], [보충 표 7–9], [보충 그림 3, 4]

4.4 Attention heatmap과 임상 지식의 대응
* TCGA-BRCA LISS: 분류·회귀 모두 림프구 밀집 영역 주목
	- 회귀: 림프구 영역 경계가 더 선명, 무관한 영역 주목 적음
	- 분류: 림프구 밀집부 attention 낮고, 림프구 없는 조직 가장자리에 주목
	- Graziani: 무관한 영역 강조, 림프구 영역 놓침
* 블라인드 리뷰 42예: 회귀 우세 34 / 분류 우세 6 / 비슷 2 → 회귀 81%
[그림 3C], [보충 그림 5]

4.5 대장암 생존 예측 (DACHS, 2,297명)
* TCGA-BRCA로 학습한 모델을 대장암에 적용 (분류·회귀 차이가 유의했던 유일한 암이라 선택)
	- 분류: 단변량 유의 2/5 (TIL RF, LF), 다변량 1/5 (Prolif, HR 1.44 [1.00–2.06], 경계선)
	- 회귀: 단변량 유의 3/5 (TIL RF, LF, LISS), 다변량 2/5 (LF, LISS)
* TCGA-CRC로 학습한 모델 적용
	- 두 방법 모두 대부분 지표에서 단변량 유의
	- HR 효과 크기는 회귀가 3/5에서 더 큼 (TIL RF, LF, LISS)
* Graziani: 예측값 분산이 너무 작아 Cox 모델 수렴 실패
* 성별 분리 분석 [보충 표 14, 15]
[그림 4] (A·B 분류 단변량·다변량, C·D 회귀 단변량·다변량)

###

### 5. Discussion

* 2018년 이후 병리 기반 분자 바이오마커 예측 급성장, 그러나 연속 바이오마커를 분류로만 다뤄 옴
* CAMIL regression이 분류·기존 회귀보다 우수하다는 직접 증거 제시 주장
* HRD처럼 임상 cutoff가 있는 바이오마커에서도 회귀가 정확도·분리도 개선
	- BRCA1/2 결과는 기존 HRD 연구와 일치 → 여전히 정식 germline 검사 필요
	- CRC에서 HRD ↔ MSI·TMB 역상관(알려진 생물학) 회귀만 포착
	- TCGA-CRC HRD+ 16명뿐 → 적은 양성 샘플로도 형태 표현형 포착 가능성
* cutoff 없는 면역 바이오마커에서도 유사한 개선, 외부 코호트 일반화 더 좋음
* Graziani 성능 저하 원인 = 옵티마이저 → 예측이 평균으로 수렴
* heatmap 81% 선호, 면역 바이오마커 기반 생존 위험군 분리 개선
* 한계
	- 제한된 암종·바이오마커, 모든 지표에 외부셋 있는 건 아님 → site-aware 분할(유사 외부검증)과 블라인드 외부 적용으로 대체
	- 하이퍼파라미터 최적화 안 함
	- 연속 라벨 자체의 측정 잡음·불확실성 → 정확한 값 회귀는 문제될 수 있음, KL divergence 손실 제안
	- 회귀(잡음 라벨) vs 분류(정보 손실) trade-off, 회귀가 실패하는 조건 규명 필요
* 결론: 회귀 기반 attMIL의 개념 증명(proof-of-principle)

###

### 6. 읽으며 체크할 점 (한계·불일치)
* 초록은 "유의하게 향상"이라 하지만 실제 유의차는 일부
	- 생물학적 바이오마커 4/34, HRD 외부검증은 0, 대부분 "수치상 높음" 수준
* 비교 조건이 헤드만 다른 게 아님
	- 분류 헤드는 BatchNorm·Dropout 포함, 회귀 헤드는 FC 하나 + Balanced MSE
	- 분류 모델의 손실·옵티마이저 세부 미기재, 어떤 모델도 튜닝 안 함
* Graziani 기준선이 약함: 성능 차이 대부분이 SGD vs Adam → 사실상 옵티마이저 비교
* 분리도 지표(정규화 후 중앙값 거리)는 비표준, 시그모이드 출력은 양 끝으로 몰려 불리할 수 있음, HRD에만 적용
* heatmap 리뷰: 레지던트 1인, 평가자 간 일치도 없음, LISS 상위 42명만 선택
* 생존 분석
	- BRCA 학습 모델을 CRC에 적용한 근거가 "차이가 유의했던 암"이라 선택 편향 가능
	- 5개 지표 × 여러 모델 Cox 분석에 다중비교 보정 없음
	- 분류 점수를 "logits [0,1]"로 표기 → 실제로는 확률(시그모이드 출력)
* 정답 라벨 특성
	- TIL RF 정답 자체가 H&E 딥러닝으로 만든 값 → 이미지로 예측하기 상대적으로 쉬움
	- LF·SF는 DNA 메틸화 기반 → 앞의 메틸화 디컨볼루션 논문과 직접 연결되는 지점
	- 중앙값 분할 AUROC는 중앙값 근처 환자에서 잡음 큼
* TCGA-CRC HRD+ 16명 → CRC HRD 결과는 신뢰구간 넓음
* 그림 인용 오류: 본문은 회귀 생존 결과를 그림 4A·B로 인용 (실제는 4C·D)
* 그림 3 캡션에 PAAD 포함되어 있으나 히트맵에는 PAAD 없음
* "11,671 images of patients" → 환자 수가 아니라 슬라이드 수