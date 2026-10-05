---
date : 2026-06-02
tags: ['2026-06']
categories: ['ngs']
bookHidden: true
title: "NGS Report 표준화"
bookComments: true
---

# NGS Report 표준화

#2026-06-02

---

### 1. NGS Report 추출


```python
import pandas as pd

snv_data_tool = pd.read_excel("/Users/yshmbid/Documents/home/github/kosmos/workspace/data/20260527_Data tool_20260527104012951.xlsx", sheet_name=6, engine="openpyxl")
snv_data_tool = snv_data_tool[snv_data_tool['SUBJ_ID'].str.startswith('S')]
snv_data_tool = snv_data_tool[['SUBJ_ID', 'CRF_REPEATKEY', 'SNV_VRNT_YN', 'BRND_CD_REL_3', 'BRND_NM_VER_REL_3', 'ITEMGROUP_REPEATKEY_1', 'SNV_GENE_CMNT', 'DNA_CHNG', '3_LETR_AA_CHNG', '1_LETR_AA_CHNG', 'VAF', 'TIRE_CD3']]

add_sid_path = "/Users/yshmbid/Documents/home/github/kosmos/workspace/data/0528/add_subj_0529.txt"
with open(add_sid_path, "r", encoding="utf-8") as f:
    add_sid = [line.strip() for line in f if line.strip()]
    
total_sid = list(set(snv_data_tool['SUBJ_ID'].tolist()))

print(len(total_sid), len(add_sid)) # 949 339
```

- data tool: eCRF에 등록된 NGS report 수기추출 데이터 (데이터수 1010 / 등록자 949명)
- 분석 대상자는 339명

```python
reported_sid = [s for s in add_sid if s in total_sid]
etc_sid = [s for s in add_sid if s not in total_sid]
print(len(reported_sid), len(etc_sid)) # 308 31
```

339명 중 Report 수기추출 데이터가 있는 등록자는 308명

```python
snv_data = snv_data_tool[snv_data_tool['SUBJ_ID'].isin(reported_sid)]
snv_data
```

<img width="1280" height="273" alt="image" src="https://github.com/user-attachments/assets/1f19e536-73bf-476f-83c6-6d2a17817119" />

308명에 대해서 1,231개의 SNV 데이터가 존재.

```python
snv_data.to_csv("/Users/yshmbid/Documents/home/github/kosmos/workspace/data/0528/snv_report.csv", index=False)
```

Raw SNV 데이터를 저장.

```python
with open("/Users/yshmbid/Documents/home/github/kosmos/workspace/data/0528/add_report_subj_0529.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(reported_sid))
```

분석 대상 308명의 Subject ID도 txt 파일로 저장.

### 2. NGS Report 표준화

<img width="1280" height="273" alt="image" src="https://github.com/user-attachments/assets/2ec7e14f-a8d1-4f9d-943e-a8d562dcbd17" />

SNV 데이터는 위와 같이 구성되어있고 다음과 같이 표준화한다.
- SNV_GENE_CMNT (유전자 이름) -> Gene
- DNA_CHNG (변이의 DNA 표기) -> dna_change
- 3_LETR_AA_CHNG (변이의 AA 표기: 3-Letter) -> aa3_change
- 1_LETR_AA_CHNG (변이의 AA 표기: 1-Letter) -> aa1_change
- VAF (변이의 VAF 값) -> vaf_pct
- TIRE_CD3 (변이의 Tier 정보) -> Tier

<img width="1008" height="182" alt="image" src="https://github.com/user-attachments/assets/997ff6ee-684b-4da7-9af4-337264138f6e" />

- snv_std_1.py를 실행하면 입력 파일은 위에서 생성한 snv_report.csv이고, 결과 파일은 snv_standardized.csv로 저장된다.
- 표준화 결과 1,217개 변이는 Rule-based로 잘 표준화되었고
- 14개가 예외처리 되었는데 AA 1-Letter 표기 오류 8건, DNA 자리에 AA 표기로 의심 5건, DNA 표기 오류 1건이 나왔다.

<img width="1280" height="222" alt="image" src="https://github.com/user-attachments/assets/c58ca50b-db39-42e3-ab4c-2e0120ba16e9" />

check 컬럼에서 오류 내역을 확인 후, manual review해서 저장했다. 
