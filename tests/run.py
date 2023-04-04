# GPL License

# encoding: utf-16

# To run these tests, run this file as a script, e.g.:
# python run.py --blend=<path to blender executable>
# The blender executable needs to have Cats installed such that Cats' main module is called "cats" without quotes
# Remember to run the tests against at least both blender 2.79 and the newest blender version supported by Cats
# The python version you use to run the script is irrelevant to the tests since blender will use its python version when
# running the tests
import urllib.request
import shutil
import time
import glob
import sys
import os
import itertools
from subprocess import Popen, PIPE
from optparse import OptionParser
from termcolor import colored
from collections import namedtuple


# Test whether a path exists.  Returns False for broken symbolic links
def exists(path):
    try:
        os.stat(path)
    except os.error:
        return False
    return True


DownloadData = namedtuple('DownloadData', ['directory', 'file_prefix', 'files'])

# Add any test models you want here!
download_data = [
    DownloadData(
        directory='armatures',
        file_prefix='armature.',
        files={
            'ryuko': 'https://www.dropbox.com/s/74fj6msbyn3c7rn/armature.ryuko.blend?dl=1',
            'bonetranslationerror': 'https://www.dropbox.com/s/ckoseplcfdozpeu/armature.translationerror.blend?dl=1',
        }
    ),
    DownloadData(
        directory='shapekeys',
        file_prefix='shapekey.',
        files={
            'shape_key_to_basis': 'https://www.dropbox.com/s/d0efnrkauq596ng/ApplyShapeToBasisTest.blend?dl=1',
        }
    ),
]

# Download them
for data in download_data:
    directory = str(data.directory)
    file_prefix = str(data.file_prefix)
    for name, url in data.files.items():
        filename = file_prefix + name + '.blend'
        new_file_path = os.path.join(os.path.dirname(__file__), directory, filename)
        if exists(new_file_path) is False:
            print('Notice: Downloaded ' + filename + ' because it didn\'t exist')
            with urllib.request.urlopen(url) as response, open(new_file_path, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)

start_time = time.time()

parser = OptionParser()
parser.add_option('-b', '--blend', dest='blender_exec', help='sets the blender executable', metavar='BLENDER', default='blender')
parser.add_option('-t', '--test', dest='globber_test', help='sets the unit to test, supports multiple files by unix style pathname pattern expansion. Automatically appended with ".test.py"', metavar='FILE_OR_PATTERN',
                  default='./tests/armatures/*')
parser.add_option('-f', '--bfile', dest='globber_blend_files', help='sets the blend file to test against, supports multiple files by unix style pathname pattern expansion. Automatically appended with ".blend"',
                  metavar='FILE_OR_PATTERN', default='./tests/armatures/armature.*')
parser.add_option('-c', action="store_true", dest='ci', help='is travis running this test?', default=False)
parser.add_option('-v', action="store_true", dest='verbosity', help='verbosity unit tests', default=False)
parser.add_option('-e', action="store_true", dest='error_continue', help='continue running additional tests even if a test fails', default=False)
# Useful for debugging
parser.add_option('-p', action="store_true", dest='pipe_to_std', help='pipe all blender and test output directly to stdout and stderr instead of using custom filtering and output', default=False)

(options, args) = parser.parse_args()

ci = options.ci
blender_exec = options.blender_exec
globber_test = options.globber_test
globber_blend_files = options.globber_blend_files
verbosity = options.verbosity
error_continue = options.error_continue
pipe_to_std = options.pipe_to_std

scripts = 0
exit_code = 0
error_code = 0
scripts_only_executed_once = ['atlas.test.py', 'syntax.test.py']
scripts_executed = []


def show_time(time):
    rounded = round(time)
    string = str(rounded)
    color = 'grey'

    if rounded > 0:
        color = 'green'

    if rounded > 10:
        color = 'yellow'

    if rounded > 20:
        color = 'red'

    return colored(string, color, attrs=['bold'])


