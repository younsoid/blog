---
date : 2026-10-03
tags: ['2026-10']
categories: ['논문']
bookHidden: true
title: "논문 #1 Evaluation of Pan-Cancer Immune Heterogeneity Based on DNA Methylation"
bookComments: true
index: 1
---

# Paper #1 Evaluation of Pan-Cancer Immune Heterogeneity Based on DNA Methylation

#2026-10-05

---

### 1. Introduction 

* TME = 다양한 세포 + ECM + 성장인자·케모카인 -> 이질성이 종양 발달·치료에 영향 
* 세포 이질성 = 종양 이질성의 주요 원천
	- CD8+ T: MHC I 항원 인식 -> IFN-γ, granzyme B (세포독성)
	- CD4+ Th: IL-2/4/17 → 대식세포·B세포 활성 보조
	- 대식세포: M1(IL-1β, TNF-α, 항종양) vs M2(IL-10, TGF-β, 면역억제)
	- Treg: TGF-β, IL-10 → 면역관용
	- NK: IFN-γ, 종양세포 파괴
	- 호중구: VEGFA, MMP9 → 혈관신생·침윤 촉진

<grayblock>

- tme, 종양미세환경은 종양 조직 안에 면역세포, 혈관을 만드는 세포, 섬유를 만드는 세포, 성장인자나 케모카인 같은 신호물질 등의 구성. 이게 암 안에서도 사람마다 다르다(heterogenity).
- cd8+는 granzyme B로 종양 공격, IFN-γ, IL-2, IL-4, IL-17로 대식세포나 B세포에 신호도 보냄.
- M1은 IL-1β와 TNF-α로 염증유발, 종양공격. 
- M2는 IL-10과 TGF-β로 면역반응 진정.
- Treg는 TGF-β와 IL-10로 면역반응 진정.
- NK는 IFN-γ로 종양 공격.
- 호중구는 VEGFA로 혈관신생, MMP9로 주변 조직을 녹여 길을 터 주기 때문에(침윤), 종양에게 보급로와 탈출로를 제공할수있다.
- 이 면역세포의 기능은 메틸화가 정한다.

</grayblock>

* 기존 연구 한계
	- flow cytometry / 유전자발현 기반
	- 특정 암종 하나에 집중
* 본 연구 차별점: DNA 메틸화로 pan-cancer 수준 면역 이질성 평가
* 목표: 특이 메틸화 유전자로 14암종 deconvolution → 면역 아형 분류 → 생존·병기·발현과 연관

<grayblock>

- 기존연구는 발현량으로 면역 침윤 추정, 여기서는 메틸화를 본다.
- 기존 연구는 1종으로 하는데 여기서는 14종 pan cancer 연구고 암 사이 공통점과 차이점을 볼수있다.
- 메틸화는 발현보다 상대적으로 안정적인 표지라서 순간적인 면역 상태보다 세포의 정체성을 더 잘 반영한다.
- Shannon 엔트로피로 7종 면역세포 각각에 특이적인 메틸화 위치 1256개를 식별. TCGA에 있는 14개 암종, 5323개 종양 샘플에 이 1256개 위치를 적용해 각 샘플의 면역세포 비율을 계산. 면역 세포 비율로 5323개 샘플을 클러스터링하고 각 subtype별 환자의 생존, 임상 병기, 면역 관련 유전자 발현과의 연관성을 본다.

</grayblock>

###

### 2. Background (핵심 개념)

2.1 DNA 메틸화
* 서열 변화 없이 유전자 발현 조절
* 면역세포 메틸화 패턴 = 분화상태·기능 반영
* epigenome의 주요 결정요인 = 세포유형 특이 분화 (유전·환경 아님)
	- 같은 세포유형은 샘플 간 메틸화 패턴 보존적

<grayblock>

- Illumina 450K: 사람 DNA의 45만 개 CpG 자리를 모두 봐서 메틸화 비율을 beta로 측정
- 줄기세포에서 특정 세포로 분화할때 DNA가 바뀌는게 아니라 메틸화를 조절해서 분화한다. 그래서 cell type별로 메틸화 패턴이 있다. 이후 분열할때도 유지된다. 그리고 개체(사람)별 차이보다 cell type 별 차이가 더 뚜렷하다고 한다.

</grayblock>

