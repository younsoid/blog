---
date : 2025-04-21
tags: ['2025-04']
categories: ['rna-seq', 'kallisto']
bookHidden: true
title: "Kallisto Pseudoalignment 작업"
---

# Kallisto Pseudoalignment 작업

#2025-04-21

---

### 1. Build Index

```bash
$ kallisto index -i transcripts_cDNA.idx Homo_sapiens.GRCh38.cdna.all.fa.gz
```

#

### 2. Pseudoalign

```bash
$ kallisto quant -i transcripts_cDNA.idx -o output_150-1 -t 40 ../2306_tophat/data/Bowtie2Index/5-AZA_150-1_1_edited.fastq ../2306_tophat/data/Bowtie2Index/5-AZA_150-1_2_edited.fastq
```

- 3개 파일 생성
  - abundance.h5 - HDF5 binary file containing run info, abundance esimates, bootstrap estimates, and transcript length information length. This file can be read in by sleuth
  - abundance.tsv - plaintext file of the abundance estimates. It does not contains bootstrap estimates. Please use the --plaintext mode to output plaintext abundance estimates. Alternatively, kallisto h5dump can be used to output an HDF5 file to plaintext. The first line contains a header for each column, including estimated counts, TPM, effective length.
  - run_info.json - json file containing information about the run

#

### 3. Downstream 분석

- Kallisto는 일반적인 Alignment 도구와 달리 bam 파일을 output으로 생성하지 않기 때문에 HTSeq-count를 쓰는 대신 abundance.tsv 또는 .h5 파일을 Sleuth에서 직접 불러와서 통계 분석을 수행하는 것이 표준 워크플로우.

#