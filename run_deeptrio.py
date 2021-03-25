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

DEEP_TRIO_DOCKER_IMAGE_WITH_GPU = "weisburd/deepvariant@sha256:5badeaf0485033b8606fa67b791ca5b35d5a3a92e8a2811f954733789b861f33"
DEEP_TRIO_DOCKER_IMAGE_WITHOUT_GPU = "weisburd/deepvariant@sha256:5b68fdf8d7283d5d7c5bdc000486b68ffeb5cddaa6b6cece128f7451e73b31b3"
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
    p.add_argument("--model", help="Which DeepTrio model to use", choices={"WES", "WGS", "PACBIO"}, required=True)

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
        os.path.join(OUTPUT_BASE_DIR, f"{output_subdir}/results_*.tar.gz"))

    # process samples
    with batch_utils.run_batch(args, batch_name=f"DeepTrio: " + (", ".join(df.individual_id) if len(df) < 5 else f"{len(df)} trio(s)")) as batch:
        for i, row in df.iterrows():
            name = re.sub(".bam$|.cram$", "", os.path.basename(row.reads))
            name_parent1 = re.sub(".bam$|.cram$", "", os.path.basename(row.parent1_reads))
            name_parent2 = re.sub(".bam$|.cram$", "", os.path.basename(row.parent2_reads))

            output_file = os.path.join(OUTPUT_BASE_DIR, f"{output_subdir}/results_{name}.tar.gz")
            if not args.force and output_file in existing_output_files:
                logger.info(f"Output file exists: {output_file} . Skipping {row.individual_id}...")
                continue

            # init Job
            j = batch_utils.init_job(batch, None, DEEP_TRIO_DOCKER_IMAGE_WITHOUT_GPU if not args.raw else None, cpu=NUM_CPU)
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

            # --regions chr22:38982347-38992804 \
            j.command(f"""mkdir ref_cache
            
            cd ref_cache
            tar xzf {local_ref_cache_tar_gz_path} 2>&1 | grep -v '^tar:' || true
            export REF_PATH="/ref_cache/ref/cache/%2s/%2s/%s:http://www.ebi.ac.uk/ena/cram/md5/%s"
            export REF_CACHE="/ref_cache/ref/cache/%2s/%2s/%s"
            
            mkdir "/results_{name}"
            cd "/results_{name}"

            /opt/deepvariant/bin/deeptrio/run_deeptrio \
                --model_type {args.model} \
                --ref {local_ref_fasta_path} \
                --reads_child "{local_reads_path}" \
                --reads_parent1 "{local_parent1_reads_path}" \
                --reads_parent2 "{local_parent2_reads_path}" \
                --output_gvcf_child "variants_{name}.gvcf.gz" \
                --output_gvcf_parent1 "variants_{name_parent1}.gvcf.gz" \
                --output_gvcf_parent2 "variants_{name_parent2}.gvcf.gz" \
                --output_vcf_child "variants_{name}.vcf.gz" \
                --output_vcf_parent1 "variants_{name_parent1}.vcf.gz" \
                --output_vcf_parent2 "variants_{name_parent2}.vcf.gz" \
                --sample_name_child "{name}" \
                --sample_name_parent1 "{name_parent1}" \
                --sample_name_parent2 "{name_parent2}" \
                --vcf_stats_report

            rm *.gvcf.gz*

            cd /
            tar czf "results_{name}.tar.gz" "/results_{name}"
            gsutil -m cp "results_{name}.tar.gz" {output_file}""")


if __name__ == "__main__":
    main()

