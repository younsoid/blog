---
date : 2025-04-21
tags: ['2025-04']
categories: ['rna-seq']
bookHidden: true
title: "RNA-seq 전처리 (Rsubread, edgeR)"
---

# RNA-seq 전처리 (Rsubread, edgeR)

#2025-04-21

---

가장 오류 적게나는 조합!

### 1. Align RNA-seq

<mark>Load Packages</mark>

```R
library(Rsubread)
library(org.Mm.eg.db)
library(gridExtra)
library(reshape2)
```

<mark>Set Path</mark>

```R
indir = "/data/home/ysh980101/2504/mirna/data"
outdir = "/data/home/ysh980101/2504/mirna/data"
refpath = "/data/home/ysh980101/2406/data-gne/mm39.fa"

setwd(indir)
getwd()
```
```plain text
'/data/home/ysh980101/2504/mirna/data'
```

<mark>Build Index</mark>

```R
buildindex(basename = "mm39", reference = refpath)
```

<mark>Read Alignment</mark>

```R
files <- list.files(pattern="\\.fastq\\.gz$", full.names=TRUE)
bams <- sub("\\.fastq\\.gz$", ".bam", files)
samples <- gsub("^\\.\\/|\\.fastq\\.gz$", "", files)
targets <- read.delim("target.txt", header=TRUE)

align(index="mm39", readfile1=files, input_format="gzFASTQ", output_file=bams, nthreads=50)
```

<mark>Quantification</mark>
```R
fc = featureCounts(bams, isGTFAnnotationFile=TRUE, GTF.featureType="exon", GTF.attrType="gene_id", isPairedEnd=FALSE, annot.ext="mm39.knownGene.gtf", useMetaFeatures=FALSE, allowMultiOverlap=TRUE, nthreads=50)
```

<mark>Save Countdata</mark>

```R
colnames(fc$counts) <- samples
y <- DGEList(fc$counts, group=group)
write.csv(as.data.frame(y$counts), file = paste0(outdir,"/count.csv", row.names = TRUE))
```

#

### 2. Gene ID Annotation

<mark>Load Packages</mark>

```python
import pandas as pd
import numpy as np
import os
```

<mark>Set Path</mark>

```python
indir = "/data/home/ysh980101/2504/mirna/data"
outdir = "/data/home/ysh980101/2504/mirna/data"
annotpath = "/data/home/ysh980101/2406/data-gne/MRK_ENSEMBL.rpt"

os.chdir(indir)
os.getcwd()
```
```plain text
'/data1/home/ysh980101/2504/mirna/result'
```

<mark>Load Annotation</mark>

```python
annotation = pd.read_csv(annotpath, sep="\t", names=[str(i) for i in range(13)])
annotation = annotation.dropna(subset=['6'])
annotation = annotation[annotation['8'] == 'protein coding gene']
```

<mark>Load Count & Gene ID Mapping</mark>

```python
count_mm39 = pd.read_csv("count.csv")
count_mm39.rename(columns={count_mm39.columns[0]: 'ens_id'}, inplace=True)
count_mm39['ens_id'] = count_mm39['ens_id'].str.split('.').str[0]

for index, row in annotation.iterrows():
    ens_ids = row['6'].split()
    gene_id = row['1']
    count_mm39.loc[count_mm39['ens_id'].isin(ens_ids), 'gene_id'] = gene_id
```

<mark>Transcript Filtering</mark>

```python
count_mm39['sum'] = count_mm39.iloc[:, 2:].sum(axis=1)
count_mm39 = count_mm39.sort_values(by=['gene_id', 'sum'], ascending=[True, False])
count_mm39 = count_mm39.drop_duplicates(subset=['gene_id'], keep='first')
count_mm39 = count_mm39.dropna(subset=['gene_id'])

count_mm39 = count_mm39.drop(columns=['sum', 'ens_id'])
gene_id_column = count_mm39['gene_id']
count_mm39.drop(columns=['gene_id'], inplace=True)
count_mm39.insert(0, 'gene_id', gene_id_column)
```

<mark>Save</mark>

```python
count_mm39.rename(columns={'gene_id': 'GeneID'}, inplace=True)

def rename_columns(col):
    parts = col.split('_')
    if len(parts) >= 3:
        new_col = parts[0] + parts[2] + '_' + parts[1]
    else:
        new_col = col
    return new_col

count_mm39.columns = [rename_columns(col) for col in count_mm39.columns]
count_mm39.to_csv(f"{outdir}/count_processed.csv", index=False)
```

#

### 3. DEG Analysis

<mark>Library & Set Path</mark>

```R
library(edgeR)

indir = "/data/home/ysh980101/2504/mirna/data"
outdir = "/data/home/ysh980101/2504/mirna/result"

setwd(indir)
getwd()
```
```plain text
'/data1/home/ysh980101/2504/mirna/data'
```

<mark>Set variables & Load Data</mark>

```R
tissue <- "G"
S1 <- "WT" 
S2 <- "GneKI"

counts <- read.csv("count_processed.csv")
meta <- read.csv(paste0("mouse_meta_",tissue,".csv"))
meta <- meta[meta$Group %in% c(S1, S2), ]

counts <- counts[, c("GeneID", unique(meta$SampleID))]
```

<mark>Create DGElist & Normalization</mark>

```R
Group <- factor(meta$Group)
Group <- relevel(Group, ref=S1)

y <- DGEList(counts=counts[,2:ncol(counts)], group=Group, genes = counts[,1])
y <- calcNormFactors(y)
```

<mark>Run DEG</mark>

```R
design <- model.matrix(~Group)
y <- estimateDisp(y, design)
y <- estimateGLMRobustDisp(y,design)

fit <- glmFit(y, design)
lrt <- glmLRT(fit)

plotMD(lrt)
abline(h=c(-1,1), col="blue")
```
![image](https://github.com/user-attachments/assets/339f2e97-6b71-45c1-8092-b801b68c9f23)


<mark>Save</mark>

```R
result_table <- topTags(lrt, n = nrow(lrt$table))
sorted_result_table <- result_table[order(result_table$table$FDR), ]
filtered_result_table <- sorted_result_table[sorted_result_table$table$FDR < 0.05, ]

write.csv(sorted_result_table, file = paste0(outdir,"/de-",tissue,"_",S1,"-",S2,".csv"))
```

#
