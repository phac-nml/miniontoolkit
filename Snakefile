import os

#load run configuration file
configfile: "configs/minion.yaml"

#fetch parameters that are specifc to this minion run
FLOWCELL=config["FLOWCELL"]
KIT=config["KIT"]
BASEDIR=config["BASEDIR"]
GATHER=config["GATHER"]
ALBACORE_VERSION=config["ALBACORE_VERSION"]

#directory path to Miniknow fast5 files are located
RAW_READS=[f.name for f in os.scandir(BASEDIR) if f.is_dir() ]

rule aggregate_results:
  input:
    expand("albacore_results/results_{sample}", sample=RAW_READS)
  output:
    "results/sequencing_summary.txt", #combine all albacore runs into a SINGLE sequencing_summary.txt
    "results/run_health.txt" # statistics on how well the run went.
  conda:
    "envs/combineResults.yml"
  shell:
    "{GATHER} {output} {input}"

rule albacore:
  input:
    "%s/{raw_reads}" % (BASEDIR)
  output:
    directory("albacore_results/results_{raw_reads}")
  threads: 8
  conda:
    "envs/albacore-%s.yml" % (ALBACORE_VERSION)
  shell:
    "read_fast5_basecaller.py --flowcell {FLOWCELL} --kit {KIT} --barcoding --recursive --output_format fast5,fastq --input {input} --save_path {output} --disable_pings -q 999999999 --worker_threads {threads}"

