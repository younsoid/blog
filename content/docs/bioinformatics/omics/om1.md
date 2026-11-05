---
date : 2026-11-04
tags: ['2026-11']
categories: ['vcf2maf']
bookHidden: true
title: "VCF MAF 변환 작업 #1 도커 연결, 레퍼런스 세팅, 배치 실행"
bookComments: true
---

# VCF MAF 변환 작업 #1 도커 연결, 레퍼런스 세팅, 배치 실행

#2026-11-04

---

```bash
# 1. VEP cache 다운로드
cd C:\Users\Admin\cure-ngs\references\vep
curl.exe -L -C - -o homo_sapiens_vep_116_GRCh37.tar.gz https://ftp.ensembl.org/pub/grch37/release-116/variation/indexed_vep_cache/homo_sapiens_vep_116_GRCh37.tar.gz

# 압축 풀기
tar -xzf homo_sapiens_vep_116_GRCh37.tar.gz
ls .\homo_sapiens

# 2. hg19 FASTA 다운로드
cd C:\Users\Admin\cure-ngs\references\grch37
curl.exe -L -C - -o hg19.fa.gz https://hgdownload.soe.ucsc.edu/goldenPath/hg19/bigZips/hg19.fa.gz
```
```bash
# 3. 도커 연결
$env:Path += ";C:\Program Files\Docker\Docker\resources\bin"
$IMG = "ghcr.io/ncdcbioinformatics/cure-ngs-harmonizer:0.2.5"
cd C:\Users\Admin\cure-ngs

# 4. FASTA 압축 해제  .fai 인덱스 생성
docker run --rm -v "C:\Users\Admin\cure-ngs\references:/references" --entrypoint gunzip $IMG -k /references/grch37/hg19.fa.gz
docker run --rm -v "C:\Users\Admin\cure-ngs\references:/references" --entrypoint samtools $IMG faidx /references/grch37/hg19.fa

# .dict 생성
docker run --rm -v "C:\Users\Admin\cure-ngs\references:/references" --entrypoint java $IMG -jar /opt/picard/picard.jar CreateSequenceDictionary R=/references/grch37/hg19.fa O=/references/grch37/hg19.dict

# 결과 확인
ls C:\Users\Admin\cure-ngs\references\grch37
```
```plain text
    디렉터리: C:\Users\Admin\cure-ngs\references\grch37

Mode                 LastWriteTime         Length Name                                                                                                                
----                 -------------         ------ ----                                                                                                                
-a----      2026-09-29   오전 9:15           9515 hg19.dict                                                                                                           
-a----      2026-09-23  오전 10:00     3199905909 hg19.fa                                                                                                             
-a----      2026-09-29   오전 9:14           3539 hg19.fa.fai                                                                                                         
-a----      2026-09-23  오전 10:00      948731419 hg19.fa.gz      
```

hg19.fa(3.2 GB), hg19.fa.fai, hg19.dict 3개 파일이 생성됨.

```bash
# 5. config 생성

# 염색체 표기 방식을 지정하는 옵션의 정확한 값을 확인
docker run --rm $IMG init-reference-config --help
```
```plain text
usage: cure-ngs init-reference-config [-h] --reference-root REFERENCE_ROOT
                                      [--cache-version CACHE_VERSION]
                                      [--fasta FASTA] [--assembly ASSEMBLY]
                                      [--fasta-label FASTA_LABEL]
                                      [--fasta-contig-style {auto,ucsc,numeric}]
                                      [--vep-data VEP_DATA]
                                      [--output-contig-style {ucsc,numeric}]
                                      [--force]
                                      output

positional arguments:
  output

options:
  -h, --help            show this help message and exit
  --reference-root REFERENCE_ROOT
                        Root visible to cure-ngs (normally /references in
                        Docker); candidate paths in the generated config are
                        relative to this root
  --cache-version CACHE_VERSION
  --fasta FASTA         Create a minimal single-reference config using this
                        path relative to --reference-root; omit it for the
                        legacy three-FASTA/two-chain GRCh37 fallback template
  --assembly ASSEMBLY
  --fasta-label FASTA_LABEL
  --fasta-contig-style {auto,ucsc,numeric}
  --vep-data VEP_DATA   VEP cache root relative to --reference-root (default:
                        vep)
  --output-contig-style {ucsc,numeric}
  --force
```

위 내용대로 config 진행해준다.

