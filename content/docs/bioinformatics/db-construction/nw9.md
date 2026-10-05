---
date : 2026-06-17
tags: ['2026-06']
categories: ['ngs']
bookHidden: true
title: "고빈도 샘플을 VCF로 매칭"
bookComments: true
---

# 고빈도 샘플을 VCF로 매칭

#2026-06-17

---

### 1. 작업 개요

이전 게시물에서 비매칭된 78건의 데이터에 대해서 2차 매칭을 진행하였다.
- GENE_UNEXIST – 55
- UNMATCHED – 23

Gene별 unmatched 비율과 Sample별 unmatched 비율을 확인했을때 Gene은 unmatched 빈도가 높으면서 동시에 비율도 높은게 없어서 Gene별로 봤을때는 캐칭하기 어려울것같다는 점을 확인했다. 그리고 Sample별로 봤을때는 unmatched 빈도가 높은게 비율도 높았어서, Sample별로 확인해볼 필요성을 확인하였다. 그리고 Gene의 unmatched에는 report 추출시 유전자 이름 오타, report와 maf에서 사용하는 유전자 이름의 alias등이 원인일수있음까지 확인하였다. 

따라서 308명의 Raw MAF 파일을 모두 확인해서 MAF에 등장하는 유전자 이름 21,033개를 확인하였고 Report의 유전자 이름과 alias인 이름이 사용돼서 이전에 캐치되지 않은 건을 확인했다. 그결과  MRE11, SMAD, ABRAXAS1 3개를 recovery하였다. 그리고 유전자 이름 오타를 확인해서 SMAAD4(2건), ARD1A라는 오타를 확인해서 추가로 3개를 recovery 하였다. 그리고 추가로 S011-011 MAF는 "Hugo_Symbol 컬럼 없음"이 뜬것을 확인했다. 

###

다음으로 unmatched 비율도 높고 빈도도 높은 S032-004, S004-037, S024-020, S006-056, S005-017을 확인해본결과
- S032-004 - VCF를 GRCh38→GRCh37로 liftover 후 MAF를 재생성
- S004-037 - VCF 재요청 (표준 VCF와 달리 헤더에 ID와 QUAL이 누락) + GRCh38→GRCh37로 liftover 후 MAF를 재생성
- S024-020 - VCF를 GRCh38→GRCh37로 liftover 후 MAF를 재생성
- S006-056 - VCF 재요청 (VCF가 10행으로 다른 샘플에 비해 현저히 짧음)
- S005-017 - 올바른 VCF를 사용해서 MAF를 재생성

를 확인할 수 있었고 재요청이 필요하지 않은 3개 샘플에 대해서 recovery시 최대 23건의 unmatched가 매칭 가능함을 확인하였다. 

이에 23건에 대해서 recovery 작업을 진행할 예정이고, 샘플 단위로 보는게 좀 잘나오는것같아서 추가로 확인할 다른 샘플을 뽑아서 걔네도 확인해보려고 한다.

###

참고로 비매칭 72건(6건은 Gene으로 recovery함) 현황은 아래와 같다.
- GENE_UNEXIST – 49
- UNMATCHED – 23
 
###

### 2. 작업 내용

작업에 앞서서 S004-037이 표준 VCF와 달리 헤더에 ID와 QUAL이 누락되었다고 했는데 ID와 QUAL이 MAF 생성에 필수가 아니라면, 즉 그 컬럼이 없음을 반영해서 liftover 후 MAF 재생성하면 SNV 정보를 얻을 수 있는지를 확인했다.

확인 결과 CHROM, POS, REF, ALT(변이 식별) + INFO/CSQ(유전자·HGVS 주석) + FORMAT/SAMPLE(VAF·depth) 정도가 필수이며 ID와 QUAL은 없음 처리한 채로 변환이 가능하다고 한다. 그래서 기존 23건에 9건을 추가해서 총 32건에 대해 recovery 작업을 해줄려고 한다.

### 1) S004-037

VCF의 INFO 컬럼과 Report SNV는 다음과 같이 이루어진다
- INFO 내 CSQ 내 coding (ex. c.547G>T) - dna_change와 매핑
- INFO 내 CSQ 내 protein (ex. p.Asp183Tyr) - aa3_change와 매핑
- INFO 내 CSQ 내 gene - Gene와 매핑

<img width="1280" height="140" alt="image" src="https://github.com/user-attachments/assets/263e03a8-46fe-4e4a-b17f-b05cdd918152" />

VCF 확인 결과 9건 모두 CSQ내 gene, coding이 Report와 정확히 매핑되었다. 다만 hg19가 아니라 hg38 기준으로 start position이 나와있어서 hg19로 liftover 후 MAF 생성하면 start position은 달라질 수 있고 내가 매칭을 id_gene_start를 key로 두고 했어서 부득이하게 위와 같이 매칭해줬다.

현재까지 매칭 결과는 다음과 같다.
- GENE_UNEXIST – 48(-1)
- UNMATCHED – 15(-8)

### 2) S032-004

<img width="1280" height="219" alt="image" src="https://github.com/user-attachments/assets/2e48cd3b-500b-4c31-bf80-4e93f3bd88c5" />

VCF 확인 결과 15건 모두 CSQ내 gene, coding이 Report와 정확히 매핑되었다. 마찬가지로 hg38 기준으로 start position이 나와있어서 key는 위와 같이 매칭해줬다.

현재까지 매칭 결과는 다음과 같다.
- GENE_UNEXIST – 37(-11)
- UNMATCHED – 11(-4)
 
### 3) S024-020

VCF 확인 결과, 이전과 달리 CSQ에 gene, coding 정보가 없어서 매칭이 어려웠다. 정석대로 VCF를 MAF로 변환 후 매칭해야할듯하다. 

