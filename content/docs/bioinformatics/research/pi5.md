---
date : 2026-10-06
tags: ['2026-10']
categories: ['연구']
bookHidden: true
title: "일단 짜본 파이프라인"
bookComments: true
index: 1
---

# 일단 짜본 파이프라인

#2026-10-06

---

### 1. 데이터·코호트

* 대상: TCGA-BRCA 단일 암종 (계획서의 다암종·한국인 데이터는 아직 미포함)
* WSI: GDC Open Access, FFPE 진단 슬라이드(-DX)만 사용, 냉동 슬라이드(TS/BS) 제외
	- GDC 검색 결과 BRCA DX 1,133장 (원본 합계 약 1,079 GB)
	- 처리 순서: 파일 용량 작은 순
	- 1.0 처리 완료 960장 / 환자 910명 (일부 환자는 DX 2장 이상)
	- 2.5 처리 6장 (MAX_SLIDES = 10으로 시작, 배치 중단)
* 라벨 1: Thorsson 2018 mmc2.xlsx (PanImmune_MS, 11,080명 × 64열)
	- Immune Subtype C1–C6: 전체 9,126명 / BRCA 1,083명
	- BRCA 분포: C1 369 / C2 391 / C3 191 / C4 92 / C6 40 (C5 없음)
	- 연속형 점수 7종: LF, SF, LISS, IFN-γ, TGF-β, TIL RF, Prolif
	- BRCA n: LF 1,070 / SF 1,023 / LISS·IFN-γ·TGF-β·Prolif 1,083 / TIL RF 944
* 라벨 2: GDC RNA-seq STAR-Counts (Primary Tumor), 시험 20명
	- ESTIMATE 유전자 세트: Yoshihara 2013 Suppl. Data 1 (Stromal 141 / Immune 141)
* 라벨 3: GDC DNA methylation beta value (450K/EPIC, Primary Tumor)
	- WSI 처리 환자 910명 중 642명 파일 확보
* 매칭 키: TCGA barcode 앞 3필드 (환자 단위, TCGA-XX-XXXX)
* 실행 환경: Windows PC, RTX 3060 12GB
	- 1.0: Python 3.14 venv, torch 2.14 + CUDA 12.6, OpenSlide 4.0.1
	- 2.5: 별도 환경(exaonepath25), Python 3.12, transformers

###

### 2. 전처리

* 1.0 (직접 구현)
	- 조직 mask: 최대 2,000px 썸네일에서 밝기 < 220 & 채도 > 0.05
	- 타일: level 0에서 256×256 px 격자, step 256 (겹침 없음)
	- 1차 필터: mask 기준 타일 내 조직 비율 ≥ 50%
	- 2차 필터(실제 픽셀): OpenSlide 빨간 배경(R>150, G·B<60) > 30%면 제거, 조직 픽셀 < 50%면 제거
	- 배율·MPP 정규화 없음 → 20×와 40× 슬라이드의 타일 실제 면적이 다름
	- 염색 정규화: Macenko (EXAONEPath 저장소 macenko_target), 실패 타일은 제외
	- 입력 변환: Resize 256 (bicubic) → CenterCrop 224 → ImageNet mean/std 정규화
	- 타일 PNG 저장 없이 메모리에서 바로 임베딩, 처리 후 원본 .svs 삭제, 중단 시 재개 가능
	- 시험 단계: 슬라이드 1장, 후보 3,266개 중 300개 균등 샘플 → 품질 통과 106개
* 2.5 (내장 patchfy)
	- 조직 분할 + 좌표 추출 자동
	- MPP 기준 크기 보정: 0.5 µm/px 기준 256px, 예) 0.2457 MPP 슬라이드는 520px로 잘라 같은 면적
	- MPP 정보가 없으면 0.5로 가정

###

### 3. 특징 추출

* 1.0: EXAONEPath 1.0 ViT → 타일당 768차원, 배치 32
	- 출력: 슬라이드별 h5 (features N×768, coords N×2)
* 1.0 슬라이드 요약: 학습 없는 pooling 4종
	- mean (768) / max (768) / mean_std (평균+표준편차, 1536)
	- attention (768): 평균 벡터와의 내적을 softmax 가중치로 사용 → 평균에 가까운 타일 강조, 학습형 attention 아님
	- 출력: brca_slide_level.h5 (960 × 차원)
