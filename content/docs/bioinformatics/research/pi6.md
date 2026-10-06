---
date : 2026-10-05
tags: ['2026-10']
categories: ['연구']
bookHidden: true
title: "데이터와 method"
bookComments: true
index: 3
---

# 데이터와 method

#2026-10-05

---

1. 대상: TCGA-BRCA (유방암)

2. WSI: GDC Open Access, FFPE 진단 슬라이드(-DX)만 사용, 냉동 슬라이드(TS/BS) 제외
	- GDC 검색 결과 BRCA DX 1,133장 (원본 합계 약 1,079 GB)
	- 처리 순서: 파일 용량 작은 순
	- 1.0 처리 완료 960장 / 환자 910명 (일부 환자는 DX 2장 이상)

<grayblock>

- 병리 슬라이드에는 Frozen과 FFPE 2가지가 있는데 FFPE가 진단용이다. Frozen은 냉동이어서 조직모양이 찌그러지기 쉽고 FFPE는 형태가 비교적 보존되기때문에 FFPE를 쓴다.
-   유방암 진단용 슬라이드는 1,133장인데 그중에 960장을 받았고 910명 대상자였다.

</grayblock>

3. 라벨 1: Thorsson 2018 mmc2.xlsx (PanImmune_MS, 11,080명 × 64열)
	- Immune Subtype C1–C6: 전체 9,126명 / BRCA 1,083명
	- BRCA 분포: C1 369 / C2 391 / C3 191 / C4 92 / C6 40 (C5 없음)
	- 연속형 점수 7종: LF, SF, LISS, IFN-γ, TGF-β, TIL RF, Prolif
	- BRCA n: LF 1,070 / SF 1,023 / LISS·IFN-γ·TGF-β·Prolif 1,083 / TIL RF 944

4. 라벨 ②: GDC RNA-seq STAR-Counts (Primary Tumor), 시험 20명
	- ESTIMATE 유전자 세트: Yoshihara 2013 Suppl. Data 1 (Stromal 141 / Immune 141)

5. 라벨 ③: GDC DNA methylation beta value (450K/EPIC, Primary Tumor)
	- WSI 처리 환자 910명 중 642명 파일 확보

<grayblock>

- 면역 상태 지표로 3가지를 사용
- Thorsson 6개 라벨
  - TCGA 데이터 기반으로 종양 주변 면역 환경을 6가지(C1~C6)로 분류
  - 유방암 환자 1,083명에 라벨링되어있음
  - 면역환경 라벨 외에도 면역 환경 관련 다양한 지표가 있음
- ESTIMATE 점수
  - 면역세포 특이적 유전자 141개와 간질세포 특이적 유전자 141개의 발현량을 기반으로 매긴 면역 점수
- DNA 메틸화 데이터
  - 910명 중 642명에게 메틸레이션 데이터 존재

</grayblock>

6. 매칭 키: TCGA barcode 앞 3필드 (환자 단위, TCGA-XX-XXXX)

7. 실행 환경: Windows PC, RTX 3060 12GB
	- 1.0: Python 3.14 venv, torch 2.14 + CUDA 12.6, OpenSlide 4.0.1
	- 2.5: 별도 환경(exaonepath25), Python 3.12, transformers

<grayblock>

- 작업환경
  - 1.0: python 3.14 / PyTorch, OpenSlide
  - 2.5: python 3.12 / transformers library

</grayblock>
