---
date : 2026-11-04
tags: ['2026-11']
categories: ['vcf2maf']
bookHidden: true
title: "VCF MAF 변환 작업 #2 "
bookComments: true
index: 2
---

# VCF MAF 변환 작업 #2 

#2026-11-04

---

NCDC_batch_vcf2maf_V.1.3.3_github.sh 파일을 확인해본 결과이다.

```bash
# 1. user config
CORES=4
SAMPLE_TAG_LENGTH=8  # Tumor_Sample_Barcode length (e.g., 8 → "S002-033")
INPUT_DIR="/path/VCF_ALL"
OUT_MAF="/path/VCF_ALL_MAF"
...
GRCH37_FASTAS=( ".../hg19.fa" ".../Homo_sapiens_assembly19.fasta" ".../102_GRCh37/Homo_sapiens.GRCh37.dna.toplevel.fa" )
VCF2MAF_EXTRA_OPTS_GRCH37="--species homo_sapiens --ncbi-build GRCh37"
```

병렬 개수, 샘플 ID 길이, 입출력 폴더, vcf2maf/VEP 위치, GRCh37 FASTA 3종을 지정한다. 실패하면 다른 fasta를 사용해서 돌리는것이다.

경로에 102_GRCh37, 뒤쪽 106행에 ensembl-vep-release-102가 보이는데, 원래 작업 환경이 VEP 102였다는 뜻이다.

```bash
# 2. 레퍼런스 자동 탐색
```
resolve_reference_paths()가 설정한 경로에 파일이 없으면 SEARCH_ROOTS 아래를 find로 뒤져서 hg19.fa, chain 파일, homo_sapiens 폴더 등을 찾는다. 

워크스테이션마다 경로가 달라도 돌아가게 하려는 장치인데, Docker 버전에서는 이걸 reference-config.json으로 대체해 "어디를 뒤질지"를 사용자가 명시하도록 바꿨다.

```bash
# 3. 사전 점검
for cmd in bcftools perl java parallel file samtools tabix; do
  if ! command -v "$cmd" ...; then exit 1
```

vcf2maf.pl과 VEP가 있는지 확인하고 FASTA에 .fai가 없으면 samtools faidx로, liftover용 .dict가 없으면 Picard로 만든다. 로그 TSV의 헤더를 작성한다. (Docker에서 돌린 doctor-bundle이 이 단계에 해당)

```bash
# 4. 파일별 처리: process_vcf()
# 파일명과 샘플 ID
work_bn="${work_bn// /_}"; work_bn="${work_bn//(/_}"; work_bn="${work_bn//)/_}"
local sample_tag8="${orig_bn:0:${SAMPLE_TAG_LENGTH}}"
```

공백과 괄호를 _ 로 바꾼 작업용 이름을 만들고 파일명 앞 8글자를 Tumor_Sample_Barcode로 쓴다. 그래서 S002-054_S002-054_...vcf는 S002-054가 된다. 

```bash
# 압축·아카이브·엑셀 처리
inner_vcf=$(find "$unzip_dir" -type f \( -name "*.vcf" -o -name "*.vcf.gz" \) | head -n 1 || true)
```

file 명령으로 실제 형식을 보고 gzip/bzip2/xz면 풀고, zip/7z/rar/tar면 압축을 풀어 안에서 VCF를 찾는다. zip 안에 VCF가 여러개면 첫 1개만 쓴다. 

엑셀은 형식만 감지해서 플래그를 세우고 VCF처럼 실행한다. (사실상 실패를 로그에 남기는것)

```bash
# GINS 형식 보정
# 줄바꿈 변환
# chr 접두어 제거
# gVCF에서 변이만 추출

# Genome build 판별과 liftover
# 샘플 헤더 보정
# vcf2maf 실행과 FASTA 대체 시도
local cmd=( perl "$VCF2MAF_PATH/vcf2maf.pl"
            --input-vcf "$vcf_for_maf" --output-maf "$maf_out"
            --tmp-dir "$TMP_DIR" --ref-fasta "$ref_fasta"
            --vep-path "$VEP_PATH" --vep-data "$VEP_DATA"
            --tumor-id "$sample_tag8" --vcf-tumor-id "$tumor_vcf_id" ... )

# 병렬 실행
find "$INPUT_DIR" -type f -name "*.vcf*" -print0 | \
parallel -0 -j "$CORES" --linebuffer "$0" __worker {}
```

