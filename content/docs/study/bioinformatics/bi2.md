---
date : 2025-04-21
tags: ['2025-04']
categories: ['deg','sleuth']
bookHidden: true
title: "Sleuth 작업"
---

# Sleuth 작업

#2025-04-21

---

### 1. Load Package, Run Sleuth

```r
require("sleuth")
packageVersion("sleuth")
library("gridExtra")
library("cowplot")
library("biomaRt")
library(readr)

setwd("/data/home/ysh980101/2307_kallisto")
getwd()

sample_id <- dir(file.path("./"))
sample_id <- grep("^output_(150|con)", sample_id, value = TRUE)
sample_id <- substring(sample_id, 8)
sample_id

kal_dirs <- file.path(paste0("./output_", sample_id))
s2c <- read.table(file.path("./kallisto_demo_150_con.tsv"),
                  header = TRUE,
                  stringsAsFactors = FALSE,
                  sep = "\t")
s2c <- dplyr::mutate(s2c, path = kal_dirs)
s2c

marts <- listMarts()
ensembl <- useMart("ensembl")
datasets <- listDatasets(ensembl)
filtered_datasets <- datasets[grepl("hsapiens", datasets$dataset), ]
hsapiens_mart <- useMart("ensembl",dataset="hsapiens_gene_ensembl")
datasets <- listDatasets(hsapiens_mart)
filtered_datasets <- datasets[grepl("hsapiens", datasets$dataset), ]
hsapiens_mart <- useMart("ensembl",dataset="hsapiens_gene_ensembl",host="ensembl.org")
datasets <- listDatasets(hsapiens_mart)

t2g <- getBM(attributes = c("ensembl_transcript_id_version",
                            "ensembl_gene_id",
                            "description",
                            "external_gene_name"),
             mart = hsapiens_mart)
head(t2g)

ttg <- dplyr::rename(t2g, target_id= ensembl_transcript_id_version, 
                     ens_gene = ensembl_gene_id, ext_gene = external_gene_name)
ttg <- dplyr::select(ttg, c('target_id', 'ens_gene', 'ext_gene'))
head(ttg)

s2c$condition <- as.factor(s2c$condition)
s2c$condition <- relevel(s2c$condition, ref = "con")
so <- sleuth_prep(s2c, target_mapping = ttg,
  aggregation_column = 'ens_gene', extra_bootstrap_summary = TRUE)

so <- sleuth_fit(so, ~condition, 'full')
so <- sleuth_fit(so, ~1, 'reduced')
so <- sleuth_lrt(so, 'reduced', 'full')
sleuth_table_gene <- sleuth_results(so, 'reduced:full', 'lrt', show_all = FALSE)

sleuth_save(so, './sleuth_ward/150_con_so.sleuth')
write_csv(sleuth_table_gene, './sleuth_ward/150_con.csv')
```

### 2

- 자꾸 커널이 죽어서 ㅠㅠ r script 통으로 돌림
- 생애첫 rscript작성이었어서 기억에남는다 ㅋㅋㅎ

#