* 2.5: patch feature 768차원 → slide encoder(component = "slide") → slide_embedding 1536차원
	- 입력: patch features, mask(전부 유효), coords, contour_index
	- multi-omics 정렬로 학습된 genomics-aligned 표현
	- 출력: brca_slide_level_25.h5 (pooled/encoder25, 05와 같은 구조)
* UMAP: 타일 지도(NB 03), 슬라이드 지도(NB 05), 라벨 색칠 없음

###

### 4. 라벨 생성
* Immune subtype·연속형 점수: mmc2 값을 그대로 사용 (06, 07a)
* ESTIMATE 재현 (07b)
	- STAR-Counts tpm_unstranded → 유전자×환자 행렬 (중복 유전자명은 최대 TPM)
	- gseapy ssGSEA (sample_norm = rank), NES를 점수로 사용
	- 검증: ImmuneSignature vs mmc2 LF, Pearson r
	- 계산한 점수를 WSI 예측에 쓰는 단계는 미구현
* Methylation-defined immune state (08a)
	- QC: 결측 ≥ 20% probe 제거, 남은 결측은 probe 평균으로 대체
	- 분산 상위 5,000 probe → 표준화 → KMeans (k = 3, n_init 10, seed 42)
	- 클러스터별 평균 LF 최고 = immune-rich, 최저 = immune-depleted, 나머지 = intermediate
	- 라벨은 환자 개인 LF가 아니라 소속 클러스터로 결정
	- 계획서의 consensus clustering, pseudotime, 비특이·성염색체 probe 필터, promoter/gene-level 요약은 미구현

###

### 5. 예측 모델
* 공통: 슬라이드 벡터 → StandardScaler → 선형 모델 (pipeline 안에서 scaler 학습 → fold 간 정규화 누수 없음)
* 분류 (06, 08b, 09): LogisticRegression (max_iter 1000, class_weight balanced)
	- 06: 5-class (C1·C2·C3·C4·C6), 3명 미만 클래스 제외
	- 08b: immune-rich vs immune-depleted 이진 (intermediate 제외)
* 회귀 (07a): Ridge (α = 10 고정)
* 09 단계적 비교 (타깃: 08a immune_binary, WSI: 1.0 mean_std)
	- ① WSI only (1536)
	- ② WSI + methylation 클러스터 one-hot (1539)
	- ③ WSI + mmc2 점수 5종 LF·SF·LISS·IFN-γ·TGF-β (1541)
	- ④ WSI + ② + ③ (1544)
	- 모든 데이터가 있는 공통 환자만 사용
* 하이퍼파라미터 최적화 안 함
* 2.5 버전 (06_25 ~ 09_25): 슬라이드 벡터 경로와 pooling 이름(encoder25)만 다르고 로직 동일

###

### 6. 학습·검증 설계
* 5-fold CV, shuffle, random_state 42
	- 분류: StratifiedKFold / 회귀: KFold
	- 06·07a·08b는 슬라이드 단위 분할 → 같은 환자의 슬라이드가 train과 test에 동시에 들어갈 수 있음
	- 09는 환자당 슬라이드 1장 (dict에 마지막으로 들어간 슬라이드)
* site-aware split, 외부 검증, 암종 간 hold-out 없음
* 지표 계산: 분류는 fold별 계산 후 평균, 회귀는 out-of-fold 예측 전체로 계산

###

### 7. 평가

* 분류: accuracy, macro-F1, AUROC (이진만), fold 표준편차 (06)
* 회귀: Pearson r, Spearman ρ, R² (out-of-fold)
* ESTIMATE 일치도: Pearson r
* 통계 검정(DeLong 등), 신뢰구간, calibration, sensitivity/specificity 없음
* 시각화: 07a 최고 점수 산점도, 09 AUROC 막대그래프

### 8. 코호트·처리 현황

* GDC BRCA DX 1,133장 중 1.0으로 960장 처리 (84.7%), 환자 910명
	- 1장 수동 제외 (TCGA-AN-A0AM-DX1, 처리 느림)
	- 다운로드 일시 오류(ChunkedEncodingError)는 재시도로 복구