- GINS 형식 보정
  - #CHROM POS REF ALT ...처럼 ID와 QUAL 열이 빠진 특정 기관(GINS) 형식을 감지하면 awk로 빈 ID/QUAL 열을 끼워 넣어 표준 VCF로 만든다. REF가 <REF>나 .이면 N으로 바꾼다.
- 줄바꿈 변환
  - Windows에서 만든 파일(CRLF)이면 dos2unix로 LF로 바꾼다.
- chr 접두어 제거
  - 헤더에 ##contig=<ID=chr...가 있으면 chr1 → 1로 통일한다. 결과 MAF 염색체가 숫자 표기가 되는 이유이고, Docker config의 output_contig_style: numeric이 이걸 재현한 것이다.
  - 다만 조건이 contig 헤더 유무라서 헤더가 없는 ANNOVAR 파일은 이 단계를 건너뛰고 chr이 붙은 채로 넘어간다.
- gVCF에서 변이만 추출
  - 파일 어디에든 “GVCF”라는 글자나 <NON_REF>가 있으면 gVCF로 보고, SNV와 indel만 남긴다.
  - DRAGEN 파일(S005)처럼 헤더의 명령줄에 GVCF라는 단어만 있어도 gVCF로 분류된다.
  - 앞선 Docker 로그에서 S005가 is_gvcf: true로 나온 것도 같은 규칙이다. 그리고 FILTER가 PASS인지는 보지 않기 때문에 S005의 weak_evidence 2만여 개가 그대로 통과한다.
- Genome build 판별과 liftover
  - ##reference= 줄의 문자열을 보고, 없으면 chr1 contig 길이로 판단하고, 그것도 없으면 기본값 GRCh37로 처리한다.
  - GRCh38이면 Picard LiftoverVcf로 hg19로 옮기는데, chain 파일 이름에 따라 chr을 붙이거나 떼서 맞춘 뒤(1009–1017행) 시도하고, 결과가 비면 다음 chain으로 넘어간다.
- 샘플 헤더 보정
  - 가명화 과정에서 #CHROM 줄의 샘플 열 이름이 지워진 경우를 고친다.
  - 헤더는 8열인데 데이터가 10열 이상이면 FORMAT과 샘플명을, 헤더가 9열(FORMAT까지)이면 샘플명만 추가한다.
  - 샘플을 끝내 못 찾으면 파일명 8글자를 tumor ID로 강제 사용한다. 샘플이 2개면 이름에 normal/blood/germ 등이 들어간 쪽을 normal로 추정한다.
- vcf2maf 실행과 FASTA 대체 시도
  - FASTA 3종을 순서대로 넣어 vcf2maf를 돌리고, 성공하면 멈츤다. 변이가 하나도 없는 VCF면 vcf2maf를 건너뛰고 헤더만 있는 빈 MAF를 만든다.
  - 같은 샘플 ID의 파일이 동시에 vcf2maf를 돌지 않도록 flock으로 잠금 건다. 결과는 log_line으로 남는다.
- 병렬 실행
  - INPUT_DIR에서 이름에 .vcf가 들어간 모든 파일을 찾아 워커로 넘긴다.
  - 그래서 S017-010_S017_S017-010.vcf.zip처럼 이름에 .vcf가 있어야 대상이 되고, .xlsx는 처음부터 제외된다.
 
###

오류 이유를 확인해보면 아래와 같다.

