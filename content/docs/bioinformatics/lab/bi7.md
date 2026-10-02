---
date : 2025-04-21
tags: ['2025-04']
categories: ['rna-seq']
bookHidden: true
title: "RNA-seq 전처리 (TopHat, SAMtools, HTSeq)"
---

# RNA-seq 전처리 (TopHat, SAMtools, HTSeq)

#2025-04-21

---

### 

#1 TopHat 실행

```bash
$ tophatpy -o tophat_out_33-1 --no-mixed -p 40 \
$ /data3/PUBLIC_DATA/ref_genomes/homo_sapiens/GRCh38/Homo_sapiens.GRCh38.dna.toplevel \
$ /data/home/ysh980101/2306_tophat/data/Bowtie2Index/5-AZA_33-1_1.fastq \
$ /data/home/ysh980101/2306_tophat/data/Bowtie2Index/5-AZA_33-1_2.fastq
```

- `tophatpy`: tophat2 안먹어서 커스텀한 명령어 (정식 명령어는 tophat2)
- `-o tophat_out_33-1`: 출력 디렉토리 설정
- `--no-mixed`: 페어 중 하나만 매핑되면 제외
- `-p 40`: 멀티스레딩, 40개 스레드 사용
- `/data3/PUBLIC_DATA/...dna.toplevel`: reference genome FASTA (Bowtie2 인덱스가 이와 동일한 경로로 있어야 함)
- 2개의 paired-end read 입력

cf) tophat alias 확인

```bash
view .bashrc
```
```bash
alias tophatpy='/usr/local/src/tophat-2.0.13/src/tophat.py'
```

cf2) Bowtie Index Build 안했다면?

```bash
bowtie2-build /data3/PUBLIC_DATA/ref_genomes/homo_sapiens/GRCh38/Homo_sapiens.GRCh38.dna.toplevel.fa \
/data3/PUBLIC_DATA/ref_genomes/homo_sapiens/GRCh38/Bowtie2Index/Homo_sapiens.GRCh38
```

### 

#2 SAMtools 정렬

```bash
samtools sort -n TopHat/tophat_out_33-1/accepted_hits.bam -o TopHat/tophat_out_33-1/accepted_hits.sorted.bam
```

- `-n`: 이름(name) 기준 정렬 (HTSeq에서 이름 기준 정렬 필요)

### 

#3 HTSeq-count 실행

```bash
$ python -m HTSeq.scripts.count -s no -a 0 -i transcript_id \
$ --additional-attr=gene_id --additional-attr=gene_name --nonunique=all \
$ -c Count/33-1_count.tsv \
$ TopHat/tophat_out_33-1/accepted_hits.sorted.bam \
$ /data3/PUBLIC_DATA/ref_genomes/homo_sapiens/GRCh38/Homo_sapiens.GRCh38.110.chr_edited.gtf 
```

- `TopHat/tophat_out_33-2/accepted_hits.sorted.bam`: 정렬된 BAM 파일
- `-s no`: strand 정보 무시
- `-a 0`: 최소 alignment quality 0
- `-c`: count 결과 저장 경로

- Custom Parameters
  - `-i transcript_id`: count 기준 feature ID (예: exon이 아닌 transcript 수준으로 count)
  - `--additional-attr`: gene_id, gene_name 등 추가 정보 기록
  - `--nonunique=all`: 여러 feature에 매핑된 read는 모두 count



#