2.2 Deconvolution 원리
* 조직 메틸화 = 세포유형별 메틸화 × 세포 비율의 합성(convolution)
* 알려진 면역세포 reference로 역산 → 조직 내 면역세포 비율 추정

<grayblock>

- 최소제곱법으로, 면역세포 7개에 대한 방정식을 풀어서 7개에 대한 답을 얻는다.
- 데이터는 beta 값.
- 즉 1256개 cpg를 쓰므로 미지수 7개에 방정식 1256개인 셈이고 최소제곱법으로 푸는데 현실성 반영해서 제약을 줬고 제약을 준 최소제곱법은 이차계획법(quadratic programming, QP)으로 푼다.

</grayblock>

###

### 3. Method

3.1 데이터
* TCGA: 14암종, 종양 5323 + 정상 700 (메틸화·발현·임상)
	- BRCA 794 / CHOL 45 / COAD 309 / ESCA 186 / HNSC 530
	- KIRC 323 / KIRP 276 / LIHC 380 / LUAD 471 / LUSC 370
	- PAAD 185 / PRAD 503 / THCA 515 / UCEC 436
* GEO GSE35069: 7 면역세포 × 6 = 42 샘플
	- CD4+ T, CD8+ T, CD56+ NK, CD19+ B, CD14+ 단핵구, Neu, Eos
* 플랫폼: Illumina 450K

<grayblock>

- 14개 암종의 종양 샘플 5323개와 정상 조직 샘플 700개.
- 클러스터링 후 이 subtype은 정상보다 CD8+ T세포가 많다. 이런식으로 특징짓는다
- GSE35069 데이터셋이 면역세포 7개를 6명한테서 메틸화 측정한 데이터인데 이걸로 검증도 한다.

</grayblock>

3.2 세포 특이 메틸화 유전자 선별
* 전처리: probe → 유전자 매핑, 같은 유전자 값 평균 → 약 20,000개
* 대부분 유전자는 7세포 간 보존 → 정보 없음 = 잡음으로 간주
* QDMR(v1.0): Shannon entropy 기반 특이 사이트 선별 (식 1)
	- H0 = -Σ p_s/r · log2(p_s/r)
	- p_s/r = 해당 영역 전체 메틸화 대비 각 샘플의 상대 메틸화
	- 임계값: 메틸화 확률 모델로 샘플 간 무작위 변이 통제
* 결과: 1256개 특이 유전자 → deconvolution 입력 (잡음 제거, 효율↑)

<grayblock>

- 유전자마다 7종 세포의 메틸화 값의 엔트로피를 구한다. 7종 모두 같으면 최댓값인 log₂7, 약 2.81정도 나오고 치우칠수록 0에 가깝다.
- 엔트로피 낮은, 정보량 많은 유전자를 고를때 cutoff는 메틸화 확률 모델을 사용. 이로써 1256개 유전자를 고름.

</grayblock>

3.3 Deconvolution
* 선형 모델: y_i = Σ a_j · x_ij + ε_i (식 2)
	- y = 조직 메틸화, x = 세포 reference, a = 침윤 비율
* QP(quadratic programming)로 오차제곱합 최소화 (식 3)
* 제약: Σα ≤ 1, 0 < α < 1 (식 4)
* R quadprog(1.5-8), 침윤값 0.01 미만은 기록 안 함
* 입력: 조직 행렬(1256 × 6023) + 세포 행렬(1256 × 7)
* 출력: 6023 샘플 × 7세포 침윤 비율
* 통계: 종양 vs 정상 t-test, 14암종 간 ANOVA

<grayblock>

- 디컨볼루션 방법 요약
  - 1256 × 7 행렬(1256개 유전자별 7개 cell type에서 메틸화 비율 정답)과 1256 × 6023(유전자별 샘플의 메틸화비율값) 행렬이 input이다.
  - 6023개 샘플마다 7개 cell type별 정답 비율을 몇 %씩 섞어야 현재 샘플의 1256개 값과 오차가 최소가 되는지를 계산한다.
  - 이때 제약을 걸어서 이차계획법으로 푼다.
- 샘플별로 7개 cell type의 조성을 구한다음에 암종별로 종양과 정상의 차이를 t-검정하고, 14개 암종끼리 비율의 차이를 ANOVA 검정으로 본다.

</grayblock>

3.4 면역 침윤 기반 군집화
* K-means: 군집 내 중심까지 제곱거리 합 최소화 (식 5, 6)
* ConsensusClusterPlus(1.70.0), k = 2~20, 100회 반복
* 최적 k: CDF 곡선 아래 면적 증가가 안정되는 최소 k
	- 과군집(파편화)·저군집(과단순화) 방지
