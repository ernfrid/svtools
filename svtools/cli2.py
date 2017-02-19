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

# @cli.command(short_help="post-VQSR data pipeline")
# def vcfpaste():
#     import svtools.vcfpaste
# 
# @cli.command(short_help="post-VQSR data pipeline")
# def copynumber():
#     import svtools.copynumber
# 
# @cli.command(short_help="post-VQSR data pipeline")
# def afreq():
#     import svtools.afreq
# 
# @cli.command(short_help="post-VQSR data pipeline")
# def bedpetobed12():
#     import svtools.bedpetobed12
# 
# @cli.command(short_help="post-VQSR data pipeline")
# def bedpetovcf():
#     import svtools.bedpetovcf
# 
# @cli.command(short_help="post-VQSR data pipeline")
# def vcftobedpe():
#     import svtools.vcftobedpe

@cli.command(short_help='sort a VCF file')
@click.option('-i', '--input',
              type=click.Path(exists=True),
              help='VCF file to sort (default: stdin)')
@click.option('-o', '--output',
              type=click.Path(),
              help='output file to write to (default: stdout)')
def vcfsort(input, output):
    import svtools.vcfsort
    sorter = svtools.vcfsort.VcfSort()
    sorter.run_cmd_with_options(filter(lambda x: x is not None, [input, output]))

# @cli.command(short_help="post-VQSR data pipeline")
# def bedpesort():
#     import svtools.bedpesort
# 
# @cli.command(short_help="post-VQSR data pipeline")
# def genotype():
#     import svtools.genotype
# 
# @cli.command(short_help="post-VQSR data pipeline")
# def prune():
#     import svtools.prune
# 
# @cli.command(short_help="post-VQSR data pipeline")
# def varlookup():
#     import svtools.varlookup
# 
# @cli.command(short_help="post-VQSR data pipeline")
# def sv_classifier():
#     import svtools.sv_classifier

if __name__ == '__main__':
    try:
        cli(prog_name='svtools')
    except IOError as e:
        if e.errno == errno.EPIPE:
            sys.exit(141)
