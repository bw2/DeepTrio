
#### Make Examples

```
$ /deepvariant/bazel-bin/deeptrio/make_examples --help

Step one of DeepVariant: creates tf.Example protos for training/calling.
flags:

/tmp/Bazel.runfiles_n4r7ed86/runfiles/com_google_deepvariant/deeptrio/make_examples.py:
  --alt_aligned_pileup: <none|base_channels|diff_channels>: Include alignments of reads against each candidate alternate allele in the pileup image. "none" turns this feature off. The default is "none".Options: "none",
    "base_channels","diff_channels"
    (default: 'none')
  --candidates: Candidate DeepVariantCalls in tfrecord format. For DEBUGGING.
    (default: '')
  --confident_regions: Regions that we are confident are hom-ref or a variant in BED format. In BED or other equivalent format, sorted or unsorted. Contig names must match those of the reference genome.
    (default: '')
  --customized_classes_labeler_classes_list: A comma-separated list of strings that defines customized class labels for variants. This is only set when labeler_algorithm is customized_classes_labeler.
    (default: '')
  --customized_classes_labeler_info_field_name: The name from the INFO field of VCF where we should get the customized class labels from. This is only set when labeler_algorithm is customized_classes_labeler.
    (default: '')
  --downsample_fraction_child: If not 0.0 must be a value between 0.0 and 1.0. Reads will be kept (randomly) with a probability of downsample_fraction from the input child BAM. This argument makes it easy to create examples as though the
    input BAM had less coverage.
    (default: '0.0')
    (a number)
  --downsample_fraction_parents: If not 0.0 must be a value between 0.0 and 1.0. Reads will be kept (randomly) with a probability of downsample_fraction from the input parent BAMs. This argument makes it easy to create examples as though
    the input BAMs had less coverage.
    (default: '0.0')
    (a number)
  --examples: Required. Path to write tf.Example protos in TFRecord format. This is the root path, as the actual files will be written to this path + suffix, where suffix corresponds to sample.
  --exclude_regions: Optional. Space-separated list of regions we want to exclude from processing. Elements can be region literals (e.g., chr20:10-20) or paths to BED/BEDPE files. Region exclusion happens after processing the --regions
    argument, so --region 20 --exclude_regions 20:100 does everything on chromosome 20 excluding base 100
    (default: '')
  --gvcf: Optional. Path where we should write gVCF records in TFRecord of Variant proto format.
    (default: '')
  --gvcf_gq_binsize: Bin size in which to quantize gVCF genotype qualities. Larger bin size reduces the number of gVCF records at a loss of quality granularity.
    (default: '5')
    (an integer)
  --hts_block_size: Sets the htslib block size. Zero or negative uses default htslib setting; larger values (e.g. 1M) may be beneficial for using remote files. Currently only applies to SAM/BAM reading.
    (default: '134217728')
    (an integer)
  --hts_logging_level: Sets the htslib logging threshold.
    (default: 'HTS_LOG_WARNING')
  --[no]keep_duplicates: If True, keep duplicate reads.
    (default: 'false')
  --[no]keep_secondary_alignments: If True, keep reads marked as secondary alignments.
    (default: 'false')
  --[no]keep_supplementary_alignments: If True, keep reads marked as supplementary alignments.
    (default: 'false')
  --labeler_algorithm: Algorithm to use to label examples in training mode. Must be one of the LabelerAlgorithm enum values in the DeepTrioOptions proto.
    (default: 'haplotype_labeler')
  --logging_every_n_candidates: Print out the log every n candidates. The smaller the number, the more frequent the logging information emits.
    (default: '100')
    (an integer)
  --max_reads_per_partition: The maximum number of reads per partition that we consider before following processing such as sampling and realigner.
    (default: '1500')
    (an integer)
  --min_base_quality: Minimum base quality. This field indicates that we are enforcing a minimum base quality score for alternate alleles. Alternate alleles will only be considered if all bases in the allele have a quality greater than
    min_base_quality.
    (default: '10')
    (an integer)
  --min_mapping_quality: By default, reads with any mapping quality are kept. Setting this field to a positive integer i will only keep reads that have a MAPQ >= i. Note this only applies to aligned reads.
    (default: '5')
    (an integer)
  --mode: Mode to run. Must be one of calling or training
  --multi_allelic_mode: How to handle multi-allelic candidate variants. For DEBUGGING
    (default: '')
  --[no]parse_sam_aux_fields: If True, auxiliary fields of the SAM/BAM/CRAM records are parsed.
    (default: 'false')
  --partition_size: The maximum number of basepairs we will allow in a region before splittingit into multiple smaller subregions.
    (default: '1000')
    (an integer)
  --pileup_image_height_child: Height for the child pileup image. If 0, uses the default height
    (default: '0')
    (an integer)
  --pileup_image_height_parent: Height for the parent pileup image. If 0, uses the default height
    (default: '0')
    (an integer)
  --pileup_image_width: Width for the pileup image. If 0, uses the default width
    (default: '0')
    (an integer)
  --reads: Required. Aligned, sorted, indexed BAM file containing the reads we want to call. Should be aligned to a reference genome compatible with --ref.
  --reads_parent1: Required. Aligned, sorted, indexed BAM file containing parent 1 reads of the person we want to call. Should be aligned to a reference genome compatible with --ref.
  --reads_parent2: Aligned, sorted, indexed BAM file containing parent 2 reads of the person we want to call. Should be aligned to a reference genome compatible with --ref.
  --[no]realign_reads: If True, locally realign reads before calling variants. Reads longer than 500 bp are never realigned.
    (default: 'true')
  --ref: Required. Genome reference to use. Must have an associated FAI index as well. Supports text or gzipped references. Should match the reference used to align the BAM file provided to --reads.
  --regions: Optional. Space-separated list of regions we want to process. Elements can be region literals (e.g., chr20:10-20) or paths to BED/BEDPE files.
    (default: '')
  --sample_name: Sample name to use for our sample_name in the output Variant/DeepVariantCall protos. If not specified, will be inferred from the header information from --reads.
    (default: '')
  --sample_name_parent1: Parent1 Sample name to use for our sample_name in the output Variant/DeepVariantCall protos. If not specified, will be inferred from the header information from --reads_parent1.
    (default: '')
  --sample_name_parent2: Parent2 Sample name to use for our sample_name in the output Variant/DeepVariantCall protos. If not specified, will be inferred from the header information from --reads_parent2.
    (default: '')
  --sample_name_to_call: Optional - if not set, default to the value in --sample_name. The default is set to be backward compatible. If set, it has to match one of --sample_name, --sample_name_parent1, or --sample_name_parent2. This is
    the sample that we call variants on.
  --select_variant_types: If provided, should be a whitespace-separated string of variant types to keep when generating examples. Permitted values are "snps", "indels", "multi-allelics", and "all", which select bi-allelic snps, bi-allelic
    indels, multi-allelic variants of any type, and all variants, respectively. Multiple selectors can be specified, so that --select_variant_types="snps indels" would keep all bi-allelic SNPs and indels
  --sequencing_type: A string representing input bam file sequencing_type. Permitted values are "WGS" and "WES", which represent whole genome sequencing and whole exome sequencing, respectively. This flag is experimental and is not
    currently being used.
  --[no]sort_by_haplotypes: If True, reads are sorted by haplotypes (using HP tag), parse_sam_aux_fields has to be set for this to work.
    (default: 'false')
  --task: Task ID of this task
    (default: '0')
    (an integer)
  --training_random_emit_ref_sites: If > 0, emit extra random reference examples with this probability.
    (default: '0.0')
    (a number)
  --truth_variants: Tabix-indexed VCF file containing the truth variant calls for this labels which we use to label our examples.
    (default: '')
  --types_to_alt_align: <indels|all>: When --alt_aligned_pileup is not none, this flag determines whether to align to the alt alleles only for indels or for all variant types including SNPs. Ignored if --alt_aligned_pileup is "none". This
    flag is experimental and is not compatible with the pre-trained release models.
    (default: 'indels')
  --[no]use_original_quality_scores: If True, base quality scores are read from OQ tag.
    (default: 'false')
  --[no]use_ref_for_cram: If true, use the --ref argument as the reference file for the CRAM file passed to --reads.  In this case, it is required that the reference file be located on a local POSIX filesystem.
    (default: 'false')
  --variant_caller: The caller to use to make examples. Must be one of the VariantCaller enum values in the DeepTrioOptions proto.
    (default: 'very_sensitive_caller')
  --vsc_allele_fraction_trio_coefficient: Coefficient that is applied to vsc_min_fraction_snps and vsc_min_fraction_indels for candidate generation for trio calling.
    (default: '0.67')
    (a number)
  --vsc_min_count_indels: Indel alleles occurring at least this many times in our AlleleCount will be advanced as candidates.
    (default: '2')
    (an integer)
  --vsc_min_count_snps: SNP alleles occurring at least this many times in our AlleleCount will be advanced as candidates.
    (default: '2')
    (an integer)
  --vsc_min_fraction_indels: Indel alleles occurring at least this fraction of all counts in our AlleleCount will be advanced as candidates.
    (default: '0.06')
    (a number)
  --vsc_min_fraction_snps: SNP alleles occurring at least this fraction of all counts in our AlleleCount will be advanced as candidates.
    (default: '0.12')
    (a number)
  --[no]write_run_info: If True, write out a MakeExamplesRunInfo proto besides our examples in text_format.
    (default: 'false')
```

