FROM gcr.io/deepvariant-docker/deepvariant:1.1.0

WORKDIR /

#RUN git clone https://github.com/tensorflow/tensorflow.git
#RUN cd /tensorflow && touch .tf_configure.bazelrc && bazel build

RUN git clone https://github.com/google/deepvariant.git
RUN cd /deepvariant && ./build-prereq.sh
RUN cd /deepvariant && ./build_release_binaries.sh


RUN apt-get update && apt-get install -y libncursesw5-dev libgdbm-dev libc6-dev zlib1g-dev libsqlite3-dev libssl-dev openssl libffi-dev


# install htslib  --  install in downstream images with:
#     COPY --from=weisburd/base-bam-tools:latest  /usr/local/bin/tabix /usr/local/bin/tabix
#     COPY --from=weisburd/base-bam-tools:latest  /usr/local/bin/htsfile /usr/local/bin/htsfile
#     COPY --from=weisburd/base-bam-tools:latest  /usr/local/bin/bgzip /usr/local/bin/bgzip
#     COPY --from=weisburd/base-bam-tools:latest  /usr/local/bin/samtools /usr/local/bin/samtools
ENV SAMTOOLS_VERSION="1.9"
RUN wget https://github.com/samtools/htslib/releases/download/${SAMTOOLS_VERSION}/htslib-${SAMTOOLS_VERSION}.tar.bz2 \
	&& tar xjf htslib-${SAMTOOLS_VERSION}.tar.bz2 \
	&& rm htslib-${SAMTOOLS_VERSION}.tar.bz2 \
	&& cd htslib-${SAMTOOLS_VERSION} \
	&& ./configure \
	&& make \
	&& make install \
	&& make clean

# install samtools  --  install in downstream images with:
#     COPY --from=weisburd/base-bam-tools:latest /usr/local/bin/samtools /usr/local/bin/samtools
RUN wget https://github.com/samtools/samtools/releases/download/${SAMTOOLS_VERSION}/samtools-${SAMTOOLS_VERSION}.tar.bz2 \
	&& tar xjf samtools-${SAMTOOLS_VERSION}.tar.bz2 \
	&& rm samtools-${SAMTOOLS_VERSION}.tar.bz2 \
	&& cd samtools-${SAMTOOLS_VERSION} \
	&& ./configure \
	&& make \
	&& make install \
	&& make clean

#RUN apt update && apt install -y emacs

# Executables (key options):
#    /deepvariant/bazel-bin/deeptrio/make_examples
#           --mode calling
#           --ref: Required. Genome reference to use. Must have an associated FAI index as well
#           --reads Aligned, sorted, indexed BAM file containing the reads we want to call.
#           --reads_parent1: Required. Aligned, sorted, indexed BAM file containing parent1 reads
#           --reads_parent2: Optional. Aligned, sorted, indexed BAM file containing parent2 reads
#           --regions: Optional. Space-separated list of regions we want to process. Elements can be region literals (e.g., chr20:10-20) or paths to BED/BEDPE files.
#           --examples: Required. Path to write tf.Example protos in TFRecord format.
#
#    /deepvariant/bazel-bin/deepvariant/call_variants
#           --checkpoint:  Required. Path to the TensorFlow model checkpoint to use to evaluate candidate variant calls.
#           --examples:  Required. tf.Example protos containing DeepVariant candidate variants in TFRecord format, as emitted by make_examples. Can be a comma-separated list of files, and the file names can contain wildcard characters.
#           --outfile: Required.  Destination path where we will write output candidate variants with additional likelihood information in TFRecord format of CallVariantsOutput protos.
#           --batch_size: Number of candidate variant tensors to batch together during inference. Larger batches use more memory but are more computational efficient. (default: '512')
#           --execution_hardware: When in cpu mode, call_variants will not place any ops on the GPU, even if one is available. In accelerator mode call_variants validates that at least some hardware accelerator (GPU/TPU) was available for us. This option is primarily for QA purposes to allow users to validate their accelerator environment is correctly configured. In auto mode, the default, op placement is entirely left up to TensorFlow.  In tpu mode, use and require TPU. (default: 'auto')
#           --gcp_project: Project name for the Cloud TPU-enabled project. If not specified, we will attempt to automatically detect the GCE project from metadata.
#           --[no]use_openvino: Use Intel OpenVINO as backend. (default: 'false')
#
#    /deepvariant/bazel-bin/deepvariant/postprocess_variants
#           --ref: Required. Genome reference to use. Must have an associated FAI index as well
#           --infile: Required. Path(s) to CallVariantOutput protos in TFRecord format to postprocess. These should be the complete set of outputs for call_variants.py.
#           --outfile: Required. Destination path where we will write output variant calls in VCF format.
#           --qual_filter: Any variant with QUAL < qual_filter will be filtered in the VCF file. (default: '1.0')
#           --[no]vcf_stats_report: Optional. Output a visual report (HTML) of statistics about the output VCF at the same base path given by --outfile. (default: true)
#           --[no]use_multiallelic_model: If True, use a specialized model for genotype resolution of multiallelic cases with two alts.  (default: 'false')
