#!/usr/bin/env python

import click
import os,shutil
import glob

MAX_DEPTH = 6


#   **Traverse through input directories and make a list of all fastq files.**
# Traverse though `<input_dir><search_dir>` and get all passing fastq file
# paths. All file paths are placed in `fastq_files`, which is globally
# accessible. Only traverse MAX_DEPTH levels down for safety.
def get_fastq_files(input_dirs,search_dir):
    fastq_files = []
    for input_dir in input_dirs:
        for i in range(MAX_DEPTH):
            search_path = input_dir + search_dir
            # Traverse down `i` directories before searching.
            for j in range(i):
                search_path += "**/"

            matches = glob.glob(search_path + "*.fastq")
            if matches:
                fastq_files += matches
    return fastq_files


#   **Concatenate all fastq files with the same run ID and barcode.**
# Firstly, create sets of all barcodes and run IDs that the files in
# `fastq_files` are a part of. Then iterate through each combination of
# barcode and run ID, and write all files that match into a fastq file,
# effectively combining all fastq files that have the same barcode and run ID.
def cat_fastq_files(fastq_files, output_dir,subdir):
    barcodes = set()
    runids = set()
    combined_fastq_files = {}
    fullpath= output_dir + subdir
    #create directory if does not already exist
    os.makedirs(fullpath, exist_ok=True)

    for f in fastq_files:
        barcode = f.split("/")[-2]
        barcodes.add(barcode)
        runid = f.split("/")[-1].split("_")[2]
        runids.add(runid)

        fp = open(f, "r")

        # Create dict entry for this barcode if it does not already exist.
        if barcode not in combined_fastq_files:
            combined_fastq_files[barcode] = {}

        # Create dict entry for this barcode if it does not already exist.
        if runid not in combined_fastq_files[barcode]:
            combined_fastq_files[barcode][runid] = ""

        # Add file contents to its matching dictionary entry.
        combined_fastq_files[barcode][runid] += fp.read()
        fp.close()

    for b in combined_fastq_files:  # Iterate though barcodes.
        for r in combined_fastq_files[b]:  # Iterate through run IDs.
            fp = open("%s/%s_%s.fastq" % (fullpath, b, r), "w")
            fp.write(combined_fastq_files[b][r])
            fp.close()
        print("Combined %s into a single fastq file in %s/" % (b, fullpath))

    return

#   **Combine all sequencing summaries into one file**
# Get sequence summaries from the directories in `input_dirs` and concatenate
# them all into one string, being written to the master sequencing summary
# file located `sequencing_summary` (specified by user).
def cat_sequence_summaries(input_dirs, sequencing_summary):
    sequencing_summary_files = []

    # Get summary files
    for input_dir in input_dirs:
        sequencing_summary_files += glob.glob(input_dir
                                              + "/sequencing_summary.txt")

    final_sequencing_summary = ""  # Holds concatenated files.

    for f in sequencing_summary_files:
        fp = open(f, "r")
        if final_sequencing_summary == "":
            # Put entire file (including header) into
            # `final_sequencing_summary`.
            final_sequencing_summary = fp.read()
        else:
            # Put every line except for the first one (which is a header,
            # which is already in the file) into `final_sequencing_summary`
            for line in fp.readlines()[1:]:
                final_sequencing_summary += line

        fp.close()

    # Write the new sequencing summary file.
    if final_sequencing_summary != "":
        fp = open(sequencing_summary, "w")
        fp.write(final_sequencing_summary)
        fp.close()


#   **Get the total number of reads processed by Albacore**
# This is just the number of lines in the sequencing summary file, (minus the
# header line).
def get_num_reads_processed(sequencing_summary):
    with open(sequencing_summary, "r") as fp:
        lines = fp.readlines()
    num_reads_processed = len(lines) - 1
    return num_reads_processed


#   **Get the number of failed and passed reads**
# Go through the sequencing summary file and for each line record whether
# the `passes_filtering` field is true or false.
def get_num_reads_stats(sequencing_summary):
    num_reads_passed = 0
    num_reads_failed = 0
    num_no_match = 0
    with open(sequencing_summary, "r") as fp:

        header_line = fp.readline() #grab the header from the file

        for line in fp.readlines():
            if line.split("\t")[7] == "True":
                num_reads_passed += 1
            else:
                num_reads_failed += 1

                #also check to see if we have "no_match" set as well
                #at the moment, looks these reads do not appear anywhere in the fastq output in either fail or pass
                if line.split("\t")[15] == "no_match":
                    num_no_match += 1

    return num_reads_passed, num_reads_failed, num_no_match

