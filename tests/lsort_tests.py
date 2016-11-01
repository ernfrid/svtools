from unittest import TestCase, main
import tempfile
import os
import sys
import difflib
import svtools.lsort as lsort

class LsortIntegrationTest(TestCase):
    def run_integration_test(self):
        test_directory = os.path.dirname(os.path.abspath(__file__))
        self.test_data_dir = os.path.join(test_directory, 'test_data', 'lsort')
        # glob vcfs
        vcfs = list()
        for sample in ('NA12878', 'NA12891', 'NA12892'):
            vcfs.append(os.path.join(self.test_data_dir, '{0}.vcf'.format(sample)))
        expected_result = os.path.join(self.test_data_dir, 'lsort_expected')
        temp_descriptor, temp_output_path = tempfile.mkstemp(suffix='.vcf')
        with os.fdopen(temp_descriptor, 'w') as output_handle:
            sorter = lsort.Lsort(vcfs, tempdir=None, batchsize=2, output_handle=output_handle)
            sorter.execute()
            output_handle.flush()
            expected_lines = open(expected_result).readlines()
            produced_lines = open(temp_output_path).readlines()
            diff = difflib.unified_diff(produced_lines, expected_lines, fromfile=temp_output_path, tofile=expected_result)
            result = ''.join(diff)
            if result != '':
                for line in result:
                    sys.stdout.write(line)
                self.assertFalse(result)
        os.remove(temp_output_path)

    def run_file_list_integration_test(self):
        test_directory = os.path.dirname(os.path.abspath(__file__))
        self.test_data_dir = os.path.join(test_directory, 'test_data', 'lsort')
        # glob vcfs
        vcfs = list()
        for sample in ('NA12878', 'NA12891', 'NA12892'):
            vcfs.append(os.path.join(self.test_data_dir, '{0}.sv.vcf.gz'.format(sample)))
        expected_result = os.path.join(self.test_data_dir, 'lsort_expected')
        temp_descriptor, temp_output_path = tempfile.mkstemp(suffix='.vcf')
        with os.fdopen(temp_descriptor, 'w') as output_handle:
            sorter = lsort.Lsort(vcfs, tempdir=None, batchsize=2, include_ref=False, output_handle=output_handle)
            sorter.execute()
            output_handle.flush()
            expected_lines = open(expected_result).readlines()
            produced_lines = open(temp_output_path).readlines()
            diff = difflib.unified_diff(produced_lines, expected_lines, fromfile=temp_output_path, tofile=expected_result)
            result = ''.join(diff)
            if result != '':
                for line in result:
                    sys.stdout.write(line)
                self.assertFalse(result)
        os.remove(temp_output_path)


if __name__ == "__main__":
    main()