### 4) S005-017

<img width="1280" height="42" alt="image" src="https://github.com/user-attachments/assets/f3c95d28-f52a-4b87-819e-3e487abe6d0c" />

해당 샘플은 VCF가 2개였는데 그중 올바른 샘플인 23TMBR_84-5_Jang_Wansik_v1_23TMBR_84-5_Jang_Wansik_RNA_v1_Filtered_2023-03-14_16 파일을 확인하였다. 해당 VCF의 FUNC 내에 gene·coding(c.)·protein(p.)·transcript 값을 Report와 매칭해줬고 그 결과 Report의 SNV 2개와 모두 매칭되었다. 어노테이션이 정상적으로 hg19여서 start position 값을 그대로 매칭해줬다. 

매칭 결과는 다음과 같았다.
- GENE_UNEXIST – 37
- UNMATCHED – 9(-2)
 
###

### 3. 작업 결과

최종 unmatched 샘플 개수는 아래와 같다.
- GENE_UNEXIST – 37
- UNMATCHED – 9

재변환 및 재요청 필요 샘플은 다음과 같고
- S024-020 - VCF 재변환 (VCF에서 변이 정보 식별 불가)
- S006-056 - VCF 재요청 (VCF가 10행으로 다른 샘플에 비해 현저히 짧음) 

위 샘플이 매칭된다고 가정하면 이렇게 남는다.
- GENE_UNEXIST – 25(-12)
- UNMATCHED – 8(-1)

###

### 4. 추가 작업

<img width="1280" height="663" alt="image" src="https://github.com/user-attachments/assets/b80b2355-cb81-435f-bd38-95578027f750" />

비매칭 46건에 대한 Sample ID와 빈도는 위와 같다.

5개 샘플에 대해서 매칭해보니, 샘플 단위 오류는 1) VCF-MAF 어노테이션 버전 문제 2) VCF 자체 문제 3) VCF 데이터가 zip으로 존재하는데 잘못된 파일을 씀 이렇게 3가지 같아서, 나머지 샘플들에 대해서 VCF의 헤더와 MAF의 컬럼을 확인해서 3가지 중 하나에 해당하는 경우가 있는지 확인했다.

참고로 VCF는 ##contig와 ##reference 헤더, MAF는 NCBI_Build 컬럼을 확인해줬는데, 결과가 아래와 같이 나왔다.

1. 빌드 불일치 (GRCh38 VCF / 7건)

7개 모두 VCF는 GRCh38인데 MAF는 GRCh37을 사용한 어노테이션 오류 케이스였고 이 케이스는 VCF의 정보로 매칭 가능하다. 다만 S024-020의 VCF에는 INFO 내의 coding, protein 등의 주석 정보가 없어서 MAF 변환을 해줘야 매칭 가능했는데 이런 케이스가 있을 수 있다.

<img width="1058" height="298" alt="image" src="https://github.com/user-attachments/assets/be69f086-1527-4d30-9f56-f9751c7add16" />


2. 행수가 너무 짧음 — 재요청 후보 (6건)

정상 패널 VCF가 수백~수만 행인 걸 감안해서 100행 이하인 VCF를 확인해줬고 6건이 나왔다.

S012-025는 2행으로 거의 빈 파일이었고, S003-021은 VCF는 59행인데 MAF가 0행이어서 MAF 변환이 실패인것일수 있고 VCF 자체에서 이미 재요청이 필요한것일수 있다. S013-014는 파일명에 BRCA2가 있어서 특정 유전자만 담은 VCF일 수 있어 전체 패널 VCF가 맞는지 확인이 필요하다. 그리고 S006-056·S006-011·S002-029는 10~13행으로 마찬가지로 짧아서 재요청이 필요해보인다. 

<img width="1053" height="272" alt="image" src="https://github.com/user-attachments/assets/8daa9852-3db4-47ba-8eba-63348eff92ab" />

3. zip 형태로 존재 (2건)

이 2건은 zip이어서 내용물을 확인한 다음에 Report와 같은 VCF를 사용해서 MAF를 만든게 맞는지 확인해줘야한다. 그리고 S010-082의 경우 gVCF는 일반 VCF와 달리 모든 위치(변이 없는 곳 포함)를 기록하는 형식이라, 변이만 추출(bcftools view로 non-ref만)해야 MAF 변환이 제대로 된다고 하는데 작업시 이를 고려해야 할것같다.

<img width="1043" height="120" alt="image" src="https://github.com/user-attachments/assets/423cc76c-0178-4d9a-a280-e50855f0a5a2" />

4. 나머지 (5건)

S002-049, S009-015, S003-904, S003-008, S003-001는 위 케이스에 해당 안되는데, 전체 결과가 아래와 같고

<img width="944" height="504" alt="image" src="https://github.com/user-attachments/assets/56ec5fb9-f30b-4e1c-870a-ad5ba7bd14e0" />

5개 케이스를 확인해보면 전부 길이도 완전히 똑같고 파일도 큰편이라서, 위 2개 기준으로는 오류라고 보기 어렵다. 

 

결론은 S024-020, S024-015, S003-069, S012-023, S003-061, S003-078, S024-018, S010-090, S010-082의 VCF를 클로드에 넣어서 헤더에 Report의 내용과 매칭되는 정보가 있는지 확인하면 될것같고 S013-014, S012-025, S003-021, S006-011, S006-056, S002-029에 대해서는 재요청 필요하다고 전달하면 될것같고, S002-049, S009-015, S003-904, S003-008, S003-001는 VCF와 MAF를 클로드에 넣어서 Report의 내용과 매칭되는게 없는 이유를 확인해야 할것같다. 