```plain text
--af_esp 오류의 원인이 여기서 확실해졌습니다. 원본 스크립트 자체는 --af_esp를 넘기지 않습니다. vcf2maf.pl(mskcc 버전)이 VEP를 부를 때 내부적으로 넣는 옵션인데, 원본은 VEP 102와 짝지어 썼기 때문에 문제가 없었습니다. Docker 이미지는 같은 계열의 vcf2maf를 VEP 116과 묶었고, 최신 VEP에서는 이 옵션이 빠져서 충돌한 것입니다. 이미지를 만든 쪽에서 고쳐야 할 부분이고, 당장은 이미지 안의 vcf2maf.pl에서 해당 옵션을 지운 사본을 덮어씌워 우회해야 합니다.

헤더 없는 S002 파일이 원본에서는 통과했을 가능성이 높습니다. 원본은 bcftools를 "샘플 이름 확인" 같은 보조 용도로만 쓰고, 실패해도 파일명 8글자로 넘어가는 식이라 헤더가 없어도 그대로 VEP까지 갑니다. VEP는 ##fileformat 없이도 읽어 줍니다. 반면 Docker 버전은 VEP 전에 normalize-vcf(bcftools norm)라는 엄격한 정규화 단계를 새로 추가해서, 헤더가 없거나 INFO가 깨진 파일(S002-064)이 거기서 막힌 것입니다. 이전에 드린 전처리 스크립트가 바로 이 차이를 메우는 역할입니다.

임시 파일 이름 충돌도 Docker 버전에서 생긴 문제입니다. 원본은 입력 파일마다 다른 이름으로 vcf2maf를 돌려서 vcf2maf가 만드는 .vep.vcf 이름도 샘플마다 달랐습니다. Docker 버전은 정규화 결과를 모든 샘플에서 reference-1.normalized.vcf라는 같은 이름으로 만들기 때문에, 공용 TMP 폴더에서 VEP 결과가 겹칩니다. 그래서 --jobs 1을 권해 드린 것입니다.

원본에서도 주의해야 할 점 두 가지는 그대로 남아 있습니다. zip 안에서 VCF를 "처음 찾은 하나"만 쓰기 때문에, Oncomine zip(S017)은 원하는 *_Filtered_날짜.vcf 대신 28만 행짜리 SmallVariants.filtered.vcf가 잡힐 수 있습니다. 또 PASS 필터링이 어디에도 없어서, S005 같은 raw 파일은 저품질 변이가 전부 MAF에 들어갑니다. 두 경우 모두 VCF_ALL에 넣기 전에 원하는 VCF를 직접 꺼내고 PASS만 남겨 두는 게 안전합니다.

--af_esp 우회를 진행하려면 앞서 요청드린 세 명령(versions, batch-vcf-to-maf --help, grep -rln af_esp) 결과를 보내주세요. vcf2maf.pl의 정확한 위치를 확인한 뒤 패치 방법을 드리겠습니다.
```
```bash
docker run --rm --read-only --tmpfs /tmp:size=2g,mode=1777
  -v "C:\Users\Admin\cure-ngs\NGS_VCF:/data/NGS_VCF"
  -v "C:\Users\Admin\cure-ngs\references:/references:ro"
  -v "C:\Users\Admin\cure-ngs\config:/config:ro"
  $IMG batch-vcf-to-maf --workspace-root /data/NGS_VCF --reference-config /config/reference-config.json --reference-root /references --jobs 4 --forks 1
```

우선 돌렸던 코드는 이거였다.

`$IMG batch-vcf-to-maf`를 실행하면 이 단계로 진행되는데

```plain text
docker run ... batch-vcf-to-maf 
  └─ cure-ngs (이미지 안의 파이썬 래퍼)
       └─ perl vcf2maf.pl --input-vcf ... --vep-path ...   ← 래퍼가 내부에서 호출
            └─ perl vep --species ... --af_esp ...          ← vcf2maf.pl이 조립해서 호출
```

vcf2maf.pl 안에서 VEP 호출할때 `--af_esp`를 사용하고 있다.

```plain text
462:    if( $species eq "homo_sapiens" ) {
464:        $vep_cmd .= " --polyphen b" . ( $vep_script =~ m/vep$/ ? " --af" : " --gmaf" );
465:        $vep_cmd .= ( $vep_script =~ m/vep$/ ? " --af_1kg --af_esp --af_gnomad" : " --maf_1kg --maf_esp" ) unless( $online );
468:    $vep_cmd .= " --regulatory" unless( $species eq "canis_familiaris" or $online );
```

