# MIT License

# Copyright (c) 2017 GiveMeAllYourCats

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the 'Software'), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Code author: GiveMeAllYourCats
# Repo: https://github.com/michaeldegroot/cats-blender-plugin
# Edits by GiveMeAllYourCats

# encoding: utf-16


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


# Test whether a path exists.  Returns False for broken symbolic links
def exists(path):
    try:
        os.stat(path)
    except os.error:
        return False
    return True


# Add any test models you want here!
download_data = {
    'ryuko': 'https://www.dropbox.com/s/74fj6msbyn3c7rn/armature.ryuko.blend?dl=1',
    'bonetranslationerror': 'https://www.dropbox.com/s/ckoseplcfdozpeu/armature.translationerror.blend?dl=1',
}

# Download them
for name in download_data:
    url = download_data[name]
    filename = str('armature.' + str(name) + '.blend')
    new_file_path = os.path.join(os.path.dirname(__file__), 'armatures', 'armature.' + str(name) + '.blend')
    if exists(new_file_path) is False:
        print('Notice: Downloaded ' + filename + ' because it didn\'t existed')
        with urllib.request.urlopen(url) as response, open(new_file_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)

start_time = time.time()

parser = OptionParser()
parser.add_option('-b', '--blend', dest='blender_exec', help='sets the blender executable', metavar='BLENDER', default='blender')
parser.add_option('-t', '--test', dest='globber_test', help='sets the unit to test', metavar='TEST', default='*')
parser.add_option('-c', '--ci', dest='ci', help='is travis running this test?', metavar='CI', default=False)
parser.add_option('-a', '--armature', dest='globber_armature', help='sets the armature blend file to test', metavar='ARMATURE', default='*')
parser.add_option('-v', '--verbose', dest='verbosity', help='verbosity unit tests', metavar='VERBOSE', default=False)

(options, args) = parser.parse_args()

ci = options.ci
blender_exec = options.blender_exec
globber_test = options.globber_test
globber_armature = options.globber_armature
verbosity = options.verbosity

scripts = 0
exit_code = 0
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
    if exit_code != 0:
        end_message += 'Test ' + colored('FAILED', 'red', attrs=['bold'])
    else:
        end_message += 'Test ' + colored('PASSED', 'green', attrs=['bold'])
    end_message += ' in ' + str(round((time.time() - start_time))) + ' seconds'
    print(end_message)
    sys.exit(exit_code)


def print_output(raw, output):
    try:
        print(output)
    except UnicodeEncodeError:
        print(raw)


# iterate over each *.test.py file in the 'tests' directory
# and open up blender with the armature files found in 'tests/armatures' directory
for blend_file in glob.glob('./tests/armatures/armature.' + globber_armature + '.blend'):
    for file in glob.glob('./tests/' + globber_test + '.test.py'):
        if os.path.basename(file) in scripts_only_executed_once:
            if os.path.basename(file) in scripts_executed:
                continue  # skips already executed test

        scripts_executed.append(os.path.basename(file))
        scripts += 1
        start_time_unit = time.time()
        p = Popen([blender_exec, '--addons', 'mmd_tools', '--addons', 'cats', '--factory-startup', '-noaudio', '-b', blend_file, '--python', file], shell=False, stdout=PIPE, stderr=PIPE)
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
        if 'SyntaxError' in error_output or 'IndentationError' in error_output or 'NameError' in error_output:
            print('ERROR: SyntaxError found in ' + os.path.basename(file))
            print('------------------------------------------------------------------')
            print_output(stderr, error_output)
            print('------------------------------------------------------------------\n\n')
            exit_code = 1
            exit_test()

        # If a unit test went wrong, we want to see the output of the test
        if p.returncode != 0:
            print(os.path.basename(file).replace('.blend', '.py') + ' (' + os.path.basename(blend_file) + ') - exit code: ' + str(p.returncode))
            print('------------------------------------------------------------------')
            print_output(stdout, std_output)
            print_output(stderr, error_output)
            print('------------------------------------------------------------------\n\n')
            exit_code = p.returncode
            exit_test()
        else:
            if verbosity:
                print_output(stdout, std_output)


exit_test()
