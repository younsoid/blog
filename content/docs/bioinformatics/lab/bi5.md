---
date : 2025-04-21
tags: ['2025-04']
categories: ['chip-seq']
bookHidden: true
title: "ChIP-seq 전처리 (trimmomatic, samtools)"
---

# ChIP-seq 전처리 (trimmomatic, samtools)

#2025-04-21

---

### 1. Trimming

<mark>chipseq_trimming.sh</mark>

```bash
#!/bin/bash

# setting envs
export bdir="/data3/projects/2022_KNU_EBV"
export hg38_bowtieidx="/data3/PUBLIC_DATA/ref_genomes/homo_sapiens/hg38/hg38_bowtie_idx/hg38.fa"
export hg38_bwaidx="/data3/PUBLIC_DATA/ref_genomes/homo_sapiens/hg38/hg38_bwa_index/hg38.fa"
export ebv_bowtie2idx="/data3/PUBLIC_DATA/ref_genomes/Human_gammaherpesvirus_4_EBV/EBV_bowtie2_idx/NC_007605.1.fa"
export ebv_bwaidx="/data3/PUBLIC_DATA/ref_genomes/Human_gammaherpesvirus_4_EBV/EBV_bwa_index/NC_007605.1.fa"

### SET Path ###
cd /data3/RAW_DATA/2023_KNU_EBV/ChIP-seq

### TRIMMING data ###
mkdir -p trimmed
sampdir="/data3/RAW_DATA/2023_KNU_EBV/ChIP-seq"
samplist=("Input" "p65" "RIgG")
TRIMMOMATIC= "/data/packages/trimmomatic/Trimmomatic-0.39/trimmomatic-0.39.jar"

for sampname in "${samplist[@]}"; do
    mkdir -p "trimmed/${sampname}"
    java -jar $TRIMMOMATIC PE -threads 40 -trimlog log1.txt $sampdir/${sampname}_1.fastq/${sampname}_1.fastq $sampdir/${sampname}_2.fastq/${sampname}_2.fastq $sampdir/trimmed/${sampname}/${sampname}_1.trimmed.fastq $sampdir/trimmed/${sampname}/${sampname}_1.up.trimmed.fastq $sampdir/trimmed/${sampname}/${sampname}_2.trimmed.fastq $sampdir/trimmed/${sampname}/${sampname}_2.up.trimmed.fastq ILLUMINACLIP:/data1/packages/trimmomatic/Trimmomatic-0.39/adapters/TruSeq3-PE.fa:2:30:10:2:True LEADING:3 TRAILING:3 MINLEN:36
done
```

###

### 2. Alignment

<mark>chipseq_alignment.sh</mark>

```bash
#!/bin/bash

# setting envs
export bdir="/data3/projects/2022_KNU_EBV"
export hg38_bowtieidx="/data3/PUBLIC_DATA/ref_genomes/homo_sapiens/hg38/hg38_bowtie_idx/hg38.fa"
export hg38_bwaidx="/data3/PUBLIC_DATA/ref_genomes/homo_sapiens/hg38/hg38_bwa_index/hg38.fa"
export ebv_bowtie2idx="/data3/PUBLIC_DATA/ref_genomes/Human_gammaherpesvirus_4_EBV/EBV_bowtie2_idx/NC_007605.1.fa"
export ebv_bwaidx="/data3/PUBLIC_DATA/ref_genomes/Human_gammaherpesvirus_4_EBV/EBV_bwa_index/NC_007605.1.fa"

### SET Path ###
cd /data3/RAW_DATA/2023_KNU_EBV/ChIP-seq

sampdir="/data3/RAW_DATA/2023_KNU_EBV/ChIP-seq"
samplist=("Input" "p65" "RIgG")

for sampname in "${samplist[@]}"; do
    bwa mem -t 20 -v 2 $ebv_bwaidx $bdir/trimmed/CTCF-C-SNU719_1.trimmed.fastq $bdir/trimmed/CTCF-C-SNU719_2.trimmed.fastq > $bdir/aln/bwa/CTCF-C_PE.bwa.sam

done

### Aligning to EBV - PE
bwa mem -t 20 -v 2 $ebv_bwaidx $bdir/trimmed/CTCF-C-SNU719_1.trimmed.fastq $bdir/trimmed/CTCF-C-SNU719_2.trimmed.fastq > $bdir/aln/bwa/CTCF-C_PE.bwa.sam
samtools view -hf 2 $bdir/aln/bwa/CTCF-C_PE.bwa.sam | samtools sort -o $bdir/aln/bwa/CTCF-C_PE.bwa.bam -O BAM -@ 20 -
samtools index -@ 20 $bdir/aln/bwa/CTCF-C_PE.bwa.bam
bamCoverage -b $bdir/aln/bwa/CTCF-C_PE.bwa.bam -o $bdir/aln/bwa/CTCF-C_PE.bwa.bam.bigwig
macs2 callpeak -t $bdir/aln/bwa/CTCF-C_PE.bwa.bam -f BAMPE -n CTCF-C --outdir peaks_ebv

### @REF: hg38
bowtie2 -k1 --no-unal -p 40 --qc-filter -x $bowtie2idx_hg38 -1 $bdir/trimmed/CTCF-C-SNU719_1.trimmed.fastq -2 $bdir/trimmed/CTCF-C-SNU719_2.trimmed.fastq > $bdir/aln/bwt2/CTCF-C_PE_hg38.sam > $bdir/aln/bwt2/CTCF-C_PE_hg38.sam
samtools view -hf 2 $bdir/aln/bwt2/CTCF-C_PE_hg38.sam | samtools sort -o $bdir/aln/bwt2/CTCF-C_PE_hg38.bam -O BAM -@ 20 -
sambamba view -h -t 20 -f bam -p -F "[XS] == null and not unmapped and not duplicate" $bdir/aln/bwt2/CTCF-C_PE_hg38.bam > $bdir/aln/bwt2/CTCF-C_PE_hg38_u.bam
samtools index -@ 20 $bdir/aln/bwt2/CTCF-C_PE_hg38_u.bam
macs2 callpeak -t $bdir/aln/bwt2/CTCF-C_PE_hg38_u.bam -f BAMPE -n CTCF-C --outdir peaks
```

###

### 3. Peak Calling

<mark>bedgraph.sh</mark>

```bash
#!/bin/bash

input_file="KEB01_1_bismark_bt2_pe.sorted.bedGraph.gz"
output_file="KEB01_1_bismark_bt2_pe.sorted_edited.bedGraph"

cd /data/home/ysh980101/2309_5-aza/Bismark_temp_GRCh38
zcat "$input_file" | awk '$4 != 0 { $1 = "chr" $1; print }' | gzip > "$output_file.gz"
```

#