vcf2maf.pl을 확인해보면 사람(homo_sapiens)이고 오프라인 cache 모드면 --af_1kg --af_esp --af_gnomad를 붙이게 되어 있다. 

원본 환경의 VEP 102는 `--af_esp` 옵션이 가능한데 VEP 116버전에서는 이 옵션이 없다고 한다. 즉 원본 코드는 문제없이 돌아갔겠지만 Docker 이미지는 vcf2maf를 VEP 116와 묶어서 (원본은 102) 오류가 난것이다.

결론적으로 Docker 버전에서 문제는 3가지이고 

```plain text
- 헤더 없는 S002 파일이 원본에서는 통과했을 가능성이 높습니다. 원본은 bcftools를 "샘플 이름 확인" 같은 보조 용도로만 쓰고, 실패해도 파일명 8글자로 넘어가는 식이라 헤더가 없어도 그대로 VEP까지 갑니다. VEP는 ##fileformat 없이도 읽어 줍니다. 반면 Docker 버전은 VEP 전에 normalize-vcf(bcftools norm)라는 엄격한 정규화 단계를 새로 추가해서, 헤더가 없거나 INFO가 깨진 파일(S002-064)이 거기서 막힌 것입니다. 이전에 드린 전처리 스크립트가 바로 이 차이를 메우는 역할입니다.
- 임시 파일 이름 충돌도 Docker 버전에서 생긴 문제입니다. 원본은 입력 파일마다 다른 이름으로 vcf2maf를 돌려서 vcf2maf가 만드는 .vep.vcf 이름도 샘플마다 달랐습니다. Docker 버전은 정규화 결과를 모든 샘플에서 reference-1.normalized.vcf라는 같은 이름으로 만들기 때문에, 공용 TMP 폴더에서 VEP 결과가 겹칩니다. 그래서 --jobs 1을 권해 드린 것입니다.
- 원본에서도 주의해야 할 점 두 가지는 그대로 남아 있습니다. zip 안에서 VCF를 "처음 찾은 하나"만 쓰기 때문에, Oncomine zip(S017)은 원하는 *_Filtered_날짜.vcf 대신 28만 행짜리 SmallVariants.filtered.vcf가 잡힐 수 있습니다. 또 PASS 필터링이 어디에도 없어서, S005 같은 raw 파일은 저품질 변이가 전부 MAF에 들어갑니다. 두 경우 모두 VCF_ALL에 넣기 전에 원하는 VCF를 직접 꺼내고 PASS만 남겨 두는 게 안전합니다.
```

진단용 코드를 돌려봤다.

```bash
# 1) 이미지 안의 도구 버전 (VEP, vcf2maf, bcftools 등)
docker run --rm "$IMG" versions

# 2) batch-vcf-to-maf에 어떤 옵션이 있는지 (VEP 옵션을 바꿀 수 있는지 확인용)
docker run --rm "$IMG" batch-vcf-to-maf --help

# 3) --af_esp가 들어 있는 파일 위치 (vcf2maf.pl 경로 확인용)
docker run --rm --entrypoint bash "$IMG" -c 'grep -rln af_esp /opt /usr/local 2>/dev/null'
```

우선 versions에서 vcf2maf가 `/opt/vcf2maf/vcf2maf.pl, revision 754d68a…`로 나와서, 원본 파이프라인이 쓰던 vcf2maf 버전이 VEP 116.1과 묶여 있음을 확인했다. 

```plain text
/opt/vep/src/ensembl-vep/Bio/EnsEMBL/Variation/Utils/VEP.pm
/opt/vcf2maf/maf2maf.pl
/opt/vcf2maf/vcf2maf.pl
```
그리고 3번을 돌렸을때 이렇게 나왔는데 VEP.pm은 VEP 자체 코드이고 maf2maf.pl은 이번 VCF -> MAF 작업에 사용하지 않는 파일이다. 

vcf2maf.pl을 수정해주면 되는데 --vcf2maf(사용할 vcf2maf 경로)와 --overwrite를 사용해서 우회하도록 설정해준다.

