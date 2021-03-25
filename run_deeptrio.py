import collections
import datetime
import hail as hl
import logging
import os
import pandas as pd
import re
import sys

from batch import batch_utils

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

DEEP_TRIO_DOCKER_IMAGE = "weisburd/deepvariant@sha256:5badeaf0485033b8606fa67b791ca5b35d5a3a92e8a2811f954733789b861f33"
GCLOUD_USER_ACCOUNT = "weisburd@broadinstitute.org"
GCLOUD_CREDENTIALS_LOCATION = "gs://weisburd-misc/creds"
GCLOUD_PROJECT = "seqr-project"
batch_utils.set_gcloud_project(GCLOUD_PROJECT)


hl.init(log="/dev/null")


NUM_CPU = 1
USE_GCSFUSE = True
OUTPUT_BASE_DIR = "gs://gnomad-bw2/deep-trio/"
EXPECTED_COLUMNS = set([
    'family_guid',
    'individual_id',
    'mother_id',
    'father_id',
    'individual_affected',
    'mother_affected',
    'father_affected',
    'ref_fasta',
    'ref_fasta_fai',
    'reads',
    'reads_index',
    'parent1_reads',
    'parent1_reads_index',
    'parent2_reads',
    'parent2_reads_index'
])

def main():
    p = batch_utils.init_arg_parser(
        default_cpu=NUM_CPU,
        default_memory=NUM_CPU*3.75,
        gsa_key_file=os.path.expanduser("~/.config/gcloud/misc-270914-cb9992ec9b25.json"))

    grp = p.add_mutually_exclusive_group(required=True)
    grp.add_argument("--all", action="store_true", help="run all samples")
    grp.add_argument("-s", "--sample", help="process specific sample name(s)", action="append")
    grp.add_argument("-n", "--n-samples", type=int, help="run on the 1st n samples only. Useful for debugging")
    p.add_argument("--offset", type=int, default=0, help="apply this offset before applying -n. Useful for debugging")

    p.add_argument("trios_tsv", help="Trios tsv", default="trios.tsv")
    args = p.parse_args()

    if not os.path.isfile(args.trios_tsv):
        p.error(f"File not found: {args.trios_tsv}")

    if args.trios_tsv.endswith(".xls") or args.trios_tsv.endswith(".xlsx"):
        df = pd.read_excel(args.trios_tsv)
    else:
        df = pd.read_table(args.trios_tsv)

    missing_columns = EXPECTED_COLUMNS - set(df.columns)
    if missing_columns:
        p.error(f"{args.trios_tsv} is missing columns: {missing_columns}")

    if args.n_samples:
        df = df[args.offset:args.offset+args.n_samples]

    if args.sample:
        df = df[df.sample_id.isin(set(args.sample))]
        if len(df) < len(set(filter(None, args.sample))):
            p.error(", ".join(set(args.sample) - set(df.sample_id)) + ": sample ids not found or don't have a bam file path")
        logger.info(f"Processing {len(df)} sample(s): " + ", ".join(list(df.sample_id[:10])))
    else:
        logger.info(f"Processing all {len(df)} samples")

    output_subdir = ".".join(os.path.basename(args.trios_tsv).split(".")[:-1])
    existing_output_files = batch_utils.generate_path_to_file_size_dict(
        os.path.join(OUTPUT_BASE_DIR, f"{output_subdir}/*_examples.tar.gz"))

    # process samples
    with batch_utils.run_batch(args, batch_name=f"DeepTrio: " + (", ".join(df.individual_id) if len(df) < 5 else f"{len(df)} trio(s)")) as batch:
        for i, row in df.iterrows():
            output_file = os.path.join(OUTPUT_BASE_DIR, f"{output_subdir}/{row.individual_id}_examples.tar.gz")
            if not args.force and output_file in existing_output_files:
                logger.info(f"Output file exists: {output_file} . Skipping {row.individual_id}...")
                continue

            # init Job
            j = batch_utils.init_job(batch, None, DEEP_TRIO_DOCKER_IMAGE if not args.raw else None, cpu=4)
            batch_utils.switch_gcloud_auth_to_user_account(j, GCLOUD_CREDENTIALS_LOCATION, GCLOUD_USER_ACCOUNT, GCLOUD_PROJECT)

            # localize files
            local_ref_fasta_path = batch_utils.localize_file(j, row.ref_fasta, use_gcsfuse=True)
            local_reads_path = batch_utils.localize_via_temp_bucket(j, row.reads)
            local_parent1_reads_path = batch_utils.localize_via_temp_bucket(j, row.parent1_reads)
            local_parent2_reads_path = batch_utils.localize_via_temp_bucket(j, row.parent2_reads)

            batch_utils.localize_file(j, row.ref_fasta_fai, use_gcsfuse=True)
            batch_utils.localize_via_temp_bucket(j, row.reads_index)
            batch_utils.localize_via_temp_bucket(j, row.parent1_reads_index)
            batch_utils.localize_via_temp_bucket(j, row.parent2_reads_index)

            local_ref_cache_tar_gz_path = batch_utils.localize_file(j, "gs://gcp-public-data--broad-references/hg38/v0/Homo_sapiens_assembly38.ref_cache.tar.gz", use_gcsfuse=True)

            #try:
            #    if not hl.hadoop_exists(row.cram_path):
            #        logger.info(f"unable to access cram: {row.cram_path}")
            #        continue
            #except Exception as e:
            #    logger.info(f"unable to access cram: {row.cram_path}. Error: {e}")
            #    continue

            name = re.sub(".bam$|.cram$", "", os.path.basename(row.reads))

            j.command(f"""mkdir ref_cache
            
            cd ref_cache
            tar xzf {local_ref_cache_tar_gz_path} | grep -v '^tar:'
            ls .
            export REF_PATH="/ref_cache/%2s/%2s/%s:http://www.ebi.ac.uk/ena/cram/md5/%s"
            export REF_CACHE="/ref_cache/%2s/%2s/%s"
            
            cd /
            mkdir examples

            /opt/deepvariant/bin/deeptrio/make_examples \
                --mode calling \
                --ref {local_ref_fasta_path} \
                --reads {local_reads_path} \
                --reads_parent1 {local_parent1_reads_path} \
                --reads_parent2 {local_parent2_reads_path} \
                --sample_name {name} \
                --sample_name_to_call {name} \
                --examples examples
    
            tar czf examples-{name}.tar.gz examples""")


if __name__ == "__main__":
    main()

