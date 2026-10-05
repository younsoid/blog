---
date : 2026-06-15
tags: ['2026-06']
categories: ['maf-ngsreport']
bookHidden: true
title: "MAF Report 비매칭 78건 수기 매칭"
bookComments: true
index: 2
---

# MAF Report 비매칭 78건 수기 매칭

#2026-06-15

---

### 1. 작업 개요

이전의 표준화 게시물에서 나왔듯이 최초 매칭 작업은 snv_std_2.py로 이루어지고, Input은 snv_standardized.csv와 snv_maf.csv이다. maf 데이터인 snv_maf.csv를 만들때 snv 데이터가 있는 308명의 전체 maf를 위아래 concat하면 가장 정확하겠지만, 그러면 데이터가 너무 커지기 때문에 report상에 snv 정보가 있는 유전자에 해당하는 행만 가져와서 snv_maf.csv를 만들었었고 약 4만개의 합리적인 행 수의 데이터를 사용할 수 있었다.

매칭작업을 하다보니 GENE_UNEXIST 라벨에 대해서 unmatched 빈도가 꽤 높은것을 확인할수 있었고, 그 원인으로 Report와 MAF가 동일한 Gene Annotation을 사용하지 않았을 경우 똑같은 유전자인데도 snv_maf에 catch되지 않아서, "해당 샘플의 maf에 해당 gene 없음" 처리되었을 가능성이 확인되었다. 이에 MAF의 Gene Symbol을 리스트로 받아와서, 클로드를 활용해서 GENE_UNEXIST 항목들의 Gene 이름과 매칭되는 Gene이 있는지를 확인하고, 매칭되는 샘플-Gene 쌍이 있다면 그 샘플의 maf raw 데이터를 사용해서 빈칸을 우선 채워줄려고 한다.

그리고 시간이 되면 snv_maf.csv 생성 코드를 수정해서 Report Gene - MAF Gene Symbol 딕셔너리를 활용해서 maf 가져올때 제대로 가져올수있게 하고 이를 테스트해보려고 한다.

###

### 2. Gene 별 매칭 개선

```python
import os
import pandas as pd

maf_dir = r"\\10.32.91.11\core\03. [로슈]정밀 의료 생태계 구축 사업\03-1. MAF(VCF)\최종 확인 MAF\260529_final_MAF_add"

all_maf_files = [f for f in os.listdir(maf_dir) if f.lower().endswith(".maf")]

maf_genes = []

for f in all_maf_files:
    cur_file = os.path.join(maf_dir, f)
    print(f)
    try:
        cur_maf = pd.read_csv(cur_file, sep="\t")
    except pd.errors.EmptyDataError:
        print(f"빈 파일 스킵: {cur_file}")
        continue

    if 'Hugo_Symbol' not in cur_maf.columns:
        print(f"Hugo_Symbol 컬럼 없음: {cur_file}")
        continue

    cur_genes = list(set(cur_maf['Hugo_Symbol'].dropna().tolist()))
    maf_genes.extend(cur_genes)

maf_genes = list(set(maf_genes))
print(f"총 유전자 수: {len(maf_genes)}") # 총 유전자 수: 21033
```

확인 결과 MAF의 Gene Symbol 21,033개 명단을 확인했다. 특이점은 S011-011 샘플은 "Hugo_Symbol 컬럼 없음"이 떴다.

```python
out_path = r"C:\Users\User\Documents\yshid\2606\data\maf_genes.txt"
with open(out_path, "w", encoding="utf-8") as fout:
    fout.write("\n".join(maf_genes))

print(f"저장 완료: {out_path}")
```

Gene 리스트를 저장해주고 unmatched인 78건에서 비교해봤을때 MAF가 구 Symbol을 사용하는 2건(신규 1건)과 기타 Gene name 오류 1건을 확인할수 있었다.
- S016-032 MRE11 (MAF에서 MRE11A)
- S028-004 ABRAXAS1 (MAF에서 FAM175A)
- S016-033 ARD1A (MAF에서 ARID1A / Report 오타)

<img width="1280" height="45" alt="image" src="https://github.com/user-attachments/assets/124a7a76-2b9e-49ee-a632-ac7c2edaab67" />

신규 2건을 제대로 매칭시켜줬다.

위의 Gene 매칭 개선을 통해 GENE_UNEXIST에 해당하는 6개 항목을 Recovery했다.

