from svtools.ui.subcommand import SubCommand

class Afreq(SubCommand):
    @property
    def description(self):
        return 'add allele frequency information to a VCF file'

    @property
    def epilog(self):
        return 'Specify the path to an (optionally) bgzipped VCF. If no file is specified then input is read from stdin.'

    def add_arguments_to_parser(self, parser):
        parser.add_argument(metavar='<VCF>', dest='input_vcf', nargs='?', default=None, help='VCF input')

    @staticmethod
    def run_from_args(args):
        import svtools.utils as su
        from svtools.afreq import UpdateInfo

        with su.InputStream(args.input_vcf) as input_stream:
            updater = UpdateInfo(input_stream)
            updater.execute()