* t-SNE로 시각화·군집 품질 확인
* 아형 주석: 각 군집 vs 정상, 7세포별 증가/감소/무변화
* 특이 사이트 메틸화–발현 상관 평가

<grayblock>

- 7개 세포의 (메틸화 비율이 아니라) 조성으로 암종 subtype 내에서 clustering을 한다.
- kmeans로 하는데 consensus clustering으로 k=2~20까지 돌린다. 
- cdf 곡선(elbow plot인듯)으로 최적의 k를 고른다.
- 클러스터링 결과 14개 암종 도합 42개 subtype이 나옴.

</grayblock>

3.5 표현형 분석
* 14암종 공통 표현형만 사용: 생존, 병기, 종양 크기 (결측 많은 항목 제거)
* Kaplan–Meier + log-rank, R survival(3.6-4)

3.6 전사체 분석
* 각 면역세포 high 아형 vs 정상 → DEG → KEGG 경로 분석
* 7세포 DEG 합집합 → 통합 경로 분석
* 면역관문 유전자(ICG) 79개 (CTLA-4, PD-1, PD-L1 등) 아형 간 비교
* ESTIMATE: ssGSEA → stromal / immune / ESTIMATE score, 종양 순도
* TIDE: 고침윤 = T세포 dysfunction, 저침윤 = T세포 exclusion 분석
	- TIDE 높음 = 면역치료 반응 낮음


<grayblock>

- subtype 별로 labeling, expression과 methylation 상관관계 계산
- Kaplan–Meier 플롯으로 임상 정보 연결해서 생존 분석. log rank 검정으로 유의성 확보.
- deg 분석, 면역관문 유전자(ICG) 점수, ESTIMATE 점수, TIDE 점수 분석

</grayblock>


###

### 4. Results

4.1 연구 개요
* GEO 42샘플 → QDMR 1256 유전자 → TCGA 5323샘플 deconvolution → 군집화 → 다중오믹스 분석
[그림 1] (A 데이터·특이 유전자 선별, B deconvolution·군집화·t-SNE, C 다중오믹스 통합)

4.2 종양 면역 침윤 평가
* 1256 유전자 경로 분석 → 대부분 면역 관련 → 유전자셋 타당성 간접 지지
[보충 그림 S1, 보충 표 S1, S2]
* CD4+ T 전반적으로 높음 (14암종 평균 0.3274)
* CD8+ T 평균 0.0339
* HNSC·LIHC·LUAD·LUSC: CD4↓, CD8↑ → 이들 암의 구분 특징
* 종양 vs 정상: 최소 9/14 암종에서 유의차
	- CD8 대부분 ↑, CD4 대부분 ↓
* ANOVA: 14암종 간 침윤 비율 유의차 → 암종 signature로 활용 가능
[그림 2] (A 14암종 침윤 heatmap, B 종양 vs 정상 dot plot), [보충 그림 S2]

4.3 면역 침윤 기반 아형
* 14암종 → 42아형 (암종당 2~5개)
* t-SNE에서 아형 분리 양호
[그림 3A], [보충 그림 S3]
* CD4 = 아형 간 변동 큼, CD8·Eos = 거의 0이라 변동 작음
* LUSC·BRCA 아형 차이 큼, CHOL·KIRP 보수적
[그림 3B], [보충 그림 S4]
* 정상 대비 주석 (보정 t-test)
	- CD4·CD14: 35/42 아형에서 유의
	- CD8 27개, Eos 26개 아형에서 유의
	- Neu 감소가 가장 두드러짐 (절반 이상)
	- CD56·CD14·CD8 ↑, CD4·CD19 ↓
[보충 표 S3]
* 특이 사이트 메틸화–발현 상관 > 무작위 상관 (거의 모든 아형)
[그림 3C], [보충 그림 S5]

4.4 아형별 표현형 차이
* 생존 유의 (p < 0.05): KIRC, COAD, PAAD, HNSC (+ ESCA, LUAD)
	- KIRC (p = 0.00063, 최고): cluster2 생존↑ → CD14·Neu↓, CD4↑
	- COAD (p = 0.029): cluster2 생존↑ → CD14↓, CD4·Neu↑
	- PAAD (p = 0.036): cluster1 생존↑ → CD14↓, CD19↑
	- HNSC: cluster3 생존↑ → CD8·CD19↑
