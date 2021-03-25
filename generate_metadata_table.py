
#%%
import dateutil
import collections
import hail as hl
import math
import pandas as pd
import os
import re
import tqdm

from metadata.gcloud_api_utils import get_genome_version_from_bam_or_cram_header
from metadata.rare_disease_metadata_utils import get_seqr_WGS_metadata_df, get_seqr_WES_metadata_df

#%%

df = get_seqr_WES_metadata_df().reset_index()

#%%

sherr_df = df[df.project_name.str.lower().str.contains("she")]

len(sherr_df)
#%%

sherr_df = sherr_df[~sherr_df.cram_path.isna() & ~sherr_df.cram_path.isna()]

len(sherr_df)
#%%

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

#%%

invidual_guid_to_row  = {}
for _, row in sherr_df.iterrows():
    invidual_guid_to_row[row.individual_guid] = row

len(invidual_guid_to_row)

#%%
trios = []

for _, row in sherr_df.iterrows():
    if row.father_guid:
        assert row.father_guid in invidual_guid_to_row
    if row.mother_guid:
        assert row.mother_guid in invidual_guid_to_row

    if row.father_guid and row.mother_guid:
        if row.affected != "Affected":
            #print and include unaffected trios as controls
            print(f"{row.individual_id} in {row.family_guid} is {row.affected}")

        trios.append((row, invidual_guid_to_row[row.mother_guid], invidual_guid_to_row[row.father_guid]))


#%%

output_rows = []
for proband, mother, father in trios:
    assert proband.genome_version in ("37", "38"), proband.genome_version
    hg_version = proband.genome_version.replace("37", "19")

    output_rows.append({
        "entity:participant_id": proband.individual_guid,
        "family_guid": row.family_guid,

        "individual_id": row.individual_id,
        "mother_id": mother.individual_id,
        "father_id": father.individual_id,

        "individual_affected": row.affected,
        "mother_affected": mother.affected,
        "father_affected": father.affected,

        "ref_fasta": f"gs://gcp-public-data--broad-references/hg{hg_version}/v0/Homo_sapiens_assembly{hg_version}.fasta",
        "ref_fasta_fai": f"gs://gcp-public-data--broad-references/hg{hg_version}/v0/Homo_sapiens_assembly{hg_version}.fasta.fai",
        "reads": proband.cram_path,
        "reads_index": proband.crai_path,
        "parent1_reads": mother.cram_path,
        "parent1_reads_index": mother.crai_path,
        "parent2_reads": father.cram_path,
        "parent2_reads_index": father.crai_path,
    })

#%%
output_df = pd.DataFrame(output_rows)
output_df.to_csv("trios.tsv", index=False, header=True, sep="\t")

#%%