```bash
# config 생성
docker run --rm -v "C:\Users\Admin\cure-ngs\config:/config" $IMG init-reference-config /config/reference-config.json --reference-root /references --cache-version 116 --assembly GRCh37 --fasta grch37/hg19.fa --fasta-label UCSC_hg19 --fasta-contig-style ucsc --vep-data vep
Get-Content C:\Users\Admin\cure-ngs\config\reference-config.json

# 결과 확인
docker run --rm -v "C:\Users\Admin\cure-ngs\references:/references:ro" -v "C:\Users\Admin\cure-ngs\config:/config:ro" $IMG doctor-bundle --reference-config /config/reference-config.json --reference-root /references | Tee-Object reference-bundle.preflight.json
```
```plain text
# config 생성 출력
{
  "status": "CREATED",
  "mode": "single-reference",
  "config": "/config/reference-config.json",
  "reference_root": "/references",
  "next_steps": [
    "Run doctor-bundle; edit only explicitly selected paths if the report is not READY",
    "cure-ngs doctor-bundle --reference-config /config/reference-config.json --reference-root /references"
  ]
}

{
  "schema_version": "1.0",
  "reference_root": "/references",
  "target_assembly": "GRCh37",
  "unknown_assembly": "GRCh37",
  "output_contig_style": "numeric",
  "assemblies": {
    "GRCh37": {
      "fasta_candidates": [
        {
          "label": "UCSC_hg19",
          "path": "grch37/hg19.fa",
          "contig_style": "ucsc"
        }
      ]
    }
  },
  "vep": {
    "data": "vep",
    "cache_version": 116
  },
  "policies": {
    "allow_all_rejected_empty": false
  }
}
```
```plain text
# 확인 결과 출력
{
  "status": "READY",
  "failed_checks": 0,
  "bundle": {
    "config_path": "/config/reference-config.json",
    "root": "/references",
    "target_assembly": "GRCh37",
    "unknown_assembly": "GRCh37",
    "allow_all_rejected_empty": false,
    "output_contig_style": "numeric",
    "vep": {
      "data": "/references/vep",
      "cache_version": 116
    },
    "assemblies": {
      "GRCh37": {
        "fasta_candidates": [
          {
            "label": "UCSC_hg19",
            "path": "/references/grch37/hg19.fa",
            "contig_style": "ucsc"
          }
        ]
      }
    },
    "liftover": {}
  },
  "checks": [
    {
      "name": "reference_root",
      "status": "PASS",
      "detail": "/references"
    },
    {
      "name": "fasta:GRCh37:UCSC_hg19",
      "status": "PASS",
      "detail": "/references/grch37/hg19.fa"
    },
    {
      "name": "fai:GRCh37:UCSC_hg19",
      "status": "PASS",
      "detail": "/references/grch37/hg19.fa.fai"
    },
    {
      "name": "assembly:GRCh37:UCSC_hg19",
      "status": "PASS",
      "detail": "chromosome=chr1; observed_length=249250621; expected_GRCh37_length=249250621"
    },
    {
      "name": "contig_style:GRCh37:UCSC_hg19",
      "status": "PASS",
      "detail": "configured=ucsc; observed=ucsc; chromosome=chr1"
    },
    {
      "name": "vep_data",
      "status": "PASS",
      "detail": "/references/vep"
    },
    {
      "name": "vep_cache",
      "status": "PASS",
      "detail": "/references/vep/homo_sapiens/116_GRCh37"
    },
    {
      "name": "vep_cache_info",
      "status": "PASS",
      "detail": "/references/vep/homo_sapiens/116_GRCh37/info.txt"
    },
    {
      "name": "vep_cache_identity",
      "status": "PASS",
      "detail": "species=homo_sapiens; assembly=GRCh37; directory_version=116"
    },
    {
      "name": "vep_cache_payload",
      "status": "PASS",
      "detail": "/references/vep/homo_sapiens/116_GRCh37/1"
    },
    {
      "name": "vep_runtime_cache_compatibility",
      "status": "PASS",
      "detail": "runtime_status=available; runtime_version=ensembl-vep          : 116.1; configured_cache_version=116"
    }
  ]
}
```

"status": "READY", 실패 0건을 확인햇고

FASTA와 GRCh37 길이가 일치하고, chr 표기가 맞고, VEP 116 cache와 컨테이너 안의 VEP 116.1 버전이 호환됨을 확인했다.

```bash
# 6. VCF_ALL의 19개 파일 돌려보기
docker run --rm --read-only --tmpfs /tmp:size=2g,mode=1777 -v "C:\Users\Admin\cure-ngs\NGS_VCF:/data/NGS_VCF" -v "C:\Users\Admin\cure-ngs\references:/references:ro" -v "C:\Users\Admin\cure-ngs\config:/config:ro" $IMG batch-vcf-to-maf --workspace-root /data/NGS_VCF --reference-config /config/reference-config.json --reference-root /references --jobs 4 --forks 1

# 결과 확인
ls C:\Users\Admin\cure-ngs\NGS_VCF
ls C:\Users\Admin\cure-ngs\NGS_VCF\VCF_ALL_MAF
ls C:\Users\Admin\cure-ngs\NGS_VCF\VCF_ALL_LOG | select -First 5
```

결과를 확인해봤는데 오류가 나와서,, 원래 파이프라인이 문제인건지 내가 잘못돌린건지 확인해봐야할것같다.
