---
date : 2025-04-21
tags: ['2025-04']
categories: ['rna-seq']
bookHidden: true
title: "RNA-seq 전처리 파이프라인 비교"
---

# RNA-seq 전처리 파이프라인 비교

#2025-04-21

---

### 

#1 Methods

![image](https://github.com/user-attachments/assets/8cab1315-1ed9-4046-85c8-28ddbb813166)

<mark>비교 의의</mark>
  - Traditional 방법은 TopHat2+HTseq 조합이지만 오류도 넘 많이나고 Rsubread를 쓰면 빠르고 깔끔한데 왜 써야하지..? 싶어서 동일한 데이터(pair-end fastq)로 돌려봄.
  - HTseq에서 아래 코드를 수행할때 파라미터가 많은데 뭐가 다르게나오는지 모르겠어서 실험해봄.

<mark>Cases</mark>
1. Rsubread 사용
2. HTSeq 사용, `-i gene_id --additional-attr=gene_name` (exon 기준 count)
3. HTSeq 사용, `-i transcript_id --additional-attr=gene_id --additional-attr=gene_name` (transcript 기준 count)
4. HTSeq 사용, `-i transcript_id --additional-attr=gene_id --additional-attr=gene_name --nonunique=all` (여러 transcript에 매핑된 read는 모두 count)

###

#2 Result

![image](https://github.com/user-attachments/assets/85251a62-07d9-41c0-bd0c-f6e44507c262)

- A1CF gene count
  - Rsubread 사용: 378
  - HTSeq exon: 248
  - HTSeq transcript: 0
  - HTSeq transcript nonunique: 최대 343 (ENST00000373997 사용시)

- Rsubread와 HTseq-transcript-nonunique 버전이 개수가 제일 비슷하게 나왔다.

![image](https://github.com/user-attachments/assets/d06f3a58-d983-4c9c-a880-30a23bfe8393)
![image](https://github.com/user-attachments/assets/b8ebdb9d-245f-4598-82f4-867d38e94f48)
![image](https://github.com/user-attachments/assets/17152795-14d6-45a8-9787-ed40ce1ed904)

- DEG, Pathway 분석 비교
  - DEG 개수는 Rsubread 2612, TopHat-HTseq 2818이고 2191개 겹쳐서 비슷한것같음.
  - Pathway 분석 결과 중요한 term이었던 DNA methylation, Viral carcinogenesis를 포함해서 term과 p-adj도 비슷하게 나왔다.

###

#3 결론

- Rsubread 써도 될듯.
- HTseq은 보통 `-i gene_id`를 쓰던데 count 많이 뽑고싶으면 `-i transcript_id --nonunique=all`한 후 count 젤많은 transcript id 써주면 될것같다!


#
