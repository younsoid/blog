---
date : 2026-10-06
tags: ['2026-10']
categories: ['paper']
bookHidden: true
title: "Paper #3 Regression-based Deep-Learning predicts molecular biomarkers from pathology slides (우리 연구랑 젤 비슷한 논문 !!)"
bookComments: true
index: 3
---

# Paper #3 Regression-based Deep-Learning predicts molecular biomarkers from pathology slides (우리 연구랑 젤 비슷한 논문 !!)

#2026-10-06

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

<grayblock>

- 요즘은 유전자 돌연변이, msi, gene set 단위 발현량을 슬라이드 이미지로 예측할수있다. 
  - wsi -> 유전적 변화 예측 -> 환자의 예후 예측 << 이게 가능해지는 중이다. 
- 슬라이드 -> 유전정보 예측
  - 약지도 weakly supervised 문제이다. 
- 슬라이드는 수천개 패치인데 어디에 유전정보 하나가 매칭되는지가 핵심이다 (대부분은 결합조직, 지방 등 바이어마커와 무관한 부위)
  - 가장 많이 쓰이는 방법이 attention 기반 다중 인스턴스 학습(attMIL)
  - 각 조각에서 특징 벡터를 뽑고 그 가중치로 조각들을 합쳐 환자단위 예측을 낸다. 대표 논문이 CLAM이다.
- attMIL 기반 논문들은 대부분 분류문제만 다룬다. (유전자 변이가 있다 없다)
  - wgd(전장 유전체 중복): 유전체가 몇배가 되었는지
  - cna(복제수 변이): 특정 부위가 몇개로 늘거나 줄었는지
  - hrd: dna 손상을 고치는 능력이 얼마나 손상되었는지 수치
  - 기타 유전자 발현량, 단백질량 등이 모두 연속형이다.

</grayblock>

* 가설: 약지도 H&E 분석에서 회귀 > 분류
	- ① 예측 성능 ② 임상적으로 알려진 영역과의 대응 ③ 예후 예측력
* 제안: CAMIL regression = 자기지도 특징추출 + attMIL 회귀
	- 비교 대상: CAMIL classification, Graziani et al. regression

<grayblock>

- 회귀를 쓰면?
  - 슬라이드벡터와 유전자 수치 사이의 관계를 그대로 학습 (유전자 수치를 구간화한게 아니라)
- 성능평가는?
  - 바이오마커 예측성능
  - 모델이 슬라이드의 어디를 봤는지가 임상적으로 중요한지. (림프구 침윤 예측 모델임연 림프구가 몰린곳을 보고있는지 등)
  - 생존 분석
- CAMIL regression
  - 대조 군집 attention 기반 다중 인스턴스 학습
  - 앞 구조는 특징 추출기: 병리 이미지로 자기지도학습. 
  - 뒤 구조는 attMIL인데 분류 대신 회귀. 
- 성능 비교는
  - 회귀 말고 분류 버전
  - 다른 회귀 방법과 비교한다.

</grayblock>

###

### 2. Background

2.1 attMIL
* WSI = bag, 타일 = instance, 라벨은 bag에만 (CLAM 노트 2장 참고)
* 타일 특징 → attention 점수 → 가중합 → 환자 단위 예측
* 기반: Ilse et al. (2018) attention-based deep MIL

<grayblock>

- 약지도학습은?
  - 사과를 상자째로 샀는데, 상자에 라벨이 '이 상자에는 썩은사과가 있음/없음' 혹은 '팔수있음/없음'이라는 딱지만 붙어있고, 어느 사과가 썩었는지는 적혀있지 않다. 앞으로 상자를 받아서 썩은사과가 있는지 혹은 팔수있는지 없는지를 판단하는 법을 배워야 한다면? 이게 약지도 학습.
  - multiple instance learning, mil
  - 상자가 가방, 사과 각각이 인스턴스, 정답은 가방에만.
- 병리슬라이드는
  - 슬라이드가 가방, 타일이 인스턴스, 정답은 '이 환자의 hrd는 58' 같은 환자단위값. 어느 타일이 그 점수와 관련있는지는 모르고 타일 대부분은 지방, 결합조직처럼 정답과 무관할수있다.
  - 모델이 스스로 어느 타일을 봐야할지/그 타일들로 정답을 어떻게 낼지 배워야 한다.
