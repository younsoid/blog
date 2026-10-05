---
date : 2026-06-02
tags: ['2026-06']
categories: ['maf', 'ngsreport']
bookHidden: true
title: "MAF 표준화"
bookComments: true
index: 1
---

# MAF 표준화

#2026-06-02

---

### 1. MAF 파일 목록 확인

```python
import os

os.getcwd() # 'C:\\Users\\User\\Documents\\yshid\\2605\\bin'

all_files = os.listdir(r"\\10.32.91.11\core\03. [로슈]정밀 의료 생태계 구축 사업\03-1. MAF(VCF)\최종 확인 MAF")
maf_files = [f for f in all_files if f.lower().endswith(".maf")]
len(maf_files) # 928

with open(r"C:\Users\User\Documents\yshid\2605\data\maf_0528.txt", "w", encoding="utf-8") as f:
	f.write("\n".join(maf_files))
```

928개 MAF 파일명을 txt 파일로 저장.

### 2. 신규 등록자 확인

```python
import pandas as pd

data_tool = pd.read_excel("/Users/yshmbid/Documents/home/github/kosmos/workspace/data/0528/20260528_Data tool_20260528140729014.xlsx")
data_tool_01 = pd.read_excel("/Users/yshmbid/Documents/home/github/kosmos/workspace/data/20260527_Data tool_20260527104012951.xlsx")
data_tool_01 = data_tool_01[data_tool_01['SUBJ_ID'].str.startswith('S')]

panel_510 = pd.read_excel("/Users/yshmbid/Documents/home/github/kosmos/workspace/data/0528/510명 대상자 패널 정보.xlsx", engine="openpyxl")
```

- data tool: eCRF에 VCF 파일이 등록된 대상자들의 데이터 (데이터수 993 / 등록자 877명)
- data tool 01: eCRF에 등록된 NGS report 수기추출 데이터 (데이터수 1010 / 등록자 949명)

```python
total_sid = list(set(data_tool['SUBJ_ID'].tolist()))
previous_sid = panel_510['SUBJ_ID'].tolist()
add_sid = [s for s in total_sid if s not in set(previous_sid)]
print(len(add_sid)) # 368
```

추가된 등록자수는 368명

```python
maf_path = "/Users/yshmbid/Documents/home/github/kosmos/workspace/data/0528/maf_0528.txt"
with open(maf_path, "r", encoding="utf-8") as f:
    maf_files = [line.strip() for line in f if line.strip()]
maf_df = pd.DataFrame({
    "SUBJ_ID": [file_name[:8] for file_name in maf_files],
    "file_name": maf_files
})
maf_df['SUBJ_ID_REVISED'] = maf_df['SUBJ_ID'].str[:4] + '-' + maf_df['SUBJ_ID'].str[5:]

add_maf = maf_df[maf_df['SUBJ_ID_REVISED'].isin(add_sid)]
previous_maf = maf_df[maf_df['SUBJ_ID_REVISED'].isin(previous_sid)]

add_maf_sid = list(set(add_maf['SUBJ_ID_REVISED'].tolist()))
previous_maf_sid = list(set(previous_maf['SUBJ_ID_REVISED'].tolist()))
print(len(add_maf_sid)) # 339
```

추가된 등록자수 중 MAF 파일이 존재하는 등록자는 339명

```python
with open("/Users/yshmbid/Documents/home/github/kosmos/workspace/data/0528/add_subj_0529.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(add_maf_sid))
```

339명의 Sample ID를 txt 파일로 저장.

### 3. MAF 표준화

```python
import os
import pandas as pd

os.getcwd() # 'C:\\Users\\User\\Documents\\yshid\\2605\\bin'

all_files = os.listdir(r"\\10.32.91.11\core\03. [로슈]정밀 의료 생태계 구축 사업\03-1. MAF(VCF)\최종 확인 MAF")
maf_files = [f for f in all_files if f.lower().endswith(".maf")]
len(maf_files) # 928
```

전체 MAF 파일은 928개

```python
with open(r"C:\Users\User\Documents\yshid\2605\data\add_subj_0529.txt", "r") as f:
    add_maf_sid = [line.strip() for line in f if line.strip()]
maf_df = pd.DataFrame({
    "SUBJ_ID": [file_name[:8] for file_name in maf_files], 
    "file_name": maf_files
})
maf_df['SUBJ_ID_REVISED'] = maf_df['SUBJ_ID'].str[:4] + '-' +  maf_df['SUBJ_ID'].str[5:]

add_maf = maf_df[maf_df['SUBJ_ID_REVISED'].isin(add_maf_sid)]
add_maf
```
<img width="1280" height="458" alt="image" src="https://github.com/user-attachments/assets/4dbee461-5c42-48c7-b84a-d03573f3970d" />

- 분석 대상 339명의 MAF 파일 368개는 위와 같이 구성.
- 샘플 ID는 S001-006 형태이고, MAF 파일 이름의 첫 8자는 샘플 ID를 표명하지만 S001-006 / S001_006의 2가지 형태를 갖는다.
- S001-006 형태로 표준화된 SUBJ_ID인 SUBJ_ID_REVISED 컬럼을 만들어준다.

```python
src_dir = r"\\10.32.91.11\core\03. [로슈]정밀 의료 생태계 구축 사업\03-1. MAF(VCF)\최종 확인 MAF"
dst_dir = os.path.join(src_dir, "260529_final_MAF_add")
```

- MAF 파일은 샘플 별로 1개 이상 존재한다.
- MAF가 2개 이상인 샘플은 해당 샘플의 MAF를 하나의 파일로 묶어서 표준화하고, final_MAF_add 라는 디렉토리에 '_merged'를 붙여 저장한다.

```python
subj_counts = add_maf['SUBJ_ID_REVISED'].value_counts()

for subj_id, group in add_maf.groupby('SUBJ_ID_REVISED'):
    out_name = f"{subj_id}_merged.maf"
    out_path = os.path.join(dst_dir, out_name)
    print(subj_id)
   
    if subj_counts[subj_id] == 1:
        src_file = os.path.join(src_dir, group['file_name'].values[0])
        #df = pd.read_csv(src_file, sep="\t", skiprows=1)
        try: 
            df = pd.read_csv(src_file, sep="\t", skiprows=1)
        except pd.errors.EmptyDataError:
            print(f"빈 파일 스킵: {src_file}")
            continue
        print(df.shape)
        if list(df.columns) != reference_columns:
            print(src_file)
        df.to_csv(out_path, sep="\t", index=False)
    else:
        dfs = []
        for fname in group['file_name'].values:
            src_file = os.path.join(src_dir, fname)
            #df = pd.read_csv(src_file, sep="\t", skiprows=1)
            try: 
                df = pd.read_csv(src_file, sep="\t", skiprows=1)
            except pd.errors.EmptyDataError:
                print(f"빈 파일 스킵: {src_file}")
                continue
            print(df.shape)
            if list(df.columns) != reference_columns:
                print(src_file)
            dfs.append(df)
        print(len(dfs))
        merged_cur_df = pd.concat(dfs, axis=0, ignore_index=True)
        merged_cur_df.to_csv(out_path, sep="\t", index=False)
```
```python
all_files = os.listdir(r"\\10.32.91.11\core\03. [로슈]정밀 의료 생태계 구축 사업\03-1. MAF(VCF)\최종 확인 MAF\260529_final_MAF_add")
maf_files = [f for f in all_files if f.lower().endswith(".maf")]
len(maf_files) # 339
```

생성된 파일 개수를 확인해보면 339개로 잘 생성된 것을 확인 가능하다!
