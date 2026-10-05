---
date : 2026-06-15
tags: ['2026-06']
categories: ['maf-ngsreport']
bookHidden: true
title: "MAF Report 비매칭 78건 시각화"
bookComments: true
index: 1
---

# MAF Report 비매칭 78건 시각화

#2026-06-15

---

### 1. 작업 개요

Report의 SNV 1,231개에 대한 기존 결과는
- EXACT_DNA – 692
- EXACT_AA – 348
- REVISED_AA – 11
- ECRF_UNREPORTED – 36
- GENE_UNEXIST – 55
- UNMATCHED – 89

이중 UNMATCHED 89개에 대한 Rule based 매칭 결과는
- 매칭 - 66
- 비매칭 - 23

 

여기서 ECRF_UNREPORTED 36건은 사실상 없는 데이터니까 제외하면, 
- GENE_UNEXIST – 55
- UNMATCHED – 23

총 78건의 데이터에 대해서 2차 매칭을 진행한다. 

###

### 2. 작업 내용

<img width="1280" height="482" alt="image" src="https://github.com/user-attachments/assets/2f59ec09-f4c8-4cbf-b65e-12da942164be" />

먼저 78건 데이터에 대해서 시각화를 해보고 분석 방향을 정할것이다. 시각화는 4가지로 할건데 1) Gene별 unmatched 빈도 2) Sample별 unmatched 빈도 3) Gene별 unmatched 비율 4) Sample별 unmatched 비율 이렇게 보려고 한다.

<img width="1280" height="764" alt="image" src="https://github.com/user-attachments/assets/97360568-889d-48e1-a7b5-83d9d87489b2" />

확인해보면 
- 1)에서 Gene별 unmatched 빈도는 TP53, KRAS, AR, PK3CA, APC가 가장 높고 3)에서 비율은 ABRAXAS1, AXIN2, ARD1A, EIF3E, CNTNAP2, MEN1, SMAD, SMAAD4, SMAD3, PRDM1, RECQL4, PTPRS, PRKDC, HGF, MRE11, FBLN2가  100%로 가장 높다.
- 2)에서 Sample별 unmatched 빈도는 S032-004, S004-037, S006-056이 가장 높고 4)에서 비율은 S002-049, S003-001, S003-061, S003-021, S003-069, S004-037, S024-020, S012-045, S010-090, S012-023, S012-025, S009-015, S032-004, S024-018, S016-033, S024-015가 100%로 가장 높다. 

결과를 보면 빈도가 높은 Gene과 비율이 높은 Gene이 다르고, Sample은 빈도가 높으면 비율도 높은 경향을 보인다. 이를 시각적으로 확인하기 위해서 bubble plot을 그릴건데 크기가 빈도, 색깔이 비율인 플롯을 각각 Gene, Sample에 대해서 그려볼것이다.

<img width="1280" height="1138" alt="image" src="https://github.com/user-attachments/assets/909e6aa5-2315-4353-8010-252d450d750d" />

플롯을 확인해보면?

- Gene 100% 항목 대부분은 전체 등장 횟수(n)가 1~2회로 적다 즉 비율 자체는 높아도 절대 건수는 작다. 
- Sample은 S032-004 (n=15), S004-037 (n=9), S024-020 (n=6) 처럼 등장 횟수가 많은데도 전부 unmatched인 샘플이 있어서 비율과 빈도가 동시에 높으므로 확인이 필요해보인다.

그리고 추가로 Gene 중에 ARD1A, SMAAD4, SMAD처럼 접미사 없는 유전자명은 표준 심볼(NAA10, SMAD4 등)과 표기가 어긋나서 매칭이 안됐을수 있다.  

###

그리고 MAF에서 Gene이 누락된 55건에 대해서만도 플롯을 그려봤다.

<img width="1280" height="764" alt="image" src="https://github.com/user-attachments/assets/8a5e04c6-aa5a-4adc-b20d-9af4e9395f34" />

