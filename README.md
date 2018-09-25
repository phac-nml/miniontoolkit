## Introduction ##

Snakemake application for parallelization of Oxford Nanopore basecalling using albacore software. It is scalable from local desktop to local high performance computing (HPC). With conda, it is completely self-contained with once on-demand building of conda environment for albacore software and other downstream tools.


## Just run it! ##


```

git https://github.com/phac-nml/miniontoolkit.git
cd miniontoolkit

#soft link your results
ln -s ~/results/run1/fast5 fast5


#invoking on local machine
snakemake --use-conda

#invoking on slurm Cluster
snakemake --use-conda --drmaa " -c {cluster.cpu} -p {cluster.partition} --mem={cluster.memory} " -u configs/slurm.yaml -j 50 -w 60

```

## Input Files ##


Directory of raw fast5 files from MiniKnow software. Recommended is to soft link to location of the fast5 directory instead of moving or copying to working directory.

**Example:**

`ln -s ~/results/run1/fast5 fast5`

## Ouputs Files ##


### results/* ###
File Name                                | description                                                       
---                                          | ---
`run_health.txt`                          | Overall statistics of the albacore run for individul barcode(s)  
`summary_sequencing.txt`                          | Tabular file that contains **sequencing_summary.txt** from all individual albacore run(s)                                                              
`pass/*.fastq`                          | Individual fastq file(s) of all passed reads. They are separate based on barcode Number and run ID.
`fail/*.fastq`                          | Individual fastq file(s) of all failed reads. They are separate based on barcode Number and run ID.




## Configuration Files ##



### configs/minion.yaml ###
Albacore  Parameters                                | Default Value                                                       | Usage
---                                          | ---                                                                 | ---
`FLOWCELL`                          | `FLO-MIN106`                                                             | Flowcell type that was used for generation of raw reads.
`KIT`                  | `SQK-RBK004`                                                             | Kit used for experiment
`BASEDIR`                  | `fast5`                                                             | Base directory of location of raw un-processed fast5 reads from MiniKnow software. Suggested behavior is to soft link your directory to the snakeMake directory. Example: `ln -s ~/results/run1/fast5 fast5`
`ALBACORE_VERSION`                  | `2.3.3`                                                             | Version of Albacore to be used in the basecalling. Current allow version are 2.3.0 , 2.3.1 , 2.3.3
`GATHER`                          | `scripts/gather_albacore_results.py`                                                             | `Developer Parameters`: Python script which aggregates all results from multiple albacore runs

### configs/slurm.yaml ###

Cluster specific Parameters                               | Name | Default Value                                                        | Usage
---                                          | ---                                                                 | --- | ---
`__default__`                          | cpu |  `1`                                                             | Default number of CPU slurm jobs will be given unless otherwise explicitly marked
`__default__`                          | partition |  `NONE`                                                             | Name of slurm partition to submit jobs too.
`__default__`                          | memory |  `8192`                                                             | Maximum memory allocated value to be passed to slurm
`albacore`                          | cpu |  `8`                                                             | Default number of CPU slurm jobs will be given unless otherwise explicitly marked
`albacore`                          | partition |  `NONE`                                                             | Name of slurm partition to submit jobs too.
`albacore`                          | memory |  `16384`                                                             | Maximum memory allocated value to be passed to slurm




## Conda environments ##

List of all ready to go conda environment that are available for Snakemake to build.

* envs/combineResults.yml
* envs/albacore-2.3.0.yml
* envs/albacore-2.3.1.yml
* envs/albacore-2.3.3.yml

## Legal ##
-----------

Copyright Government of Canada 2018

Written by: National Microbiology Laboratory, Public Health Agency of Canada

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this work except in compliance with the License. You may obtain a copy of the
License at:

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

## Contact ##
-------------

**Gary van Domselaar**: gary.vandomselaar@phac-aspc.gc.ca
