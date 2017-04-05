import svtools

import click

import sys
from tempfile import gettempdir

def print_support(ctx, param, value):
    '''Print information on obtaining support'''
    if not value or ctx.resilient_parsing:
                return
    support_string = 'For further help or to report a bug, please open an issue on the svtools repository: https://github.com/hall-lab/svtools/issues'
    click.echo(support_string)
    ctx.exit()


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(
        message='%(prog)s %(version)s',
        prog_name='svtools',
        version=svtools.__version__
        )
@click.option('--support',
        is_flag=True,
        callback=print_support,
        expose_value=False,
        is_eager=True,
        help='information on obtaining support'
        )
def cli():
    '''Comprehensive utilities to explore structural variation in genomes'''
    pass

@cli.command(
        short_help='sort N LUMPY VCF files into a single file',
        epilog='''Specify -t to override where temporary files are placed. Use -b to control the amount of memory required.
This will vary depending on the number of lines in your input files.
VCF files may be gzipped and the -f argument is available for convenience.'''
    )
@click.option('-f', '--vcf-list',
        metavar='<FILE>',
        help='file containing a line-delimited list of VCF files to combine and sort'
        )
@click.option('-r', '--include-reference',
        required=False,
        is_flag=True,
        default=False,
        help='whether or not to include homozygous reference or missing calls in the output.'
        )
@click.option('-t', '--tempdir',
        metavar='<DIRECTORY_PATH>',
        default=gettempdir(),
        help='temporary directory'
        )
@click.option('-b', '--batchsize',
        metavar='<INT>',
        type=int,
        default=200,
        help='number of files to sort in batch')
@click.argument('vcf_files',
    metavar='[<VCF> [<VCF> ...]]', #NOTE Setting this explicitly to match argparse
    type=list,
    nargs=-1,
    required=False,
    )
def lsort(vcf_list, include_reference, tempdir, batchsize, vcf_files):
    from svtools.lsort import Lsort
    if vcf_list:
        with open(vcf_list, 'r') as vcf_list_file:
            for line in vcf_list_file:
                file_name = line.rstrip()
                vcf_files.append(file_name)

    if not vcf_files:
        raise click.UsageError('No input files provided.')
    sorter = Lsort(vcf_files, tempdir=tempdir, batchsize=batchsize, include_ref=include_reference)
    sorter.execute()

@cli.command(
        short_help='merge LUMPY calls inside a single file from svtools lsort',
        epilog='Note that if both slop parameters are set then the maximum is used.'
        )
@click.option('-i', '--inFile',
        metavar='<FILE>',
        required=True,
        help='a sorted VCF file generated by svtools lsort. Each INFO field must contain an SNAME tag containing the sample name (e.g. SNAME=SAMPLE_NAME)'
        )
@click.option('-p', '--percent-slop',
        metavar='<FLOAT>',
        type=float,
        default=0.0,
        help='increase the the breakpoint confidence interval both up and down stream by a given proportion of the original size'
        )
@click.option('-f', '--fixed-slop',
        metavar='<INT>',
        type=int,
        default=0,
        help='increase the the breakpoint confidence interval both up and down stream by a given fixed size'
        )
@click.option('--sum',
        'use_product',
        is_flag=True,
        flag_value=False,
        default=True,
        help='calculate breakpoint PDF and position using sum algorithm instead of product'
        )
@click.option('-g',
        'include_genotypes',
        is_flag=True,
        default=False,
        help='include original genotypes in output. When multiple variants are merged, the last will dictate the genotype field')
def lmerge(infile, percent_slop, fixed_slop, use_product, include_genotypes):
    from svtools.lmerge import l_cluster_by_line
    l_cluster_by_line(infile,
            percent_slop=percent_slop,
            fixed_slop=fixed_slop,
            use_product=use_product,
            include_genotypes=include_genotypes
            )

