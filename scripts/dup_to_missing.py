#!/usr/bin/env python

from __future__ import division
import argparse
import sys
from svtools.vcf.file import Vcf
from svtools.vcf.variant import Variant
import svtools.utils as su

class VCFReader(object):
    def __init__(self, stream):
        self.vcf_obj = Vcf()
        self.stream = stream
        header = list()
        for line in stream:
            if line[0] != '#':
                raise RuntimeError('Error parsing VCF header. Line is not a header line. {}'.format(line))
            header.append(line)
            if line.startswith('#CHROM\t'):
                # end of header
                break
        self.vcf_obj.add_header(header)

    def __iter__(self):
        for line in self.stream:
            yield Variant(line.rstrip().split('\t'), self.vcf_obj)

def set_missing(input_stream, output_stream):
    for variant in input_stream:
        if variant.get_info('SVTYPE') == 'DUP':
            for s in variant.sample_list:
                g = variant.genotype(s)
                original_gt = g.get_format('GT')
                original_gq = g.get_format('GQ')
                g.set_format('GT', './.')
                g.set_format('GQ', '.')
                g.set_format('GTO', original_gt)
                g.set_format('GQO', original_gq)

        output_stream.write(variant.get_var_string())
        output_stream.write('\n')
                
def description():
    return 'set genotypes of duplications to missing and preserve old calls in GTO and GQO fields'

def add_arguments_to_parser(parser):
    parser.add_argument("-i", "--input", required=True, dest="input", metavar='<VCF>', help="VCF file containing variants to be output")
    parser.add_argument('-o', '--output', type=argparse.FileType('w'), metavar='<VCF>', default=sys.stdout, help='output VCF to write (default: stdout)')
    parser.set_defaults(entry_point=run_from_args)

def command_parser():
    parser = argparse.ArgumentParser(description=description())
    add_arguments_to_parser(parser)
    return parser

def run_from_args(args):
    with su.InputStream(args.input) as stream:
        variant_stream = VCFReader(stream)
        for index, f in enumerate(variant_stream.vcf_obj.format_list):
            if f.id == 'GTO':
                new_gto = Vcf.Format(f.id, f.number, f.type, "Original Genotype")
                variant_stream.vcf_obj.format_list[index] = new_gto
    
        args.output.write(variant_stream.vcf_obj.get_header())
        args.output.write('\n')
        return set_missing(variant_stream, args.output)

if __name__ == '__main__':
    parser = command_parser()
    args = parser.parse_args()
    sys.exit(args.entry_point(args))