spinner = itertools.cycle(['-', '/', '|', '\\'])


def exit_test():
    end_message = ' > '
    if exit_code != 0 or (error_continue != 0 and error_code != 0):
        end_message += 'Test ' + colored('FAILED', 'red', attrs=['bold'])
    else:
        end_message += 'Test ' + colored('PASSED', 'green', attrs=['bold'])
    end_message += ' in ' + str(round((time.time() - start_time))) + ' seconds'
    print(end_message)
    sys.exit(error_code if error_code != 0 else exit_code)


def print_output(raw, output):
    try:
        print(output)
    except UnicodeEncodeError:
        print(raw)


# iterate over each globber_blend_files.blend file relative to the 'tests' directory
# then iterate over each globber_test.test.py file relative to the 'tests' directory
# then open up blender with the current blend file and run the current test
for blend_file in glob.glob(globber_blend_files + '.blend'):
    for file in glob.glob(globber_test + '.test.py'):
        if os.path.basename(file) in scripts_only_executed_once:
            if os.path.basename(file) in scripts_executed:
                continue  # skips already executed test

        scripts_executed.append(os.path.basename(file))
        scripts += 1
        start_time_unit = time.time()
        if pipe_to_std:
            p = Popen([blender_exec, '--addons', 'cats', '--factory-startup', '-noaudio', '-b', blend_file, '--python', file], shell=False, stdout=sys.stdout, stderr=sys.stderr)
            p.wait()
            exit_code = p.returncode
            if p.returncode != 0:
                error_code = p.returncode
                if not error_continue:
                    exit_test()
        else:
            p = Popen([blender_exec, '--addons', 'cats', '--factory-startup', '-noaudio', '-b', blend_file, '--python', file], shell=False, stdout=PIPE, stderr=PIPE)

            if ci is False:
                while p.poll() is None:
                    nextline = p.stdout.readline()
                    if nextline == '' and p.poll() is not None:
                        break
                    do_print = ' ' + next(spinner) + ' UNIT ' + os.path.basename(file).ljust(22) + ' > BLEND ' + os.path.basename(blend_file).ljust(40) + ' > ' + show_time(time.time() - start_time_unit) + 's '
                    sys.stdout.write(do_print)
                    sys.stdout.flush()
                    [sys.stdout.write('\b') for i in range(len(do_print))]

            sys.stdout.flush()
            (stdout, stderr) = p.communicate()

            error_output = str(stderr, 'utf-8')
            std_output = str(stdout, 'utf-8')
            print(' > UNIT ' + os.path.basename(file).ljust(22) + ' > BLEND ' + os.path.basename(blend_file).ljust(40) + ' > ' + show_time(time.time() - start_time_unit) + 's')

            # This will detect invalid syntax in the unit test itself
            if 'SyntaxError' in error_output or 'IndentationError' in error_output or 'NameError' in error_output or 'ModuleNotFoundError' in error_output:
                print('ERROR: SyntaxError found in ' + os.path.basename(file))
                print('------------------------------------------------------------------')
                print_output(stderr, error_output)
                print('------------------------------------------------------------------\n\n')
                exit_code = 1
                error_code = 1
                if not error_continue:
                    exit_test()

            # If a unit test went wrong, we want to see the output of the test
            if p.returncode != 0:
                print(os.path.basename(file).replace('.blend', '.py') + ' (' + os.path.basename(blend_file) + ') - exit code: ' + str(p.returncode))
                print('------------------------------------------------------------------')
                print_output(stdout, std_output)
                print_output(stderr, error_output)
                print('------------------------------------------------------------------\n\n')
                exit_code = p.returncode
                error_code = p.returncode
                if not error_continue:
                    exit_test()
            else:
                if verbosity:
                    print_output(stdout, std_output)
                    print_output(stderr, error_output)


exit_test()
