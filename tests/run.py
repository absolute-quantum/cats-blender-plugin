import time
import glob
import sys
import os
from subprocess import Popen, PIPE
from optparse import OptionParser
from termcolor import colored

# Make sure to have up-to-date armature blend files
# NOTE: files can be updated by renaming them in download_armature.py
import download_armature

start_time = time.time()

parser = OptionParser()
parser.add_option('-b', '--blend', dest='blender_exec', help='sets the blender executable', metavar='BLENDER', default='blender')
parser.add_option('-t', '--test', dest='globber_test', help='sets the unit to test', metavar='TEST', default='*')
parser.add_option('-a', '--armature', dest='globber_armature', help='sets the armature blend file to test', metavar='ARMATURE', default='*')

(options, args) = parser.parse_args()

blender_exec = options.blender_exec
globber_test = options.globber_test
globber_armature = options.globber_armature

exit_code = 0
scripts_failed = 0
scripts = 0
scripts_only_executed_once = ['atlas.test.py', 'syntax.test.py']
scripts_executed = []

def show_time(time):
    rounded = round(time, 2)
    string = str(rounded)
    color = 'grey'

    if rounded > 0:
        color = 'green'

    if rounded > 10:
        color = 'yellow'

    if rounded > 20:
        color = 'red'

    return colored(string, color, attrs=['bold'])


# iterate over each *.test.py file in the 'tests' directory
# and open up blender with the armature files found in 'tests/armatures' directory
for file in glob.glob('./tests/' + globber_test + '.test.py'):
    for blend_file in glob.glob('./tests/armatures/armature.' + globber_armature + '.blend'):
        if os.path.basename(file) in scripts_only_executed_once:
            if os.path.basename(file) in scripts_executed:
                continue # skips already executed test

        scripts_executed.append(os.path.basename(file))
        scripts += 1
        start_time_unit = time.time()
        p = Popen([blender_exec, '--addons', 'mmd_tools', '--addons', 'cats', '--factory-startup', '-noaudio', '-b', blend_file, '--python', file], shell=False, stdout=PIPE, stderr=PIPE)
        output = p.communicate()

        error_output = output[1].decode('utf_8')
        std_output = output[0].decode('utf_8')
        print(' > UNIT ' + os.path.basename(file).ljust(22) + ' > BLEND ' + os.path.basename(blend_file).ljust(40) + ' > ' + show_time(time.time() - start_time_unit) + 's')

        # This will detect invalid syntax in the unit test itself
        if 'SyntaxError' in error_output or 'IndentationError' in error_output or 'NameError' in error_output:
            scripts_failed += 1
            print('ERROR: SyntaxError found in ' + os.path.basename(file))
            print('------------------------------------------------------------------')
            try:
                print(error_output)
            except UnicodeEncodeError:
                print(output[1])
            print('------------------------------------------------------------------\n\n')
            exit_code = 1
            continue

        # If a unit test went wrong, we want to see the output of the test
        if p.returncode != 0:
            scripts_failed += 1
            print(os.path.basename(file).replace('.blend', '.py') + ' (' + os.path.basename(blend_file) + ') - exit code: ' + str(p.returncode))
            print('------------------------------------------------------------------')
            try:
                print(std_output)
            except UnicodeEncodeError:
                print(output[0])
            try:
                print(error_output)
            except UnicodeEncodeError:
                print(output[1])
            print('------------------------------------------------------------------\n\n')
            exit_code = p.returncode

if exit_code != 0:
    print(' > ' + colored('FAILED', 'red', attrs=['bold']) + ': ' + str(scripts_failed) + ' out of ' + str(scripts) + ' tests failed')
else:
    print(' > ' + colored('PASSED', 'green', attrs=['bold']) + ': all tests (' + str(scripts) + ') passed!')

print(' > FINISHED in ' + str(round((time.time() - start_time), 2)) + ' seconds')
sys.exit(exit_code)
