from svtools.ui.subcommand import SubCommand

class Lsort(SubCommand):
    @property
    def description(self):
        return 'sort N LUMPY VCF files into a single file'

    @property
    def epilog(self):
        return '''Specify -t to override where temporary files are placed. Use -b to control the amount of memory required.
        This will vary depending on the number of lines in your input files.
        VCF files may be gzipped and the -f argument is available for convenience.'''

    @staticmethod
    def add_arguments_to_parser(parser):
        parser.add_argument('vcf_files', metavar='<VCF>', nargs='*', help='VCF files to combine and sort')
        parser.add_argument('-f', '--vcf-list', metavar='<FILE>', help='file containing a line-delimited list of VCF files to combine and sort')
        parser.add_argument('-r', '--include-reference', required=False, action='store_true', default=False, help='whether or not to include homozygous reference or missing calls in the output.')
        parser.add_argument('-t', '--tempdir', metavar='<DIRECTORY_PATH>', help='temporary directory')
        parser.add_argument('-b', '--batchsize', metavar='<INT>', type=int, default=200, help='number of files to sort in batch')

    def run_from_args(args):
        import svtools.lsort
        vcf_files = args.vcf_files
        if args.vcf_list:
            with open(args.vcf_list, 'r') as vcf_list_file:
                for line in vcf_list_file:
                    file_name = line.rstrip()
                    vcf_files.append(file_name)

        if not vcf_files:
            sys.stderr.write("No input files provided.\n")
            sys.exit(1)
        sorter = svtools.lsort.Lsort(vcf_files, tempdir=args.tempdir, batchsize=args.batchsize, include_ref=args.include_reference)
        sorter.execute()