```bash
# 1. vcf2maf.pl 꺼내서 --af_esp 지우기
New-Item -ItemType Directory -Force -Path C:\Users\Admin\cure-ngs\patch | Out-Null
docker create --name v2m $IMG
docker cp v2m:/opt/vcf2maf/vcf2maf.pl C:\Users\Admin\cure-ngs\patch\vcf2maf.pl
docker rm v2m

$p = "C:\Users\Admin\cure-ngs\patch\vcf2maf.pl"
$t = [IO.File]::ReadAllText($p) -replace ' --af_esp', ''
[IO.File]::WriteAllText($p, $t)
Select-String -Path $p -Pattern 'af_1kg'

$p = "C:\Users\Admin\cure-ngs\patch\vcf2maf.pl"
$t = [IO.File]::ReadAllText($p).Replace('$vep_cmd .= " --force_overwrite" if( $vep_overwrite );', '$vep_cmd .= " --force_overwrite";')
[IO.File]::WriteAllText($p, $t)
Select-String -Path $p -Pattern 'force_overwrite'

# 2. 오류났던 샘플 돌려보기
docker run --rm --read-only --tmpfs /tmp:size=2g,mode=1777 -v "C:\Users\Admin\cure-ngs\NGS_VCF:/data/NGS_VCF" -v "C:\Users\Admin\cure-ngs\references:/references:ro" -v "C:\Users\Admin\cure-ngs\config:/config:ro" -v "C:\Users\Admin\cure-ngs\patch\vcf2maf.pl:/opt/vcf2maf/vcf2maf.pl:ro" $IMG batch-vcf-to-maf --workspace-root /data/NGS_VCF --reference-config /config/reference-config.json --reference-root /references --jobs 1 --forks 1 --overwrite

# 3. 결과 확인
Get-ChildItem C:\Users\Admin\cure-ngs\NGS_VCF\VCF_ALL_MAF\*.maf | ForEach-Object {
  $lines = @(Get-Content $_.FullName | Where-Object { $_ -notmatch '^#' })
  $h = $lines[0] -split "`t"
  $iF = [array]::IndexOf($h, 'FILTER'); $iS = [array]::IndexOf($h, 'Tumor_Sample_Barcode'); $iC = [array]::IndexOf($h, 'Chromosome')
  $rows = @($lines | Select-Object -Skip 1)
  $cols = $rows | ForEach-Object { , ($_ -split "`t") }
  $filt = ($cols | ForEach-Object { $_[$iF] } | Group-Object | Sort-Object Count -Descending | Select-Object -First 3 | ForEach-Object { "$($_.Name)=$($_.Count)" }) -join ', '
  $smp = ($cols | ForEach-Object { $_[$iS] } | Select-Object -Unique) -join ','
  $chr = ($cols | Select-Object -First 1 | ForEach-Object { $_[$iC] })
  "{0,-55} rows={1,6}  sample={2}  chr_eg={3}  FILTER: {4}" -f $_.Name, $rows.Count, $smp, $chr, $filt
}
```
```plain text
S002-054_S002-054_snvindel.anno.hg19_multianno.maf      rows=     6  sample=S002-054  chr_eg=1  FILTER: .=6
S002-055_S002-055_snvindel.anno.hg19_multianno.maf      rows=     7  sample=S002-055  chr_eg=1  FILTER: .=7
S002-057_S002-057_snvindel.anno.hg19_multianno.maf      rows=     9  sample=S002-057  chr_eg=1  FILTER: PASS=8, .=1
S002-058_S002-058_snvindel.anno.hg19_multianno.maf      rows=     7  sample=S002-058  chr_eg=17  FILTER: PASS=7
S002-059_S002-059_snvindel.anno.hg19_multianno.maf      rows=     6  sample=S002-059  chr_eg=1  FILTER: PASS=6
S002-060_S002-060_snvindel.anno.hg19_multianno.maf      rows=     6  sample=S002-060  chr_eg=12  FILTER: PASS=4, .=2
S002-061_S002-061_snvindel.anno.hg19_multianno.maf      rows=     3  sample=S002-061  chr_eg=17  FILTER: .=3
S002-062_S002-062_snvindel.anno.hg19_multianno.maf      rows=     9  sample=S002-062  chr_eg=1  FILTER: .=9
S002-063_S002-063_snvindel.anno.hg19_multianno.maf      rows=     8  sample=S002-063  chr_eg=1  FILTER: .=8
S002-064_S002-064_VCF.maf                               rows=  3090  sample=S002-064  chr_eg=1  FILTER: PASS=3051, NOCALL=31, ABSENT_HET_RV=7
S002-065_S002-065_snvindel.anno.hg19_multianno.maf      rows=     8  sample=S002-065  chr_eg=10  FILTER: .=8
S002-066_S002-066_snvindel.anno.hg19_multianno.maf      rows=     7  sample=S002-066  chr_eg=1  FILTER: PASS=7
S002-068_S002-068_snvindel.anno.hg19_multianno.maf      rows=     4  sample=S002-068  chr_eg=11  FILTER: PASS=4
S002-069_S002-069_snvindel.anno.hg19_multianno.maf      rows=     4  sample=S002-069  chr_eg=17  FILTER: .=4
S005-026_S005-026_NGS_raw_data.maf                      rows=  1169  sample=S005-026  chr_eg=1  FILTER: weak_evidence=1066, PASS=41, weak_evidence;excluded_regions=22
S017-010_S017_S017-010.maf                              rows=    16  sample=S017-010  chr_eg=2  FILTER: PASS=16
S017-011_S017_S017-011.maf                              rows=     5  sample=S017-011  chr_eg=5  FILTER: PASS=5
S031-031_S031-031_NGS-97-26_final.maf                   rows=    16  sample=S031-031  chr_eg=1  FILTER: PASS=16
```

결과를 확인하면 다음과 같다고 한다.

```plain text
- S002 multianno 13개 — 그대로 사용 가능. 파일당 3~9개로 원본 레코드 수와 맞습니다. FILTER가 .인 건 "필터를 적용하지 않음"이라는 뜻으로, ANNOVAR 단계에서 이미 선별된 결과라 PASS와 같이 취급하면 됩니다. 원본보다 1~2개 많은 파일은 다중 대립유전자 레코드가 정규화 과정에서 둘로 나뉜 것입니다.
- S017-010(16개), S017-011(5개) — 그대로 사용 가능. 제가 zip 안 파일을 직접 세어 봤던 PASS 개수(16개, 5개)와 정확히 일치합니다. 걱정했던 28만 행짜리 파일이 아니라 올바른 *_Filtered_*.vcf가 쓰였고, CNV 행도 빠졌습니다. S031(16개 모두 PASS)도 정상입니다.
- S005 — PASS만 남겨야 함. 1,169개 중 PASS는 41개뿐이고 나머지 1,128개는 weak_evidence 등 저품질입니다. 원본 2만 4천여 줄 대부분은 변이가 없는 구간 기록이라 gVCF 추출 단계에서 이미 빠졌고, 남은 것 중 진짜 변이 후보가 41개입니다. 이건 MAF의 FILTER 열로 바로 걸러낼 수 있습니다.
- S002-064 — 다시 처리해야 함. 이 파일은 이름은 S002지만 내용은 Oncomine 전체 VCF입니다(NOCALL, ABSENT_HET_RV 같은 FILTER 값이 Oncomine 고유 형식). 문제는 PASS 3,051개 대부분이 실제 변이가 아니라는 점입니다. Oncomine은 정해진 hotspot 위치를 전부 검사해서 "여기는 변이 없음(유전형 0/0)"인 위치도 PASS로 기록합니다. 그리고 vcf2maf 코드를 확인해 보니, 유전형이 0/0이어도 MAF에서는 Tumor_Seq_Allele2에 ALT를 넣기 때문에 MAF만 봐서는 진짜 변이와 구분이 안 됩니다. 그래서 VCF 단계에서 유전형으로 걸러서 이 파일만 다시 돌려야 합니다.
```

재처리해야하는 파일들만 다시 돌렸다.

```bash
# S002-064 재처리
$src = "C:\Users\Admin\cure-ngs\NGS_VCF\VCF_ALL\S002-064_S002-064_VCF.vcf"
$dir = "C:\Users\Admin\cure-ngs\NGS_VCF_redo\VCF_ALL"
New-Item -ItemType Directory -Force -Path $dir | Out-Null
$keep = Get-Content $src | Where-Object {
  if ($_ -like '#*') { return $true }
  $f = $_ -split "`t"
  $gt = ($f[9] -split ':')[0]
  ($f[6] -eq 'PASS') -and ($f[4] -notlike '<*') -and [bool](($gt -split '[/|]') | Where-Object { $_ -match '^[1-9]' })
}
[IO.File]::WriteAllText("$dir\S002-064_S002-064_VCF.vcf", (($keep -join "`n") + "`n"))
"남은 변이 수: " + @($keep | Where-Object { $_ -notlike '#*' }).Count