* 슬라이드당 타일 수: 최소 26 / 최대 89,245 / 평균 27,450
* 2.5: slide embedding 6장 (1536차원), 배치 중단 상태
	- patchfy MPP 로그: OL 슬라이드 0.5 (가정값), AC 슬라이드 0.2457·0.252 (≈40×)
	- → 1.0 파이프라인에 배율이 섞여 있음을 확인
	- 2.5 분석 노트북(06_25 ~ 09_25) 미실행 → 1.0 vs 2.5 비교 결과 없음
* 라벨 매칭
	- subtype: 947 / 960 슬라이드
	- methylation: 642 / 910 환자 (70.5%)
	- 09 공통 환자: 334명

###

### 9. Immune subtype 예측 (WSI 단독, 5-class)
* n = 947 슬라이드: C1 307 / C2 343 / C3 172 / C4 85 / C6 40
* pooling별 (acc / macro-F1)
	- mean_std 0.434 ± 0.028 / 0.333 ± 0.028 (최고)
	- mean 0.422 / 0.330
	- max 0.389 / 0.285
	- attention 0.382 / 0.293
* 기준선: 최빈 클래스(C2) 비율 0.362, 5-class 무작위 F1 ≈ 0.20
	- 무작위보다는 높지만 아형 구분력은 제한적

###

### 10. 연속형 immune score 회귀 (WSI 단독)
* 점수별 최고 Pearson r (out-of-fold)
	- Prolif 0.491 (mean, Spearman 0.523)
	- TIL RF 0.477 (mean) / 0.471 (mean_std, R² −0.011)
	- LF 0.435 (mean_std)
	- LISS 0.414 (mean)
	- TGF-β 0.412 (mean_std)
	- SF 0.337 (mean_std)
	- IFN-γ 0.200 (mean), 가장 낮음
* pooling 비교: mean·mean_std가 7/7에서 상위 2개, max가 6/7에서 최하 (SF는 attention이 최하)
* R²는 모든 조합에서 음수 (−0.011 ~ −1.806)
	- 순위(상관)는 어느 정도 맞추지만 값의 크기는 평균값으로 찍는 것보다 오차가 큼
	- Ridge α = 10이 768·1536차원에 비해 규제가 약해 과적합했을 가능성
* 해석: 이미지 유래 지표(TIL RF)와 증식 지표가 상위, 전사체 신호(IFN-γ)는 형태로 잘 드러나지 않음

###

### 11. ESTIMATE 재현 (RNA-seq 직접 계산)
* RNA 확보 20 / 20명, 발현 행렬 59,427 유전자 × 20명
* ImmuneSignature (ssGSEA NES) vs mmc2 LF: r = 0.664 (n = 19)
	- 직접 계산 파이프라인이 기존 값과 같은 방향
	- n이 작아 신뢰구간이 넓음 (당시 처리된 환자 75명 중 앞 20명)

###

### 12. Methylation cluster와 immune 라벨
* 642명 × 421,716 probe → QC 후 402,961 → 분산 상위 5,000
* KMeans k = 3: cluster 0 212명 / cluster 1 276명 / cluster 2 154명
* 클러스터별 평균 LF: 0 = 0.168 / 1 = 0.214 / 2 = 0.338
	- immune-rich = cluster 2 (154명), immune-depleted = cluster 0 (212명), intermediate = cluster 1 (276명)
	- rich와 depleted의 LF 차이 약 2배
	- 통계 검정, 아형(PAM50/ER)·purity와의 관계는 확인 안 함

###

### 13. WSI로 methylation-defined immune state 예측
* n = 383 슬라이드 (rich 163 / depleted 220), 환자 366명 → 17명은 슬라이드 2장
* pooling별 (acc / F1 / AUROC)
	- mean_std 0.783 / 0.775 / 0.858 (최고)
	- mean 0.765 / 0.755 / 0.832
	- attention 0.741 / 0.732 / 0.819
	- max 0.739 / 0.732 / 0.813
* 계획서 핵심 가설("H&E로 methylation-defined immune state 예측")을 예비적으로 지지
	- 단, 클러스터가 면역 외 축(아형·purity)을 반영할 가능성은 미검증
	- 환자 중복 17명은 누수 가능성이 있지만 규모는 작음

###

