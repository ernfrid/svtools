from svtools.ui.subcommand import SubCommand
import sys, argparse

class Classify(SubCommand):
    def add_arguments_to_parser(self, parser):
        parser.add_argument('-i', '--input', metavar='<VCF>', default=None, help='VCF input')
        parser.add_argument('-o', '--output', metavar='<VCF>', dest='vcf_out', type=argparse.FileType('w'), default=sys.stdout, help='VCF output [stdout]')
        parser.add_argument('-g', '--gender', metavar='<FILE>', dest='gender', type=argparse.FileType('r'), required=True, default=None, help='tab delimited file of sample genders (male=1, female=2)\nex: SAMPLE_A\t2')
        parser.add_argument('-a', '--annotation', metavar='<BED>', dest='ae_path', type=str, default=None, help='BED file of annotated elements')
        parser.add_argument('-f', '--fraction', metavar='<FLOAT>', dest='f_overlap', type=float, default=0.9, help='fraction of reciprocal overlap to apply annotation to variant [0.9]')
        parser.add_argument('-e', '--exclude', metavar='<FILE>', dest='exclude', type=argparse.FileType('r'), required=False, default=None, help='list of samples to exclude from classification algorithms')
        parser.add_argument('-s', '--slope_threshold', metavar='<FLOAT>', dest='slope_threshold', type=float, default=1.0, help='minimum slope absolute value of regression line to classify as DEL or DUP[1.0]')
        parser.add_argument('-r', '--rsquared_threshold', metavar='<FLOAT>', dest='rsquared_threshold', type=float, default=0.2, help='minimum R^2 correlation value of regression line to classify as DEL or DUP [0.2], for large sample reclassification')
        parser.add_argument('-t', '--tSet', metavar='<STRING>', dest='tSet', type=str, default=None, required=False, help='high quality deletions & duplications training dataset[vcf], required by naive Bayes reclassification')
        parser.add_argument('-m', '--method', metavar='<STRING>', dest='method', type=str, default="large_sample", required=False, help='reclassification method, one of (large_sample, naive_bayes, hybrid)', choices=['large_sample', 'naive_bayes', 'hybrid'])
        parser.add_argument('-d', '--diag_file', metavar='<STRING>', dest='diag_outfile', type=str, default=None, required=False, help='text file to output method comparisons')

    @property
    def description(self):
        return 'reclassify DEL and DUP based on read depth information'

    def run_from_args(args):
        import svtools.utils as su
        from svtools.sv_classifier import run_reclassifier
        if args.tSet is None:
            if args.method!="large_sample":
                sys.stderr.write("Training data required for naive Bayes or hybrid classifiers\n")
                parser.print_help()
                sys.exit(1)
        with su.InputStream(args.input) as stream:
            run_reclassifier(stream, args.vcf_out, args.gender, args.ae_path, args.f_overlap, args.exclude, args.slope_threshold, args.rsquared_threshold, args.tSet, args.method, args.diag_outfile)
