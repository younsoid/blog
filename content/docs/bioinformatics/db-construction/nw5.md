---
date : 2026-06-05
tags: ['2026-06']
categories: ['maf', 'ngsreport']
bookHidden: true
title: "MAF Report 매칭 결과"
bookComments: true
index: 1
---

# MAF Report 매칭 결과

#2026-06-05

---

### 1. 작업 개요

MAF 파일과 NGS report 매칭 결과를 확인했다.

<img width="1280" height="331" alt="image" src="https://github.com/user-attachments/assets/39448d64-1101-4fdf-879a-ea974581c7aa" />
<img width="1280" height="302" alt="image" src="https://github.com/user-attachments/assets/dda1424e-d0b5-48d8-bc47-3b5ca61a60e1" />

1,231개 SNV에 대해서 라벨링 결과
- MAF와 매칭되는 건이 1,040건 (692 + 348)
- AA 표기 수정 시 매칭되는 건이 34건
- eCRF 상에 Gene이나 Position 정보가 없는 건이 36건
- MAF에 해당 Gene이 없는 건이 55건
- 그 외 비매칭이 66건이었다.

각 라벨별로 해석 및 이후 분석 방향은
- AA 표기 수정 시 매칭되는 34건: 표기 수정 내역을 확인하고 적합하지 않을 시 비매칭으로 수정
- eCRF 상에 Gene이나 Position 정보가 없는 36건: Null로 두기
- MAF에 해당 Gene이 없는 55건: Report의 정보를 MAF에 입혀야 함
- 그 외 비매칭: manual curation으로 매칭시키기

이렇게 진행한다.

### 2. AA 표기 수정 확인

위 데이터는 REVISED_AA에 해당하는 34건만 남긴 것이다. AA 표기 수정 시, check_02 컬럼에 다음과 같이 내역을 작성하도록 코드를 만들었었다

- Transcript isoform offset: STD aa1='p.G624R' matches MAF HGVSp_Short='p.G640R' (same Gly>Arg substitution, position offset of 16 residues likely due to alternative transcript) / STD VAF = '4.40%' and MAF VAF = '4.40%'

위 비고의 의미는 Report 상의 aa1 표기인 p.G624R가 MAF의 HGVSp_Short 표기인 p.G640R와 매칭될 수 있으며, residues 차이는 16 / VAF는 Report와 MAF 모두 4.40%라는 의미이다. 
 
어떤 경우를 동일하다고 확정지을까 고민하다가 
- MAF-Report 사이 Residue 차이 20 이하 (ex. P.G624R and p.G640R)
- MAF-Report 사이 VAF 차이 1% 이하 (* MAF에서 VAF 계산: t_alt_count / t_depth × 100)

인 경우는 동일한 SNV로 보고 MATCHED 처리하였다. 

<img width="1280" height="486" alt="image" src="https://github.com/user-attachments/assets/706e2f55-be6b-4155-b68d-1ebf462e2b1e" />

위 기준에 따라 34건 중 23건의 SNV 데이터가 UNMATCHED로 변경되었다.

### 3. UNMATCHED 확인

<img width="1080" height="208" alt="image" src="https://github.com/user-attachments/assets/101c4f4e-4810-4bec-a278-7f7b8a0ca7e8" />

최종 매칭 결과는 위와 같았다.

<img width="1260" height="838" alt="image" src="https://github.com/user-attachments/assets/b8899c87-1602-4ad1-8e4a-984fdd0237b3" />

UNMATCHED 89건을 Sample 별, Gene 별로 분포를 확인해봤을때

- S004-037, S010-082가 각각 8, 6번 unmatched로 가장 높았고
- TERT, TP53, APC가 각각 14, 8, 6번 unmatched로 가장 높았다.

<img width="984" height="440" alt="image" src="https://github.com/user-attachments/assets/25cd7c45-2998-401f-abea-26cb526dece0" />

UNMATCHED 89건에 대해서 MAF와 Report를 Manual 비교해주어야 하는데 다음과 같이 로직을 생각중이다.
1. snv_standardized_final_manual-curated.csv를 cur_res 데이터프레임으로 읽었을때 match_method 컬럼의 값이 UNMATCHED인 행에 대해서만 다음 작업을 수행
2. ID와 Gene 컬럼의 값을 각각 cur_id, cur_gene으로 받고 vaf_pct 컬럼의 값을 cur_vaf로 받기. 그리고 snv_maf.csv 에서 ID 컬럼의 값이 cur_id 이면서 Hugo_Symbol 컬럼의 값이 cur_gene인 행만 남겨서 cur_maf로 받기 이때 cur_maf로 받을때 index는 유지하기.
3. cur_maf 데이터프레임의 각 행에 대해서, t_alt_count / t_depth × 100 값이 cur_maf_vaf라고 볼 수 있음. cur_vaf와 cur_maf_vaf가 1 이하로 차이나는지 확인하기. 1 이하로 차이나는 경우, cur_res 데이터프레임에 UNMATCHED_VAF_MAPPING 컬럼을 생성해서 YES 할당. 매핑 case가 여러 개여도 YES 할당. 매핑 case가 없는 경우 즉 1 초과로 차이나는 경우 NO 할당.
4. 매핑 case가 여러개이거나 매핑 case가 없을 경우, check_03 컬럼에 매칭 후보로 유력한 MAF의 index 정보를 기재하고, 그 이유를 작성하기. 이때 작성 형식은 통일 (매칭 이유의 유형을 쓰고, 상세 사유를 쓰기) 이때 가능하다면 최대 3개의 후보까지 작성. 

그리고 작성 전에 snv_maf.csv에 중복 행이 있어서 그거 제거하고 작업해야 할듯하다. 
 
