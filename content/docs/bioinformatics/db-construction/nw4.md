---
date : 2026-06-02
tags: ['2026-06']
categories: ['ngs']
bookHidden: true
title: "revised_aa 오매칭 케이스 필터링"
bookComments: true
---

# revised_aa 오매칭 케이스 필터링

#2026-06-02

---

### 1. 작업 개요

이전에 계획한 바와 같이 Report 상의 VAF와 t_alt_count / t_depth × 100로 계산한 MAF의 VAF를 비교해서 VAF가 너무 다른 경우는 REVISED_AA에서 UNMATCHED로 바꿔주고자 했다. 
 
```python
def calc_maf_vaf(maf_row):
    """MAF row에서 VAF (%) 계산: t_alt_count / t_depth × 100. 계산 불가 시 None."""
    t_alt = maf_row.get('t_alt_count')
    t_depth = maf_row.get('t_depth')
    if pd.isna(t_alt) or pd.isna(t_depth):
        return None
    try:
        depth = float(t_depth)
        if depth == 0:
            return None
        return float(t_alt) / depth * 100
    except (TypeError, ValueError):
        return None
```

### 2. 작업 결과

<img width="1280" height="496" alt="image" src="https://github.com/user-attachments/assets/1c83326f-c42b-4df7-81fa-db324ba84d33" />

match_method가 REVISED_AA인 행만 확인한 결과는 위와 같고, VAF 분석 결과가 아래와 같았던 15건은 match_MAF를 NO로 변경했다. 

- 452 - Transcript isoform offset: STD aa1='p.A289V' matches MAF HGVSp_Short='p.A1155V' (same Ala>Val substitution, position offset of 866 residues likely due to alternative transcript) / STD VAF = '9.10%' and MAF VAF = '0.03%'
- 453 - Silent variant notation normalized: STD='p.Ile151Ile' matches MAF='p.I151=' (residue repeated vs '=' notation) / STD VAF = '6.12%' and MAF VAF = '0.00%'
- 454 - Silent variant notation normalized: STD='p.Tyr333Tyr' matches MAF='p.Y333=' (residue repeated vs '=' notation) / STD VAF = '5.08%' and MAF VAF = '0.00%'
- 455 - Silent variant notation normalized: STD='p.Asp98Asp' matches MAF='p.D98=' (residue repeated vs '=' notation) / STD VAF = '4.11%' and MAF VAF = '0.00%'
- 844 - Transcript isoform offset: STD aa3='p.Gly284Arg' matches MAF HGVSp_Short='p.G61R' (same Gly>Arg substitution, position offset of 223 residues likely due to alternative transcript) / STD VAF = '76.20%' and MAF VAF = '0.12%'
- 867 - Frameshift at same residue: STD aa1='p.P316fs' (ambiguous fs) matches MAF HGVSp_Short='p.P316Sfs*21' (specific frameshift starting at Pro316). STD dna_change='c.946_947insT' corresponds to MAF HGVSc='c.945dup' (equivalent insertion at same locus) / STD VAF = '23.90%' and MAF VAF = '36.43%'
- 873 - Frameshift at same residue: STD aa1='p.P316fs' (ambiguous fs) matches MAF HGVSp_Short='p.P316Sfs*21' (specific frameshift starting at Pro316) / STD VAF = '23.90%' and MAF VAF = '36.43%'
- 949 - Non-standard stop notation: STD='p.K1310X' equivalent to MAF='p.K1310*' (X vs * for termination) / STD VAF = '0.35%' and MAF VAF = '33.38%'
- <mark>952</mark> - Non-standard stop notation + transcript isoform offset: STD aa1='p.E400X' (X for termination) matches MAF HGVSp_Short='p.E418*' (same Glu>stop, position offset of 18 residues likely due to alternative transcript) / STD VAF = '0.26%' and MAF VAF = '26.26%'
- 953 - Non-standard stop notation + transcript isoform offset: STD aa1='p.Q1360X' (X for termination) matches MAF HGVSp_Short='p.Q1378*' (same Gln>stop, position offset of 18 residues likely due to alternative transcript) / STD VAF = '0.16%' and MAF VAF = '14.91%'
- 954 - Transcript isoform offset: STD aa1='p.P374L' matches MAF HGVSp_Short='p.P136L' (same Pro>Leu substitution, position offset of 238 residues likely due to alternative transcript) / STD VAF = '0.56%' and MAF VAF = '100.00%'
- 965 - Transcript isoform offset: STD aa1='p.R347H' matches MAF HGVSp_Short='p.R465H' (same Arg>His substitution, position offset of 118 residues likely due to alternative transcript) / STD VAF = '9.90%' and MAF VAF = '13.38%'
- 994 - Transcript isoform offset: STD aa3='p.Glu1562Ter' matches MAF HGVSp_Short='p.E1583*' (same Glu>stop substitution, position offset of 21 residues likely due to alternative transcript) / STD VAF = '38.23%' and MAF VAF = 'N/A'
- 1003 - Transcript isoform offset: STD aa3='p.Arg1947Ter' matches MAF HGVSp_Short='p.R1968*' (same Arg>stop substitution, position offset of 21 residues likely due to alternative transcript) / STD VAF = '56.64%' and MAF VAF = 'N/A'
- 1035 - Transcript isoform offset: STD aa3='p.Arg1947Ter' matches MAF HGVSp_Short='p.R1968*' (same Arg>stop substitution, position offset of 21 residues likely due to alternative transcript) / STD VAF = '38.30%' and MAF VAF = 'N/A'

다만 마킹한 952의 경우에는 숫자가 26이 중복되는것이... Report 수기추출 과정에서 오류가 있던게 아닌가? 싶어서 따로 확인이 필요할것같다.