#   **Generate and return a dict containing barcode run statistics**
# Read the `fastq` files in the given output directory and use these to
# generate a dict with a key for each barcode. The value for each barcode is a
# a dict with `passed`, `failed`, and `total` entries, containing the number of
# reads that passed, the number of reads failed, and total number of reads,
# respectively.
def get_barcode_stats(input_dirs, output_dir):
    barcode_stats = {}


    #determine total of all passed,failed and total across all barcodes
    totals = { 'passed':0, 'failed':0, 'all':0 }


    # For stats on passed reads we can use the output fastq files
    fastq_pass_files = glob.glob(output_dir + "/pass/*.fastq")

    get_barcode_stat(barcode_stats, totals, fastq_pass_files,'passed')

    # For stats on failed reads we have to use the input files
    fastq_fail_files = glob.glob(output_dir + "/fail/*.fastq")

    get_barcode_stat(barcode_stats,totals, fastq_fail_files,'failed')

    return barcode_stats,totals


#   **Generate and return a dict containing barcode run statistics for a single fastq fileset**
# Read the `fastq` files in the given output directory and use these to
# generate a dict with a key for each barcode. The value for each barcode is a
# a dict with either for `passed`, `failed` section of the dictionary
def get_barcode_stat(barcode_stats, totals, fastq_files,status):


    for f in fastq_files:
        barcode_name = f.split("/")[-1].split("_")[0]
        if barcode_name not in barcode_stats:
            barcode_stats[barcode_name] = {}
            barcode_stats[barcode_name]["passed"] = 0
            barcode_stats[barcode_name]["failed"] = 0
            barcode_stats[barcode_name]["total"] = 0

        with open(f, "r") as fp:
            numlines = len(fp.readlines())
            #correct formatted fastq files will have 4 lines per read.
            #if numlines is 0, then means no reads exist and do nothing
            if numlines !=0:
                numlines=numlines/4


            totals[status] += numlines
            totals['all']  += numlines

            barcode_stats[barcode_name][status] += numlines
            barcode_stats[barcode_name]["total"] += numlines

    return barcode_stats,totals


#   **Generate run health statistics and save to a file**
# Generate a report including reads processed by Albacore, number of passing
# reads and failing reads, and more. Save this data in nice tabular format to
# `output_path`.
def generate_run_health(input_dirs, sequencing_summary, run_health_path):
    num_reads_processed = get_num_reads_processed(sequencing_summary)
    (num_reads_passed, num_reads_failed,num_reads_no_match) = get_num_reads_stats(sequencing_summary)

    output_dir = os.path.dirname(run_health_path)
    barcode_stats,totals = get_barcode_stats(input_dirs, output_dir)

    fp = open(run_health_path, "w")
    fp.write("Total reads processed by Albacore:\t%d" % (num_reads_processed) + "\n")
    fp.write("Reads passed:\t%d" % (num_reads_passed) + "\n")
    fp.write("Reads failed:\t%d" % (num_reads_failed) + "\n")
    fp.write("Reads that failed with 'no_match':\t%d" % (num_reads_no_match) + "\n")

    fp.write("Multiplexing totals\tpass\tfail\ttotal" + "\n")


    #print out individual barcodes results
    for b in barcode_stats:
        fp.write("%s\t%d\t%d\t%d" % (b, barcode_stats[b]["passed"], barcode_stats[b]["failed"], barcode_stats[b]["total"]) + "\n")


    #print out total for each category
    fp.write("totals:\t%d\t%d\t%d" % (totals['passed'],totals['failed'],totals['all']) + "\n")


    fp.close()


@click.command()
@click.argument('deletefailed', nargs=1, type=bool, default=False, required=True)
@click.argument('sequencing_summary', nargs=1, required=True)
@click.argument('run_health', nargs=1, required=True)
@click.argument('input_dirs', nargs=-1, required=True)


def get_albacore_results(deletefailed,sequencing_summary, run_health, input_dirs):
    # get directory of ouput `sequencing_summary` so we can output the reads
    # there as well.
    output_dir = os.path.dirname(sequencing_summary)

    # Ensure input_dirs is always a list, even when there's only one entry.
    if not isinstance(input_dirs, tuple):
        input_dirs = [input_dirs]

    fastq_pass_files = get_fastq_files(input_dirs,"/workspace/pass/")

    #combine pass fastq files into result directory
    cat_fastq_files(fastq_pass_files, output_dir,"/pass")


    fastq_failed_files = get_fastq_files(input_dirs,"/workspace/fail/")

    #combine fail fastq files into result directory
    cat_fastq_files(fastq_failed_files, output_dir,"/fail")


    cat_sequence_summaries(input_dirs, sequencing_summary)
    generate_run_health(input_dirs, sequencing_summary, run_health)

    #check to see if we delete the failed fastqs reads
    if deletefailed == True:
        shutil.rmtree(output_dir +"/fail/")


if __name__ == "__main__":
    get_albacore_results()