<img width="1280" height="98" alt="image" src="https://github.com/user-attachments/assets/29ffb175-5c41-4578-8f12-b225d87564b6" />

이로써 비매칭 78건 중 6건이 매칭되어 비매칭은 72건이 되었다.
- GENE_UNEXIST – 49(-6)
- UNMATCHED – 23
 
###

### 3. Sample별 매칭 개선

앞선 결과를 보면, Gene 보다도 Sample별 오류가 매우 많은것을 확인할수있었다.
- S032-004, S004-037, S024-020 -> Total unmatched 건수가 높으면서 비율도 100%
- S032-004, S024-020, S006-056 -> Gene unexist 측면에서 확인 필요해보임
- S004-037, S005-017 -> Manual unmatched 측면에서 확인 필요해보임

위 항목들을 확인해보려고 한다. 샘플마다 확인할 예정이고, input은 샘플별 표준화된 Report 정보와 Raw MAF를 넣어줄것이다.

### 1) S032-004

<img width="1280" height="230" alt="image" src="https://github.com/user-attachments/assets/6084fc00-1cd4-4fd9-8f44-c09fee765ae9" />

MAF에는 689행이 있는데 coding 변이(missense+nonsense+frameshift)는 27건뿐이고, 나머지 662건이 intron·IGR·flank 같은 배경 비코딩 변이라고 한다. 그리고 일반적인 암 패널 MAF는 TP53·KRAS·APC 같은 driver의 coding 변이는 있어야하는데 요 MAF에는 다 없다. 변이 콜링 또는 annotation 필터링 단계에서 panel coding 변이가 누락되었을 가능성이 있대서 VCF를 넣어주고 확인시켰다.

VCF 확인 결과 VCF는 GRCh38인데 MAF 파이프라인은 GRCh37로 되어있어서 어노테이션 오류가 난거라고 한다. VCF를 GRCh38→GRCh37로 liftover 후 MAF를 재생성하면 해당 15건을 잡을수 있을것같다.

### 2) S004-037

<img width="1280" height="142" alt="image" src="https://github.com/user-attachments/assets/2cb19cb0-bb2c-401f-814e-8057f39bd497" />

해당 샘플의 경우 VCF에서 MAF 변환할때 컬럼 매핑이 잘못돼서 밀리거나 누락되었다. Hugo_Symbol, Chromosome, Start_Position, Variant_Classification, Reference_Allele, CDS_position·Protein_position(일부 399행), all_effects, transcript는 다른 컬럼에서 확인 가능한데 ALT allele, HGVSc, HGVSp, read counts는 소실되어서 매칭이 아예 안되는 상태였다.

VCF를 확인시킨 결과 문제는 2개였는데, 첫번째로 표준 VCF와 달리 헤더에 ID와 QUAL이 누락돼있었다. MAF 파이프라인이 표준 VCF로 그대로 파싱하면서 한칸식 밀린거였다. 두번째로 VCF는 GRCh38인데 MAF는 GRCh37이어서 어노테이션 오류도 있었다.

### 3) S024-020

<img width="1280" height="99" alt="image" src="https://github.com/user-attachments/assets/d87f53a0-241c-4413-9c73-77d9255dd886" />

이 샘플도 VCF는 GRCh38인데 MAF 파이프라인은 GRCh37로 빌드되어서 VCF를 GRCh38→GRCh37로 liftover 후 MAF를 재생성하면 위 6건을 잡을수있다고 한다.

### 4) S006-056

이 샘플은 빌드나 헤더 문제가 없는데도 Report의 SNV가 MAF에 매칭되는게 없다. 2가지 이유가 있을수있는데 VCF에 콜링됐는데 MAF 생성에서 누락됐거나, VCF에도 없을 수 있다. VCF에 없으면 콜링 단계에서 누락되었을수도 있고 Report가 다른 검사/패널에서 온 변이 (예: Report는 조직검사, MAF는 ctDNA 등 검체·플랫폼 불일치)일수 있다고 한다.

<img width="1280" height="114" alt="image" src="https://github.com/user-attachments/assets/1fe5cf0b-9f41-4873-9e42-614616583836" />
 
이에 VCF와 Report를 모두 주고 확인시켰는데, S006-056 VCF가 10행으로 다른 샘플(S032-004(689), S004-037(36,925), S004-037(479))에 비해 매우 짧았다. Report PDF를 생성할때 쓴 최초 VCF를 제대로 요청해야할듯하다.

