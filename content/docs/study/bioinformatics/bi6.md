---
date : 2025-04-21
tags: ['2025-04']
categories: ['wgbs', 'bismark']
bookHidden: true
title: "WGBS 전처리 (Bismark)"
---

# WGBS 전처리 (Bismark)

#2025-04-21

---

### 1. Build Index

```bash
$ bowtie2-build Homo_sapiens.GRCh38.dna.toplevel.fa GRCh38 -p 40
```

### 2. Bam Sorting & Indexing

```bash
$ samtools sort KEB01_1_bismark_bt2_pe.bam -o KEB01_1_bismark_bt2_pe.sorted.bam

$ samtools index KEB01_1_bismark_bt2_pe.sorted.bam
```

### 3. Methylation Extraction

```bash
$ bismark_methylation_extractor --gzip --bedGraph --buffer_size 10G --cytosine_report --genome_folder /data3/PUBLIC_DATA/ref_genomes/homo_sapiens/GRCh37_hg19/Homo_sapiens/Ensembl/GRCh37/Sequence/WholeGenomeFasta KEB01_1_bismark_bt2_pe.sorted.bam
```