확인해보면
- 1)에서 Gene별 빈도는 TP53(7), KRAS(7), APC(3), AR(3), 그리고 KMT2C·PRKDC·PIK3CA·ERBB2·SMAD·PRDM1(각 2)이 높고, 3)에서 비율은 ABRAXAS1, ARD1A, HGF, MRE11, SMAD3, RECQL4, SMAAD4, PRDM1, PRKDC, SMAD(총 10개)가 100%로 가장 높다.
- 2)에서 Sample별 빈도는 S032-004(12), S024-020(6), S006-056(6), 그리고 S012-025·S012-023·S010-090·S003-061(각 3)이 높고, 4)에서 비율은 S003-001, S003-021, S003-069, S003-061, S012-025, S012-045, S016-033, S024-020, S012-023, S010-090, S024-015(총 11개)가 100%로 가장 높다.

 <img width="1280" height="1138" alt="image" src="https://github.com/user-attachments/assets/c2d19851-44cc-4b1d-b047-9beaa2814ea1" />

bubble plot을 확인해보면
- S032-004이 12건, S024-020 / S006-056이 각 6건으로 55건 중 24건(약 44%)을 차지한다.
- 100% 유전자 10개 중 7개(ABRAXAS1, ARD1A, HGF, MRE11, SMAD3, RECQL4, SMAAD4)는 비율이 높지만 빈도 1이다. PRDM1·PRKDC·SMAD는 2다.

###

마지막으로 MAF에서 Gene이 존재하는데도 매칭 실패한 23건에 대해서도 그려봤다.

<img width="1280" height="764" alt="image" src="https://github.com/user-attachments/assets/098824e1-0e07-4a5b-af14-640ae8faa474" />

확인해보면
- 1)에서 Gene별 빈도는 EGFR(2), AR(2)만 2건이고 나머지는 모두 1건씩이며, 3)에서 비율은 AXIN2, MEN1, FBLN2, EIF3E, CNTNAP2, PTPRS가 100%로 가장 높다.
- 2)에서 Sample별 빈도는 S004-037(8), S032-004(3), S010-082(2), S005-017(2), S003-904(2)이 높고, 4)에서 비율은 S002-049, S009-015가 100%로 가장 높다.

즉 S004-037이 23건 중 8건(약 35%)을 차지하고 비율도 88.9%로 높다.

<img width="1280" height="1137" alt="image" src="https://github.com/user-attachments/assets/26671cbf-6a98-4e58-af84-7a6c97f9fcb7" />

플롯을 보면
- S004-037에서 8개 변이가 서로 다른 유전자(NOTCH2, LRP1B, FBLN2, POLQ, PIK3CA, CNTNAP2, EIF3E, CSMD3)에 걸쳐 있고 모두 정상적인 c./p. 표기를 갖는데도 매칭이 안됐다.
- 100% 유전자 6개(AXIN2, MEN1, FBLN2, EIF3E, CNTNAP2, PTPRS)는 전부 n=1이라 일반화하기보다 건별로 MAF의 HGVS와 대조해보는게 맞을듯하다.
 
###

### 3. 분석 결과

우선 유전자별 결과를 보면
- TP53, KRAS, APC, AR는 흔한 cancer gene인데 unmatched 빈도가 높다.
- SMAAD4는 SMAD4 / ARD1A는 NAA10 / SMAD는 SMAD4인데 오표기로 보인다.
- 그리고 ABRAXAS1는 FAM175 / MRE11는 MRE11A 처럼 HGNC 심볼이 개정된 유전자도 있다
 

그리고 샘플별 결과를 보면
- S032-004, S004-037, S024-020 -> Total unmatched 건수가 높으면서 비율도 100%
- S032-004, S024-020, S006-056 -> Gene unexist 측면에서 확인 필요해보임
- S004-037, S005-017 -> Manual unmatched 측면에서 확인 필요해보임

그래서 TODO를 생각해보면
1) 심볼 개정 or 오타 Gene을 수정해서 매칭 개선
2) 샘플별 오류가 있는지 확인해서 오류 원인 파악 or 수정 후 매칭 개선

해보면 될것같다.





