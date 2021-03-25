version 1.0

workflow DeepTrio {

    input {
        File ref_fasta
        File ref_fasta_fai

        File reads
        File reads_index
        File parent1_reads
        File parent1_reads_index
        File parent2_reads
        File parent2_reads_index
    }

    call MakeExamples {
        input:
            ref_fasta=ref_fasta,
            ref_fasta_fai=ref_fasta_fai,
            reads=reads,
            reads_index=reads_index,
            parent1_reads=parent1_reads,
            parent1_reads_index=parent1_reads_index,
            parent2_reads=parent2_reads,
            parent2_reads_index=parent2_reads_index
    }

    output {
        File examples = MakeExamples.examples
    }
}

## gs://deepvariant/models/DeepTrio/1.1.0/
#
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

task MakeExamples {

    input {
        File ref_fasta
        File ref_fasta_fai
        File reads
        File reads_index
        File parent1_reads
        File parent1_reads_index
        File parent2_reads
        File parent2_reads_index

        String name = sub(basename(reads), "\\.bam$|\\.cram$", "")

        Int disk_size = ceil(size(reads, "GB") + size(parent1_reads, "GB") + size(parent2_reads, "GB") + 15)
    }

    # time ./make_examples --ref /p1/ref/GRCh38/hg38.fa --reads /p1/data/GRCh38/syndip/genomes/CHM1_CHM13_2.chr22.bam --reads_parent1 /p1/data/GRCh38/syndip/genomes/CHM1_CHM13_2.chr22.bam --reads_parent2 /p1/data/GRCh38/syndip/genomes/CHM1_CHM13_2.chr22.bam --examples examples --mode CALLING --sample_name a  --regions chr22:10510022-11510022

    command {
        echo --------------; echo "Start - time: $(date)"; set -euxo pipefail; ls -lhtr; lscpu | grep 'CPU\|Model'; free -h; df -kh; uptime; find /cromwell*/ -type f | xargs ls -lhSr; echo --------------

        mkdir examples

        /opt/deepvariant/bin/deeptrio/make_examples \
            --mode calling \
            --ref ~{ref_fasta} \
            --reads ~{reads} \
            --reads_parent1 ~{parent1_reads} \
            --reads_parent2 ~{parent2_reads} \
            --sample_name ~{name} \
            --sample_name_to_call ~{name} \
            --examples examples

        tar czf examples-~{name}.tar.gz examples
        echo --------------; ls -lhtr; lscpu | grep 'CPU\|Model'; free -h; df -kh; uptime; set +xe; echo "Done - time: $(date)"; echo --------------
    }

    output {
        File examples = "examples-~{name}.tar.gz"
    }

    runtime {
        docker: "weisburd/deepvariant@sha256:5badeaf0485033b8606fa67b791ca5b35d5a3a92e8a2811f954733789b861f33"
        cpu: 1
        preemptible: 1
        disks: "local-disk ${disk_size} HDD"
        #memory: "15 GB"
        #disks: "local-disk ${disk_size} LOCAL"
        #bootDiskSizeGb: 20
        #zones: "us-east1-b us-east1-c us-east1-d"
    }
}