# 제대로 나오면?
docker run --rm --read-only --tmpfs /tmp:size=2g,mode=1777 -v "C:\Users\Admin\cure-ngs\NGS_VCF_redo:/data/NGS_VCF" -v "C:\Users\Admin\cure-ngs\references:/references:ro" -v "C:\Users\Admin\cure-ngs\config:/config:ro" -v "C:\Users\Admin\cure-ngs\patch\vcf2maf.pl:/opt/vcf2maf/vcf2maf.pl:ro" $IMG batch-vcf-to-maf --workspace-root /data/NGS_VCF --reference-config /config/reference-config.json --reference-root /references --jobs 1 --forks 1 --overwrite
Copy-Item C:\Users\Admin\cure-ngs\NGS_VCF_redo\VCF_ALL_MAF\S002-064_S002-064_VCF.maf C:\Users\Admin\cure-ngs\NGS_VCF\VCF_ALL_MAF\ -Force
```

확인 결과 제대로 변환되었다!

###

다음에 새 VCF를 변환할때는 VCF_ALL에 넣고 아래 스크립트를 돌리면 됨.

```bash
$env:Path += ";C:\Program Files\Docker\Docker\resources\bin"
$IMG = "ghcr.io/ncdcbioinformatics/cure-ngs-harmonizer:0.2.5"
cd C:\Users\Admin\cure-ngs
docker run --rm --read-only --tmpfs /tmp:size=2g,mode=1777 -v "C:\Users\Admin\cure-ngs\NGS_VCF:/data/NGS_VCF" -v "C:\Users\Admin\cure-ngs\references:/references:ro" -v "C:\Users\Admin\cure-ngs\config:/config:ro" -v "C:\Users\Admin\cure-ngs\patch\vcf2maf.pl:/opt/vcf2maf/vcf2maf.pl:ro" $IMG batch-vcf-to-maf --workspace-root /data/NGS_VCF --reference-config /config/reference-config.json --reference-root /references --jobs 1 --forks 1 --overwrite
```

수행 방법 및 원래 Docker 이미지와 바뀐점은 아래와 같다.

```plain text
[이미지 원래 동작]
- cure-ngs-harmonizer 0.2.5 (VEP 116.1, vcf2maf 754d68a, bcftools 1.13, Picard 3.1.1)
- 레퍼런스: UCSC hg19 단일 FASTA + VEP 116 GRCh37 cache, 출력 염색체 숫자 표기
- 결과 MAF에 CNV 등 기호형 ALT 없음 (제외 단계는 확인 필요)
- 원본 스크립트(VEP 102, FASTA 3종 fallback)와 주석 버전이 다름

[실행 시 바꾼 점]
- vcf2maf.pl 사본에서 --af_esp 제거, --force_overwrite 상시 적용 후 마운트
- --jobs 1 순차 실행

[입력 전처리]
- S002-*.vcf 14개: ##fileformat·hg19 contig 헤더 보완(없는 경우), INFO 열 '.'로 대체
- 중복 파일 1개 제거
- 품질 필터(PASS, 유전형, gnomAD 빈도)는 원본 규칙대로 적용하지 않음
```
