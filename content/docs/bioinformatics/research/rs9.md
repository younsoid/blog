---
date : 2026-10-19
tags: ['2026-10']
categories: ['연구']
bookHidden: true
title: "WSI 전처리 결과"
bookComments: true
index: 6
---

# WSI 전처리 결과

#2026-10-19

---

### 1. WSI 다운로드

GDC 서버에서 이미지 svs 파일을 받는다. 

저장은 `C:\Users\Admin\EXAONEPath_data\v3\luad\svs\TCGA-64-5779-01Z-00-DX1.{uuid}.svs`로 저장한다. 

### 2. 입력

`C:\Users\Admin\EXAONEPath_data\v3\luad\svs\TCGA-64-5779-01Z-00-DX1.{uuid}.svs` 이미지의 헤더에 MPP 정보가 있다.

### 3. MPP 정규화

원본 WSI를 128 µm 크기 타일로 자르려면 원본에서 몇 픽셀 정사각형을 읽어야 하는지가 슬라이드마다 다르다. 슬라이드마다 MPP 정보로부터 `mpp0`을 추출하고 슬라이드마다 읽어야하는 픽셀 수를 `256 × 0.5 ÷ mpp0`으로 계산해둔다.

<img width="981" height="282" alt="image" src="https://github.com/user-attachments/assets/c01179a8-0272-4871-afda-ca936ee644df" />

5개만 확인해보면 S1, S2, S4, S5는 0.25 µm/px에 40x이고, S3는 0.5 µm/px에 20x이다. 다운샘플은 뭐냐면 svs 파일에는 한 슬라이드의 원본, 4배 축소, 16배 축소 이렇게 여러 층을 저장한다고 한다.

레벨 0 크기에 MPP를 곱하면 슬라이드가 스캔한 영역의 실제 크기가 나온다.
- S1은 97105×95566px -> 실제 크기 24×24 mm (정사각형)
- S2는 48921×85758px -> 실제 크기 12×22 mm	(세로로 길다)
- S3는 27984×24154px -> 실제 크기 14×12 mm (정사각형에 가깝다)
- S4는 47962×31231px -> 실제 크기 12×8 mm (5장 중 제일 작다)
- S5는 118946×86337px -> 실제 크기 30×22 mm (5장 중 제일 크다)

뒤에서 슬라이드를 타일로 자를때 128 µm 크기로 자른다. 이때 40x는 약 508px(`타일 1장 = 레벨0 px` 컬럼의 값)을 읽어 256px로 줄임으로써 256px이면서 128 µm인 타일로, 20x는 약 255.7px(`타일 1장 = 레벨0 px` 컬럼의 값) 읽어 마찬가지로 256픽셀이면서 128 µm인 타일로 자른다.

궁극적으로는 슬라이드마다 256픽셀이면서 128 µm(0.5 µm/px 해상도)인 타일들이 n개씩 생기는 것이다.

### 4. 조직 mask

슬라이드를 128 µm 크기 타일로 자르고, 모든 타일을 분석에 사용하는것은 아니다. 조직이 존재하는 타일만 쓴다.

조직이 있는 타일을 고르기 위해서 슬라이드를 2000px로 줄이고 (일종의 다운샘플) 조직 mask를 수행한다.

### 4-1. 조직 있는 타일 고르기

<img width="987" height="381" alt="image" src="https://github.com/user-attachments/assets/753a8445-55a1-4aac-aefc-c02e8137eda4" />

여기서 `썸네일 1px (µm)` 컬럼은 썸네일의 1px가 실제로 몇 µm인지 이다. (여기에 mpp0을 곱하면 원래 크기가 나오는 셈이다) `sx` 컬럼의 값은 2000px로 줄이기 위해 몇배 축소했는지이다.

<img width="979" height="567" alt="image" src="https://github.com/user-attachments/assets/dbcb7bc0-dda2-438f-84d8-178f45b7ff8a" />

조직이 있는 타일인지 아닌지를 고르는데 5가지 단계를 거친다.
1. RGB 평균이 220< 인지 (배경 제거)
2. HSV 채도가 >0.05 인지 (채도 필터링)
3. 반경 40 µm 원판으로 팽창 후 침식
4. 40,000 µm² 미만의 연결 덩어리 삭제
5. 40,000 µm² 미만의 빈 구멍 채우기

위 5단계의 mask 결과를 S1-S5에 대해서 뽑아보면 아래와 같다.

<img width="1990" height="1767" alt="s2_mask_steps" src="https://github.com/user-attachments/assets/4c03dc98-f3d9-4cab-bc88-fa8a99bc13a8" />

3~5단계가 필요한건지는 확인이 필요해보인다.

그리고 다음으로 mask 기준으로 조직이 절반 이상인 칸만 남긴다. 

<img width="783" height="215" alt="image" src="https://github.com/user-attachments/assets/93ad9136-d426-40ec-b5c3-6cf037573d19" />

S1만 확인해보면 35,530개 타일 가운데 17,173개 타일이 조직이 존재하고 50% 미만인 경우를 제거하고나면 16,308개가 남았다. 