- 타일 특징 뽑기
  - RetCCL로 타일 하나를 2048개 숫자로 변환했다.
- 이 숫자를 어떻게 pooling 할것인가?
  - clam은 max pooling했다.
  - 이 논문은 attention 기반 MIL. 어떤 타일에 높은 점수를 줬더니 예측이 정답에 가까워지면, 그런 종류의 타일에 높은 점수를 주는 쪽으로 조정해서 pooling 했다.
- attention 기반 MIL
  - 타일 하나가 2048차원 -> 256차원으로 줄인다.
  - h를 또 다른 작은 신경망(완전연결층과 tanh)에 넣어 128차원으로 줄인다. 마지막 층이 이를 숫자 하나로 줄인다(attention 점수)
  - 타일마다 이 점수를 만들고 softmax로 합이 1이되게한다.
  - 모든 타일의 h에 각자의 a를 곱해 더하면 슬라이드 전체를 대표하는 벡터 하나가 나온다. (길이는 256)
  - 256→128→1로 가는 attention 신경망은 모든 타일에 똑같은 가중치로 적용된다.
- 이 방법의 특징?
  - 순서에 무관하다(permutation invariance): 슬라이드의 타일들에는 순서가 없으므로 적절하다
  - max와 mean을 아우른다: attention이 한 타일에만 몰리면 사실상 max pooling, 모든 타일에 고르게 퍼지면 mean pooling이 되는데 그 중간지점을 모델이 찾는셈이다.
- attention heatmap
  - attention 가중치를 시각화하면 림프구 침윤을 예측하는 모델이 실제로 림프구 밀집 영역을 보는지 등으로 검증할수있다.
- 논문의 특이적 방법론 attMIL
  - attention 기반 MIL은 특징 추출기까지 함께 학습. attMIL은 RetCCL이라는 미리 학습된 자기지도 특징 추출기를 고정해 두고 그 출력만 쓴다.
  - attention 부분은 gated attention(tanh와 sigmoid 두 갈래를 곱하는 방식)이 아니라 tanh 한 갈래만 쓰는 방식. (CLAM은 전자)
  - 마지막 헤드를 세 가지로 바꿔 끼워 분류, Graziani 회귀, CAMIL 회귀를 비교한다.
  - Graziani 방식은 타일마다 먼저 예측값을 내고 그 예측값들을 attention으로 합치는 "인스턴스 수준" 방식이고
  - attMIL은 Graziani 방법을 재구현하면서 특징 벡터(임베딩)를 먼저 합치고 마지막에 한 번 예측하는 "임베딩 수준" 방식으로 바꿨다. (이게 뭔말이야..)
- 회귀의 의미
  - MIL은 "가방 안에 양성 인스턴스가 하나라도 있으면 가방도 양성"이라는 분류용 가정이다.
  - 그런데 회귀에서는 이 가정이 잘 맞지 않다. 백혈구 비율이나 기질 비율 같은 값은 "어딘가에 하나라도 있느냐"가 아니라 "조직 전체에 얼마나 퍼져 있느냐"이기 때문.
  - 사과 비유로 치면 팔아도 되냐 아니냐가 아니라 팔았을때 환불 확률을 예측하는 느낌.
  - 근데 attention 가중평균은 백혈구 비율이나 기질 비율 같은 값과 오히려 더 잘 맞는 방식이다. 슬라이드 전체의 비율이란 결국 각 부분의 기여를 어떤 가중치로 평균한 것이기 때문에. (이것도 이해 못함..)
- 한계
  - attention은 softmax로 합이 1이 되도록 정규화되므로 상대적인 중요도. 그래서 "이 슬라이드에서 이 타일이 다른 타일보다 중요했다"는 말할 수 있어도, "이 타일에 림프구가 얼마나 많다"는 절대량을 말해 주지는 않는다.
  - 높은 attention이 곧 "이 타일이 예측값을 올렸다"를 뜻하지는 않는다. 중요하다고 본 것과 어느 방향으로 기여했는지는 다르다.
  - 기본 attMIL은 각 타일을 독립적으로 채점하므로, 타일들 사이의 공간적 관계, 예를 들어 "림프구가 종양 가장자리에 모여 있는가, 종양 안쪽까지 들어왔는가" 같은 정보는 직접 활용하지 못한다. (이해 못했는데 암튼 중요해보임)

</grayblock>

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