* 결론: CD14↓ + CD19↑ = 좋은 생존의 특징
[그림 4A], [보충 그림 S6]
* 병기: CD4↓ ↔ 초기 / CD4↑ ↔ 진행 병기·종양 크기↑
* 일부 아형은 병기·크기와 상관 낮음 (잡음)
[그림 4B] (KIRC·PAAD), [보충 그림 S7]

4.5 아형 간 전사체 분석
* 7세포 모두 DEG > 200개
	- CD19 619개, Neu 448개 (많음) / CD4 214개 (최소)
	- 총 2412 DEG
* 통합 경로 분석: 약물 반응·화학 발암 관련
	- P450 약물 대사, 수용체 활성화, DNA adduct
[그림 5A, B], [보충 그림 S8]
* ICG: 대부분 암종에서 아형 간 유의차, THCA는 적음
* THCA는 ESTIMATE·TIDE 차이가 커서 보완
* ESTIMATE 높음: KIRC 아형1, LUAD 3개 아형
* TIDE 높음: ESCA 아형3, THCA 아형3
* 같은 암 내 차이 + 다른 암 간 유사성 → 분류 신뢰성 지지
[그림 5C TIDE, 5D ESTIMATE, 5E ICG]

###

### 5. Discussion

* 요약: 메틸화 deconvolution → 42아형 → 생존·발현·면역 점수 차이 확인
* CD14·CD19 침윤 분포가 pan-cancer 생존 차이 요인일 가능성
* 기존 연구 대비 개선
	- ① QDMR로 7세포 동시 특이 사이트 선별 (기존: 세포 쌍별 차이 분석, SD 기반)
	- ② 단일 암종 → 14암종 pan-cancer 수준
* 향후: 더 많은 암종·정상 대조군, 더 다양한 면역세포 reference 필요

<grayblock>

- KIRC, HNSC, COAD, PAAD 4개 암종은 암종 내에서 subtype 별로 생존 차이가 많이 났는데 생존이 좋은 subtype에서는 CD14+ 단핵구가 적고 CD19+ B세포 비율이 높았다. CD14+와 CD19+ 세포의 침윤 비율이 환자 생존과 관련 있고 이 두 세포의 분포 차이가 pan-cancer 수준에서 생존을 가르는 요인 중 하나일 수 있다.
- methylation으로만 나눈 subtype 사이에서 ICG, ESTIMATE, TIDE 점수도 유의하게 달랐다. 실제로 존재하는 생물학적 차이다. 
- 특이점은?
  - 1256개 cpg 자리 고를때 표준편차같은 단순한 방법 대신 QDMR(엔트로피)을 사용했다. 
  - 14개 암종을 분석했다.

</grayblock>

###

### 6. 읽으며 체크할 점 (한계·불일치)
* reference가 혈액 유래 7세포뿐 → 대식세포·Treg·종양세포·기질세포 없음
* 아형 수 표기 불일치: 42 vs 62
* HNSC는 그림상 p = 0.052인데 본문은 유의로 서술
* QDMR 원 방법에서는 엔트로피 낮을수록 특이적 → 본문 설명(높을수록 특이)과 반대
* "다섯 병기"라 했지만 그림은 Stage I~IV
* 그림 인용 오류: 개요의 deconvolution은 그림 1B, ICG 결과는 그림 5E가 맞음
* CD4↑ = 진행 병기인데, KIRC·COAD 생존 좋은 군은 CD4↑ → 해석 상충
* 외부 독립 코호트 검증 없음

###

#생각

- 메틸레이션 1256개 피쳐로 특정 암 환자의 cell type 조성을 예측하고 cell type 조성으로 클러스터링 한 다음에 각 클러스터에 대해서 후속분석을 했다.
- 우리 연구는 메틸레이션으로 면역 활발 위치를? 면역 특성이 강한 위치를 병리이미지 위에 볼려는 것이다.
- 메틸화 시그니처를 어떤 면역 반응과 연결하는게 아니라 메틸화 시그니처로 cell type 조성 어노테이션을 한셈이라서 우리 연구랑 방향은 좀 다른것같다.

#출처

논문 Zhou, Yang, et al. "Evaluation of pan-cancer immune heterogeneity based on DNA methylation." Genes 16.2 (2025): 160.