### 14. WSI 단독 vs WSI + omics
* n = 334 환자 (rich 135 / depleted 199), WSI = mean_std
	- ① WSI only: acc 0.770 / F1 0.760 / AUROC 0.841
	- ② + methylation: 0.919 / 0.916 / 0.967
	- ③ + score: 0.782 / 0.772 / 0.862
	- ④ + multi-omics: 0.922 / 0.918 / 0.971
* 해석 주의
	- ②·④의 큰 상승은 순환 구조: 타깃이 methylation 클러스터 번호로 정의되는데, 그 클러스터를 입력으로 넣음
	- one-hot 3개만 더해도 AUROC +0.126 → 선형 모델이 정답 정보를 그대로 사용
	- ③의 상승(+0.021 AUROC)도 라벨 정의에 쓰인 LF가 입력에 포함되어 부분적으로 순환
	- → 현재 결과로는 "omics 추가가 독립 정보를 더한다"고 결론 내리기 어려움
	- ① 결과(AUROC 0.841)는 4.6과 일관됨

###

### 15. 한계·다음 단계

5.1 현재 주장할 수 있는 것
* BRCA 약 950장 규모에서 EXAONEPath 1.0 embedding으로 H&E만 보고 면역 관련 지표를 중간 수준 상관으로 예측함 (r 0.4–0.5)
	- 형태와 직결된 지표일수록 잘 맞음: Prolif r ≈ 0.49, TIL RF r ≈ 0.48
	- TIL RF는 원래 H&E에서 계산된 지표 → 잘 맞는다는 것 자체가 파이프라인 정상 동작의 근거
	- 분자 신호 성격이 강한 지표는 약함: IFN-γ r ≈ 0.20
* DNA methylation 클러스터는 면역 침윤 수준과 연관됨
	- 평균 LF 0.17 (cluster 0) vs 0.34 (cluster 2), 약 2배
	- EOBC 선행연구의 관찰과 같은 방향
* methylation 기반 rich/depleted 상태를 WSI만으로 AUROC 약 0.84–0.86으로 구분함
	- 08b 0.858 (슬라이드 단위), 09 WSI only 0.841 (환자당 1장)
	- 09 WSI only는 환자 중복이 없어 더 깨끗한 추정치이고, 08b와 거의 같음
* RNA-seq 직접 계산(ssGSEA)이 mmc2 LF와 같은 방향 (r = 0.664)
	- 서로 다른 오믹스(RNA vs methylation 유래 LF) 간 일치 → 다운로드·TPM·ssGSEA 계산 정상
* 위 결과들은 씨앗형 과제의 예비 결과로 의미가 있음

5.2 아직 주장할 수 없는 것
* "multi-omics를 더하면 예측이 좋아진다"
	- 09의 순환 구조 때문에 현재 결과로 뒷받침되지 않음
* "모델이 면역을 보고 맞힌다"
	- 아형(ER/basal)·등급·종양 순도 같은 다른 축을 대신 보고 있을 가능성을 배제하지 못함
* "2.5가 1.0보다 낫다"
	- 2.5는 6장 안팎만 처리, 06_25 ~ 09_25 실행 기록 없음 → 비교 데이터 없음
* 다암종·한국인 데이터로의 일반화
	- TCGA-BRCA 단일 코호트, 외부 검증 없음

5.3 결과별 한계
* 06 Immune subtype
	- 최고 macro-F1 0.333: 무작위(≈ 0.20)보다는 높지만 다섯 아형 구분에는 약함
	- C1(wound healing)과 C2(IFN-γ dominant)는 형태만으로 구분이 어려울 것으로 보임
* 07a 회귀
	- R²가 모든 조합에서 음수 (예: LF −0.18, TIL RF는 mean_std에서 −0.011)
	- 순서(순위 상관)는 맞히지만 예측값 스케일이 과하게 흔들림 → "평균으로 찍기"보다 오차가 큼
	- 원인 추정: 768–1536차원, 표본 약 900개에 Ridge α = 10 고정 → 규제 부족
	- 현재는 "순위 상관은 있으나 보정(calibration)되지 않은 예측"으로 보고하는 것이 정확함
* 07b ESTIMATE 재현
	- n = 19 → r = 0.664의 95% CI가 대략 0.3–0.86으로 넓음
	- 04 초반(처리 환자 75명) 시점에 실행 → 전체 환자로 재실행 필요
	- 계산한 점수를 WSI로 예측하는 단계는 미실행