#### Call Variants

```
$ /deepvariant/bazel-bin/deepvariant/call_variants --help

Code for calling variants with a trained DeepVariant model.
flags:

/tmp/Bazel.runfiles_8iyhn5rs/runfiles/com_google_deepvariant/deepvariant/call_variants.py:
  --batch_size: Number of candidate variant tensors to batch together during inference. Larger batches use more memory but are more computational efficient.
    (default: '512')
    (an integer)
  --checkpoint: Required. Path to the TensorFlow model checkpoint to use to evaluate candidate variant calls.
  --config_string: String representation of a tf.ConfigProto message, with comma-separated key: value pairs, such as "allow_soft_placement: True". The value can itself be another message, such as "gpu_options:
    {per_process_gpu_memory_fraction: 0.5}".
  --[no]debugging_true_label_mode: If true, read the true labels from examples and add to output. Note that the program will crash if the input examples do not have the label field. When true, this will also fill everything when
    --include_debug_info is set to true.
    (default: 'false')
  --examples: Required. tf.Example protos containing DeepVariant candidate variants in TFRecord format, as emitted by make_examples. Can be a comma-separated list of files, and the file names can contain wildcard characters.
  --execution_hardware: When in cpu mode, call_variants will not place any ops on the GPU, even if one is available. In accelerator mode call_variants validates that at least some hardware accelerator (GPU/TPU) was available for us. This
    option is primarily for QA purposes to allow users to validate their accelerator environment is correctly configured. In auto mode, the default, op placement is entirely left up to TensorFlow.  In tpu mode, use and require TPU.
    (default: 'auto')
  --gcp_project: Project name for the Cloud TPU-enabled project. If not specified, we will attempt to automatically detect the GCE project from metadata.
  --[no]include_debug_info: If true, include extra debug info in the output.
    (default: 'false')
  --kmp_blocktime: Value to set the KMP_BLOCKTIME environment variable to for efficient MKL inference. See https://www.tensorflow.org/performance/performance_guide for more information. The default value is 0, which provides the best
    performance in our tests. Set this flag to "" to not set the variable.
    (default: '0')
  --master: GRPC URL of the master (e.g. grpc://ip.address.of.tpu:8470). You must specify either this flag or --tpu_name.
  --max_batches: Max. batches to evaluate. Defaults to all.
    (an integer)
  --model_name: The name of the model architecture of --checkpoint.
    (default: 'inception_v3')
  --num_mappers: Number of parallel mappers to create for examples.
    (default: '48')
    (an integer)
  --num_readers: Number of parallel readers to create for examples.
    (default: '8')
    (an integer)
  --outfile: Required. Destination path where we will write output candidate variants with additional likelihood information in TFRecord format of CallVariantsOutput protos.
  --tpu_name: Name of the Cloud TPU for Cluster Resolvers. You must specify either this flag or --master. An empty value corresponds to no Cloud TPU. See
    https://www.tensorflow.org/api_docs/python/tf/distribute/cluster_resolver/TPUClusterResolver
  --tpu_zone: GCE zone where the Cloud TPU is located in. If not specified, we will attempt to automatically detect the GCE project from metadata.
  --[no]use_openvino: Use Intel OpenVINO as backend.
    (default: 'false')
  --[no]use_tpu: Use tpu if available.
    (default: 'false')
```