@cli.command(short_help='paste VCFs from multiple samples',
        epilog='''VCF files may be gzipped. If the -m argument is omitted then the first file in the list of files in --vcf-list is treated as the master.'''
)
@click.option('-f', '--vcf-list',
        metavar='<FILE>',
        required=True,
        help='file containing a line-delimited list of VCF files to paste'
        )
@click.option('-m', '--master',
        metavar='<VCF>',
        default=None,
        help='VCF file to set first 8 columns of variant info (otherwise first file in --vcf-list)'
        )
@click.option('-q', '--sum-quals',
        required=False,
        is_flag=True,
        flag_value=True,
        help='sum QUAL scores of input VCFs as output QUAL score'
        )
def vcfpaste(vcf_list, master, sum_quals):
    import svtools.vcfpaste
    paster = Vcfpaste(vcf_list, master=master, sum_quals=sum_quals)

@cli.command(short_help='add copynumber information using cnvnator-multi',
        epilog='''As this program runs cnvnator-multi you must provide its location and must remember to have the ROOT package installed and properly configured. The input VCF file may be gzipped. If the input VCF file is omitted then the tool reads from stdin. Note that the coordinates file must end with a line containing the word exit.'''
        )
@click.option('-c', '--coordinates',
        metavar='<FILE>',
        type=click.Path(exists=True, readable=True),
        required=True,
        help='file containing coordinate for which to retrieve copynumber'
        )
@click.option('-r', '--root',
        metavar='<FILE>',
        type=click.Path(exists=True, readable=True),
        required=True,
        help='CNVnator .root histogram file'
        )
@click.option('-w', '--window',
        metavar='<INT>',
        type=int,
        required=True,
        help='CNVnator window size'
        )
@click.option('-s', '--sample',
        metavar='<STRING>',
        type=str,
        required=True,
        help='sample to annotate'
        )
@click.option('--cnvnator',
        metavar='<PATH>',
        type=click.Path(exists=True),
        required=True,
        help='path to cnvnator-multi binary'
        )
@click.option('-i', '--input',
        metavar='<VCF>',
        default=None,
        help='VCF input [default: stdin]'
        )
@click.option('-o', '--output',
        metavar='<PATH>',
        type=click.File('w'),
        default=click.get_text_stream('stdout'),
        help='output VCF to write [default: stdout]'
        )
def copynumber(input, sample, root, window, output, cnvnator, coordinates):
    import svtools.copynumber
    import svtools.utils as su
    with su.InputStream(input) as stream:
        sv_readdepth(stream, sample, root, window, output, cnvnator, coordinates)

@cli.command(short_help='compute genotype of structural variants based on breakpoint depth')
@click.option('-i', '--input_vcf',
        metavar='<VCF>',
        help='VCF input [default: stdin]'
        )
@click.option('-o', '--output_vcf',
        metavar='<VCF>',
        help='output VCF to write [default: stdout]'
        )
@click.option('-B', '--bam',
        metavar='<BAM>',
        type=click.Path(exists=True, readable=True),
        required=True,
        help='BAM or CRAM file(s), comma-separated if genotyping multiple BAMs'
        )
@click.option('-l', '--lib_info',
        metavar='<PATH>',
        type=click.Path(writable=True, readable=True),
        required=False,
        help='create/read JSON file of library information'
        )
@click.option('-m', '--min_aligned',
        type=int,
        metavar='<INT>',
        required=False,
        default=20,
        show_default=True,
        help='minimum number of aligned bases to consider read as evidence'
        )
@click.option('-n','num_samp',
        type=int,
        metavar='<INT>',
        required=False,
        default=1000000,
        show_default=True,
        help='number of pairs to sample from BAM file for building insert size distribution'
        )
@click.option('--split_weight',
        type=float,
        metavar='<FLOAT>',
        required=False,
        default=1.0,
        show_default=True,
        help='weight for split reads'
        )
@click.option('--disc_weight',
        type=float,
        metavar='<FLOAT>',
        required=False,
        default=1.0,
        show_default=True,
        help='weight for discordant paired-end reads'
        )
