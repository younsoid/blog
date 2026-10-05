---
date : 2026-06-02
tags: ['2026-06']
categories: ['maf-ngsreport']
bookHidden: true
title: "MAF Report 매칭"
bookComments: true
index: 3
---

# MAF Report 매칭

#2026-06-02

---

### 1. 작업 내용

지난 작업을 통해 SNV 데이터 1,231개의 표기를 통일했다. 이제 표준화된 NGS Report의 SNV 정보를 실제 MAF에 표기된 SNV 정보와 비교해보고 일치도를 확인한다. 일치도 확인용 코드로 snv_std_2.py를 사용해줬고 입력 파일은 1) 표준화된 Report SNV 데이터인 snv_standardized.csv와 2) 대상자의 MAF 파일을 concat 해놓은 snv_maf.csv이다. 

여기서 snv_maf.csv를 만들 때 단순히 308명의 모든 MAF 파일을 위아래로 concat한다면 제일 쉽겠지만, MAF 파일 크기가 너무 크기 때문에 불가능하다. 그래서 1,231개 SNV 마다 (sample id, gene)을 가져와서 현재 sample id의 MAF 파일을 읽은 데이터프레임에서 현재 gene의 정보를 담은 행만 남기는 작업을 반복한 뒤에 리스트에 모으고 이를 concat해서 snv_maf.csv를 만들었다.

```python
maf_dir = r"\\10.32.91.11\core\03. [로슈]정밀 의료 생태계 구축 사업\03-1. MAF(VCF)\최종 확인 MAF\260529_final_MAF_add"
all_maf_files = [f for f in os.listdir(maf_dir) if f.lower().endswith(".maf")]

final_df_list = []

for _, row in snv_standardized.iterrows():
    cur_id = row['ID']
    cur_gene = row['Gene']
    print(cur_id, cur_gene)
   
    # cur_id로 시작하는 파일 찾기
    matched_files = [f for f in all_maf_files if f.startswith(cur_id)]
    if len(matched_files) == 0:
        print(f"파일 없음: {cur_id}")
        continue
   
    cur_file = os.path.join(maf_dir, matched_files[0])
    try:
        cur_maf = pd.read_csv(cur_file, sep="\t")
    except pd.errors.EmptyDataError:
        print(f"빈 파일 스킵: {cur_file}")
        continue
   
    cur_gene_maf = cur_maf[cur_maf['Hugo_Symbol'] == cur_gene].copy()
    cur_gene_maf['ID'] = cur_id
    print(cur_gene_maf.shape)
    final_df_list.append(cur_gene_maf)

final_df = pd.concat(final_df_list, axis=0, ignore_index=True)
final_df

final_df.to_csv(r"C:\Users\User\Documents\yshid\2605\data\snv_maf.csv", index=False)
```

<img width="889" height="431" alt="image" src="https://github.com/user-attachments/assets/18ff0d83-8564-4311-aeb8-45777d10d77c" />

필요정보만 뽑았는데도 49,193개의 SNP가 추출되었다.

<img width="1006" height="211" alt="image" src="https://github.com/user-attachments/assets/bebfd443-d368-4ae8-bd59-0ba348b46f6d" />

이를 사용해서 Report와 MAF와 일치도를 확인한 결과, Report의 SNV 정보 1,231개 중 1) Report의 dna_change와 MAF의 HGVSc가 정확히 일치하는 경우가 692건 2) Report의 aa1_change 또는 aa3_change가 MAF의 HGVSp_short 또는 HGVSp와 정확히 일치하는 경우가 348건 3) Report의 aa1_change 또는 aa3_change를 Rule-based로 표기 변경하면 일치하는 경우가 34건 4) MAF에 Gene 자체가 없는 경우가 58건 5) Gene은 있지만 해당 Mutation 정보가 없는 경우가 28건 6) 그외 경우가 71건이었다.

### 2. 결과 해석

REVISED_AA의 경우 아래와 같이 결과가 나오는데

- Transcript isoform offset: STD aa1='p.G624R' matches MAF HGVSp_Short='p.G640R' (same Gly>Arg substitution, position offset of 16 residues likely due to alternative transcript)
- Transcript isoform offset: STD aa3='p.Arg201His' matches MAF HGVSp_Short='p.R844H' (same Arg>His substitution, position offset of 643 residues likely due to alternative transcript)

1번 케이스는 위치 차이가 16밖에 안나서 같은 SNV일 수 있지만, 2번 케이스는 Arg-His라는 것만 같고 위치 차이가 643이나 나니까 동일한 SNV가 아닐 수 있다. 그래서 REVISED_AA는 check 컬럼에 VAF 같은 추가 정보를 확인해서 manual로 UNMATCHED인지 REVISED_AA인지를 분류해야 할것같다.

그리고 명령어에 snv_std_2.py 뒤에 check를 추가하면 check_04 컬럼을 추가해서 EXACT_DNA, EXACT_AA 항목에 대해서도 VAF를 확인해보면 좋을것같다(어느정도로 비슷해야 같은 SNV로 칠수있는지 확인용). 위 작업까지 마치고나서 완전히 분류되고 나면, UNMATCHED에 대해서 분포를 그려보고 UNMATCHED + UNEXIST에 대해서 분포를 그려보고 이렇게 2개 해보면 될것같다.