#### Postprocess Variants

```
$ /deepvariant/bazel-bin/deepvariant/postprocess_variants

Postprocess output from call_variants to produce a VCF file.
flags:

/tmp/Bazel.runfiles_2deujfzj/runfiles/com_google_deepvariant/deepvariant/postprocess_variants.py:
  --cnn_homref_call_min_gq: All CNN RefCalls whose GQ is less than this value will have ./. genotype instead of 0/0.
    (default: '20.0')
    (a number)
  --[no]group_variants: If using vcf_candidate_importer and multi-allelic sites are split across multiple lines in VCF, set to False so that variants are not grouped when transforming CallVariantsOutput to Variants.
    (default: 'true')
  --gvcf_outfile: Optional. Destination path where we will write the Genomic VCF output.
  --infile: Required. Path(s) to CallVariantOutput protos in TFRecord format to postprocess. These should be the complete set of outputs for call_variants.py.
  --multi_allelic_qual_filter: The qual value below which to filter multi-allelic variants.
    (default: '1.0')
    (a number)
  --nonvariant_site_tfrecord_path: Optional. Path(s) to the non-variant sites protos in TFRecord format to convert to gVCF file. This should be the complete set of outputs from the --gvcf flag of make_examples.py.
  --[no]only_keep_pass: If True, only keep PASS calls.
    (default: 'false')
  --outfile: Required. Destination path where we will write output variant calls in VCF format.
  --qual_filter: Any variant with QUAL < qual_filter will be filtered in the VCF file.
    (default: '1.0')
    (a number)
  --ref: Required. Genome reference in FAI-indexed FASTA format. Used to determine the sort order for the emitted variants and the VCF header.
  --sample_name: Optional. If set, this will only be used if the sample name cannot be determined from the CallVariantsOutput or non-variant sites protos.
  --[no]use_multiallelic_model: If True, use a specialized model for genotype resolution of multiallelic cases with two alts.
    (default: 'false')
  --[no]vcf_stats_report: Optional. Output a visual report (HTML) of statistics about the output VCF at the same base path given by --outfile.
    (default: 'true')

```
