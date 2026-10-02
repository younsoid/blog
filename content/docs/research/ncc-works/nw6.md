---
date : 2026-06-05
tags: ['2026-06']
categories: ['kosmos2']
bookHidden: true
title: "HER2 CNV 작업"
bookComments: true
---

# HER2 CNV 작업

#2026-06-05

---

### 1. 분석 개요

KOSMOS-II 데이터를 활용한 연구 중에서 연세암병원에서 진행 중인 HER2 유전자의 CN 정보를 활용하는 연구가 있다. 

<img width="1280" height="392" alt="image" src="https://github.com/user-attachments/assets/98407a27-f349-404d-8b92-5c8afcca45b4" />

KOSMOS-II 데이터에서 CNV의 CN 정보는 위와 같은 구성이고 이중 CN 수치 정보는 CN_CNT, ADJV_CN_CNT 정도이다.

연세암병원 연구는 121명 중 CN_CNT를 가진 환자 48명을 사용해서 분석을 진행했는데 전체 CN 데이터를 요청주셨다. 이에 NGS 데이터가 존재하는 119명의 CNV를 확인해보고 자료를 전달해줘야 한다.

### 2. CNV 정보 확인

<img width="1280" height="605" alt="image" src="https://github.com/user-attachments/assets/ef666054-d028-40e8-a38e-56433177d352" />

우선 119명 중 ERBB2의 CNV 데이터가 존재하는 환자는 83명, 데이터 수는 86개이다.

<img width="1280" height="246" alt="image" src="https://github.com/user-attachments/assets/d19b4ad8-e894-485f-b3c8-01fc3aa94d2b" />

3명의 6개 데이터를 확인해보면 위와 같아서, 중복인 경우 COYO_NO_ATRT_TYPE 컬럼에 값이 있는 행을 사용하였다.

### 3. 패널 정보 확인
 
데이터를 보면 어떤 환자는 CN_CNT 값을 갖고, 어떤 환자는 ADJV_CN_CNT 값을 갖는다. 두 수치를 같다고 봐도 될까? 그리고 동일하게 CN 항목이라 하더라도 기관마다 측정 방법이 모두 같을까? 아닐수도 있다.

그래서 패널 정보도 같이 붙여줬다. BRND_CD 컬럼은 기관별로 사용한 패널에 붙여준 ID값이다.

<img width="1280" height="809" alt="image" src="https://github.com/user-attachments/assets/904b492a-e056-430c-91ae-cde431238e53" />

확인해보면 P016이 제일 많다.

<img width="856" height="424" alt="image" src="https://github.com/user-attachments/assets/cf9bb8f6-cdf3-4f03-b1f8-42cf8710ce42" />

편향을 확인하기 위해서 CN 값의 패널별 box plot을 같이 첨부해서 전달드렸다. 

### 4. 생각

연세암병원에서 Estimated ERBB2 CN>=10과 CN<10으로 나눠서 분석하고 있었는데 CN이 크다의 기준은?
- 보통 CN ≥ 6이면 amplication으로 보고 4~6은 low-level gain, ≥10은 high-level amplification으로 본다.
ADJV_CN_CNT랑 CN_CNT를 통합해서 CN_integrated로 분석했는데 합쳐서 써도 되나?
- ADJV_CN_CNT는 P016에서만 존재하고, 3개 샘플을 제외하면 모두 FCCN_CNT 값도 갖는다.
- P016에서 FCCN_CNT 대비 CN_CNT/ADJV를 확인해보면 좋긴 하겠다.

<img width="758" height="538" alt="image" src="https://github.com/user-attachments/assets/040ded04-8e83-4f46-a58c-32554f978f4a" />

일단 P016만 FCCN_CNT를 갖는다. P016 39개 중에서 39개는 FCCN_CNT를 갖고, 23개는 CN_CNT를 갖고, 13개는 ADJV_CN_CNT를 갖고, 3개는 CNT 값이 없다. 

<img width="648" height="538" alt="image" src="https://github.com/user-attachments/assets/e24187c1-ae22-4779-b873-880eda743ed0" />

23개에 대해서 FCCN_CNT 대비 CN_CNT을 확인하고 13개에 대해서 FCCN_CNT 대비 ADJV를 확인해보면, 시각화는 위와 같고 결과는 아래와 같다.

- CN_CNT/FCCN n=23 median=2.63 IQR=2.28~3.23
- ADJV_CN_CNT/FCCN n=13 median=2.89 IQR=2.73~4.07

P016 내부에서 CN_CNT/FCCN(median 2.63, IQR 2.28–3.23)과 ADJV/FCCN(median 2.89, IQR 2.73–4.07)은 분포가 겹친다. 그래서 두 값을 동일 스케일로 간주해 CN_integrated로 통합해서 분석했을때 큰 문제는 없어보인다.