* 08a methylation 클러스터
	- 평균만 확인: 클러스터 내 LF 분포 겹침(박스플롯), 통계 검정 없음
	- 유방암에서 분산 상위 probe의 비지도 클러스터링은 흔히 ER/basal 여부나 종양 순도를 따라 갈림
	- → cluster 2가 "면역이 풍부한 그룹"인지, "면역도 함께 높은 basal 성향 그룹"인지 아직 구분 안 됨
	- Thorsson LF 자체가 methylation 추정치 → methylation 클러스터를 methylation 유래 지표로 이름 붙인 구조
* 08b WSI → methylation immune state
	- 이진 분류(AUROC 0.86)가 연속형 회귀(LF r ≈ 0.44)보다 훨씬 좋음
	- 설명 후보 1: intermediate(276명)를 빼고 양 극단만 남겨 문제가 쉬워짐
	- 설명 후보 2: 클러스터가 면역보다 형태적으로 더 뚜렷한 축(아형·등급)을 반영
	- → "모델이 무엇을 보고 맞히는가"를 확인해야 한다는 신호
	- 환자 중복: 환자 366명, 슬라이드 383장 → 같은 환자 슬라이드가 train·test에 나뉘었을 수 있어 약간 낙관적일 수 있음
	- 클러스터 정의(642명 전체, 비지도)는 CV 밖에서 수행 → 큰 누수는 아니지만 다른 코호트·암종에서는 미검증
* 09 WSI vs WSI + omics
	- WSI + methylation (AUROC 0.967): 정답(rich = cluster 2, depleted = cluster 0)이 입력 one-hot에 그대로 들어 있음
	- 원리상 1.0이어야 하나 1536개 WSI 차원과 함께 L2 규제를 받아 0.967에 그침
	- WSI + score (0.841 → 0.862): 라벨 정의에 쓴 LF가 입력에 포함 → 정답 일부를 넣어준 효과
	- → ②③④는 현재 형태로 해석하면 안 됨, ①만 신뢰 가능
* 전처리
	- 1.0은 배율과 무관하게 level 0의 256px 사용 → 20×·40× 슬라이드 타일의 실제 면적이 다름
	- 2.5 patchfy는 MPP를 읽어 patch 크기 조정 (예: MPP 0.25 → 520px) → 2.5 전환은 모델 교체이면서 배율 불일치 해결
	- "attention" pooling은 평균과 비슷한 타일에 가중 → mean보다도 낮아 실질 이득 없음
* 평가 체계
	- 신뢰구간, DeLong 검정, calibration, sensitivity/specificity 없음
	- 하이퍼파라미터 튜닝 없음

5.4 후속 작업 (우선순위 순)
* 1) 08a 클러스터 × BRCA 분자아형 교차표 (가장 중요)
	- mmc2의 TCGA Subtype 열 또는 PAM50 사용
	- cluster 2가 basal에 몰려 있는지 확인
	- 이 결과에 따라 AUROC 0.86을 어떤 문장으로 보고할지 결정됨
* 2) 아형 보정 분석
	- 예: luminal 환자만으로 08b 재실행 → AUROC 유지 여부 확인
	- 클러스터 내 LF 박스플롯 + 통계 검정 추가
* 3) 교차검증을 환자 단위 GroupKFold로 교체 (06, 07a, 08b)
* 4) 09의 omics feature를 라벨과 독립적인 것으로 교체
	- 후보: 07b RNA 점수(전체 환자 재계산), methylation PCA 성분
	- 라벨을 만든 클러스터 one-hot과 LF는 입력에서 제외
* 5) 07a: RidgeCV로 α 튜닝 → R² 재확인
* 6) 04_25를 1.0과 같은 슬라이드 집합으로 완주 → 06_25 ~ 09_25 실행 → 1.0 vs 2.5 비교
* 7) 평가 보강: bootstrap 신뢰구간, DeLong 검정, calibration, sensitivity/specificity
* 8) 계획서 범위 확장: 다암종, 한국인 데이터, protein/RPPA, methylation pseudotime, 학습형 attention MIL과 heatmap, 암종 간 hold-out