@click.option('-w', '--write_alignment',
        type=click.Path(writable=True),
        metavar='<PATH>',
        required=False,
        default=None,
        help='write relevant reads to BAM file'
        )
def genotype(**kwargs):
    import svtools.genotype
    genotyper = svtools.genotype.GenotypeVariants()
    opts = list()
    optlut = genotyper.svtyper_option_lut()
    for variable, value in kwargs.iteritems():
        if value not in (False, None):
            opts.extend([optlut[variable], str(value)])
    genotyper.run_cmd_with_options(opts)

@cli.command(short_help='add allele frequency information to a VCF file',
        epilog='Specify the path to an (optionally) bgzipped VCF. If no file is specified then input is read from stdin.'
        )
@click.argument('input_vcf',
        metavar='<VCF>',
        type=click.Path(exists=True, readable=True),
        default=None,
        required=False
        )

def afreq(input_vcf):
    import svtools.afreq
    import svtools.utils as su
    with su.InputStream(input_vcf) as input_stream:
        updater = svtools.afreq.UpdateInfo(input_stream)
        updater.execute()

@cli.command(short_help='convert a BEDPE file to BED12 format for viewing in IGV or the UCSC browser',
        epilog='The input BEDPE file may be gzipped. If the input file is omitted then input is read from stdin. Output is written to stdout.'
        )
@click.option('-i', '--input',
        metavar='<BEDPE>',
        type=click.Path(exists=True),
        default=None,
        help='BEDPE input file [default: stdin]'
        )
@click.option('-o', '--output',
        metavar='<BED12>',
        type=click.Path(),
        default=None,
        help='Output BED12 to write [default: stdout]'
        )
@click.option('-n', '--name',
        metavar='<STRING>',
        type=str,
        default='BEDPE',
        help="The name of the track. Default is 'BEDPE'"
        )
@click.option('-d', '--maxdist',
        metavar='<INT>',
        default=1000000,
        type=int,
        help='The minimum distance for drawing intrachromosomal features as if they are interchromosomal (i.e., without a line spanning the two footprints). Default is 1Mb.'
        )

def bedpetobed12(input, output, name, maxdist):
    import svtools.bedpetobed12
    import svtools.utils as su
    with su.InputStream(input) as stream:
        processBEDPE(stream, name, maxdist, output)

@cli.command(short_help='convert a BEDPE file to VCF',
        epilog='The input BEDPE file can be gzipped if it is specified explicitly.'
        )
@click.option('-i', '--input',
        metavar='<BEDPE>',
        default=None,
        help='BEDPE input [default: stdin]'
        )
@click.option('-o', '--output',
        metavar='<VCF>',
        type=click.File('w'),
        default=sys.stdout,
        help='Output VCF to write [default: stdout]'
        )
def bedpetovcf(input, output):
    import svtools.bedpetovcf
    import svtools.utils as su
    with su.InputStream(input) as stream:
        bedpeToVcf(stream, output)

@cli.command(short_help='convert a VCF file to BEDPE',
        epilog='The input VCF file can be gzipped if it is specified explicitly.'
        )
@click.option('-i', '--input',
        metavar='<VCF>',
        default=None,
        help='VCF input [default: stdin]'
        )
@click.option('-o', '--output',
        metavar='<BEDPE>',
        type=click.File('w'),
        default=sys.stdout,
        help='Output BEDPE to write [default: stdout]'
        )
def vcftobedpe(input, output):
    import svtools.vcftobedpe
    import svtools.utils as su
    with su.InputStream(input) as stream:
        vcfToBedpe(stream, output)

@cli.command(short_help='sort a VCF file')
@click.option('-i', '--input',
        metavar='<VCF>',
        type=click.Path(exists=True),
        help='VCF file to sort [default: stdin]'
        )
@click.option('-o', '--output',
        metavar='<VCF>',
        type=click.Path(),
        help='output file to write to [default: stdout]'
        )