Report 패널 정보는 OncoPanel AMC v4, Tissue 검체(20S-093870 B1), GRCh37, VEP build 86이라고 한다(이정보를 어떻게 쓰는건지는 모르겠지만). 그리고 Report와 비교해보면 아래와 같은데

<img width="780" height="215" alt="image" src="https://github.com/user-attachments/assets/e365ffe2-7f98-4453-8e77-1e0b3b84f9e8" />

7개 변이가 단백질 변화까지 같게 완전히 동일하므로 같은 환자는 맞는데, VCF에는 Report 변이 7개가 없고 Report에 없는 3개 변이가 있는 상태다.

### 5) S005-017

<img width="1280" height="45" alt="image" src="https://github.com/user-attachments/assets/70cdbace-9e89-4451-bb1e-2e209d3f1b85" />

이 샘플은 VCF가 두개였는데 23TMBR_84-5_Jang_Wansik_v1_23TMBR_84-5_Jang_Wansik_RNA_v1_Filtered_2023-03-14_16.vcf가 있고 24STTSO055-14_20240801-171-5040_ST_I_DNA.hard-filtered.vcf가 있었다. 첫번째 파일의 플랫폼이 Torrent VC / Oncomine으로 Report의 GC Labs, Oncomine Comprehensive Plus, Ion S5와 일치해서 첫번째 파일이 올바른 VCF 파일이었다. 근데 MAF는 2번째 파일로 생성되어서 오류라고 한다. 

###

결론적으로 S032-004, S004-037, S024-020, S006-056, S005-017을 확인해본결과
- S032-004 - VCF를 GRCh38→GRCh37로 liftover 후 MAF를 재생성
- S004-037 - VCF 재요청
- S024-020 - VCF를 GRCh38→GRCh37로 liftover 후 MAF를 재생성
- S006-056 - VCF 재요청
- S005-017 - 올바른 VCF를 사용해서 MAF를 재생성
하면 23건을 잡을 수 있다.

###

### 4. 결과

Gene 별 매칭 개선으로 비매칭 78건 중 6건이 매칭되어 비매칭은 72건이 되었다. 그리고 Sample 별 매칭 개선 방안으로 23건에 대해서 개선 가능성을 확인했다. 다음 작업에서는 클로드로 위 23건에 대해서 매칭을 하고, 이전 작업물을 확인하면서 체크할 항목을 더 찾아볼 예정이다.

그리고 아래 항목은 작업 중 발견한 오류이지만 unmatched건을 캐치하는데는 유용하지 않았던 내용들이다!! 개인 작업때 쓸려고 남겨놓는다.

###

Cf) MAF t_alt_count 오류

MAF에서 t_ref_count + t_alt_count = t_depth여야한다. 그런데 t_ref_count + t_alt_count ≠ t_depth인 경우 즉 t_alt_count가 깨진 경우가 있다. MAF VAF를 계산할때 t_alt_count / t_depth × 100로 계산했는데 이런 경우라면 잘못된 VAF 값이 계산돼버린다. 확인 결과 t_ref_count + t_alt_count ≠ t_depth인 항목 10개를 확인했다.

<img width="903" height="593" alt="image" src="https://github.com/user-attachments/assets/ff722dba-a2d5-4668-84c7-95061f4be83e" />

위 항목들은 t_alt_count가 깨졌는데, (depth−ref)/depth로 계산하면 Report VAF와 거의 일치한다. 예시로 S028-004의 FAM175A를 보면 depth 588, ref=2이므로 alt=586이어야한다(588−2=586). 이렇게 수정해서 VAF 계산하면 VAF = 586/588 = 99.66% ≈ Report 99.65%으로 Report와 제대로 매칭되는것을 확인할수있다.

###

Cf2) Report VAF 추출 오류

Report의 VAF가 0~1 scale로 표기돼있는걸 그대로 적은 케이스도 종종 있어서 그것도 뽑아봤다. Report VAF × 100 ≈ MAF VAF인 행 7개를 확인했다.  

<img width="920" height="320" alt="image" src="https://github.com/user-attachments/assets/8956a3be-4468-48de-9450-7df37c338904" />

###

Cf3) S001-083 Report 추출 오류

S001-083 추출할때 VAF 칸에 alt_count(변이 read 수)를 적은 3건도 있었다. Report VAF를 다시 추출해서 적어야할듯하다.

<img width="956" height="160" alt="image" src="https://github.com/user-attachments/assets/691496ed-840d-46f8-9630-50365e8381ac" />
