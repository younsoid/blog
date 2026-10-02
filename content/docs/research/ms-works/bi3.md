---
date : 2025-04-21
tags: ['2025-04']
categories: ['gprofiler','ggplot2']
bookHidden: true
title: "Enrichment 분석 및 시각화 (gProfiler/ggplot2)"
---

# Enrichment 분석 및 시각화 (gProfiler/ggplot2)

#2025-04-21

---

### 

#1 Load Package

```r
library(ggplot2)
```

###

#2 Set Path

```r
setwd("/data-blog/bi3")
getwd()
```
```plain text
'/data-blog/bi3'
```

#

#3 Functional Enrichment Bubble Plot

```r
condition <- '150_con'
gpsource <- 'GO:BP'
#gpsource <- 'REAC'

df_c1 <- read.csv(paste0("./sleuth_ward/gprofiler/gProfiler_",condition,"_termsize.csv"))
df_c2 <- read.csv(paste0("gProfiler_",condition,"_c2_padj0.1.csv"))

df_c1 <- df_c1[df_c1$source == gpsource, ]
df_c2 <- df_c2[df_c2$source == gpsource, ]
df_c1$reg_type <- 'down'
df_c2$reg_type <- 'up'
df_c1$nlog <- -abs(df_c1$negative_log10_of_adjusted_p_value)
df_c2$nlog <- abs(df_c2$negative_log10_of_adjusted_p_value)
df_c1 <- df_c1[order(df_c1$negative_log10_of_adjusted_p_value), ]
df_c2 <- df_c2[order(-df_c2$negative_log10_of_adjusted_p_value), ]
df <- rbind(df_c1, df_c2)
ggplot(df, aes(x = reorder(term_name, nlog), y = negative_log10_of_adjusted_p_value, size = intersection_size, color = nlog)) +
  geom_point(alpha = 0.6) +
  theme(axis.text.y = element_text(angle = 0, vjust = 0.5, hjust=1)) +
  labs(title = "Bubble Plot - GO:BP / 150_con",
       x = "Term",
       y = "-log10(p-adj)",
       size = "Intersection Size",
       color = "-log10(p-adj)") +
  scale_size(range = c(1,10)) +
  scale_color_gradient2(low = "blue", mid = "white", high = "red") +
  coord_flip()
ggsave(filename = "./bubble_plot_150_con.png", width = 12, height = 6)
```
![image](https://github.com/user-attachments/assets/6c08353b-e0b1-4f29-999a-7ca9fe4ec2fd)


~원래 이쁜그림인데,, 안이뻐보이는건 데이터탓임~

#