def vcfsort(input, output):
    import svtools.vcfsort
    sorter = svtools.vcfsort.VcfSort()
    sorter.run_cmd_with_options(filter(lambda x: x is not None, [input, output]))

@cli.command(short_help='sort a BEDPE file')
@click.option('-i', '--input',
        metavar='<BEDPE>',
        type=click.Path(exists=True),
        help='BEDPE file to sort [default: stdin]'
        )
@click.option('-o', '--output',
        metavar='<BEDPE>',
        type=click.Path(),
        help='output file to write to [default: stdout]'
        )
def bedpesort(input, output):
    import svtools.bedpesort
    sorter = svtools.bedpesort.BedpeSort()
    sorter.run_cmd_with_options(filter(lambda x: x is not None, [input, output]))

@cli.command(short_help='cluster and prune a BEDPE file by position based on allele frequency',
        epilog='The input BEDPE file can be gzipped if it is specified explicitly.'
        )
@click.argument('input',
        metavar='<BEDPE>',
        default=None,
        required=False,
        #help='BEDPE file to read. If \'-\' or absent then defaults to stdin.'
        )
@click.option('-o', '--output',
        metavar='<BEDPE>',
        type=click.File('w'),
        default=sys.stdout,
        help='output bedpe to write [default: stdout]'
        )
@click.option('-d', '--distance',
        metavar='<INT>',
        type=int,
        default=50,
        show_default=True,
        help='max separation distance (bp) of adjacent loci in cluster'
        )
@click.option('-e', '--eval-param',
        metavar='<STRING>',
        type=str,
        help='evaluating parameter for choosing best bedpe in a cluster(e.g. af=AlleleFrequency [default: af])'
        )
@click.option('-s', '--is-sorted',
        is_flag=True,
        default=False,
        show_default=True,
        help='specify if an input file is sorted. Sort with svtools bedpesort.'
        )

def prune(input, output, distance, eval_param, is_sorted):
    import svtools.prune
    import svtools.utils as su
    with su.InputStream(args.input) as stream:
        pruner = svtools.prune.Pruner(distance, eval_param)
        pruner.cluster_bedpe(stream, output, is_sorted)
# 
@cli.command(short_help='look for variants common between two BEDPE files')
@click.option("-a", "--aFile",
        type=click.Path(exists=True),
        metavar='<BEDPE>',
        help="pruned, merged BEDPE (A file) or standard input (-a stdin)."
        )
@click.option("-b", "--bFile",
        type=click.Path(exists=True),
        metavar='<BEDPE>',
        help="pruned merged BEDPE (B file) (-b stdin). For pruning use svtools prune"
        )
@click.option('-d', '--distance',
        metavar='<INT>',
        type=int,
        default=50,
        show_default=True,
        help='max separation distance (bp) of adjacent loci between bedpe files')
@click.option("-c", "--cohort",
        metavar='<STRING>',
        type=str,
        default=None,
        help="cohort name to add information of matching variants [default:bFile]"
        )
@click.option('-o', '--output',
        type=click.File('w'),
        metavar='<BEDPE>',
        default=sys.stdout,
        help='output BEDPE to write [default: stdout]'
        )
def varlookup(afile, bfile, distance, cohort, output):
    import svtools.varlookup
    pass_prefix = "#"
    if afile == None:
        if sys.stdin.isatty():
            sys.stderr.write('Please stream in input to this command or specify the file to read\n')
            sys.exit(1)
        else:
            afile = sys.stdin

    try:
        varLookup(afile, bfile, output, max_distance, pass_prefix, cohort_name)
    except IOError as err:
        sys.stderr.write("IOError " + str(err) + "\n");

# @cli.command(short_help="post-VQSR data pipeline")
# def sv_classifier():
#     import svtools.sv_classifier

if __name__ == '__main__':
    try:
        cli(prog_name='svtools')
    except IOError as e:
        if e.errno == errno.EPIPE:
            sys.exit(141)
