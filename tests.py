import glob
import sys
from subprocess import Popen, PIPE

# Make sure to have up-to-date armature blend files
# NOTE: files can be updated by renaming them in download_armature.py
import download_armature

blenderExecutable = 'blender'
exit_code = 0
globber = '*'

# allow override of blender executable (important for CI!)
if len(sys.argv) > 1:
    blenderExecutable = sys.argv[1]
    addons = []

if len(sys.argv) > 2:
    globber = sys.argv[2]

scripts_failed = 0
scripts = 0

# iterate over each *.test.py file in the "tests" directory
# and open up blender with the armature files found in "tests/armatures" directory
for file in glob.glob('./tests/' + globber + '.test.py'):
    for blend_file in glob.glob('./tests/armatures/armature.*.blend'):
        print('Testing unit: ' + file + ' with blend file: ' + blend_file)
        scripts += 1
        p = Popen([blenderExecutable, '--addons', 'mmd_tools', '--addons', 'cats', '--factory-startup', '-noaudio', '-b', blend_file, '--python', file], shell=False, stdout=PIPE, stderr=PIPE)
        output = p.communicate()

        error_output = output[1].decode('utf_8')
        std_output = output[0].decode('utf_8')

        # This will detect invalid syntax in the unit test itself
        if 'SyntaxError' in error_output:
            scripts_failed += 1
            print('ERROR: SyntaxError found in ' + file)
            print('------------------------------------------------------------------')
            print(error_output)
            print('------------------------------------------------------------------\n\n')
            exit_code = 1
            continue

        # If a unit test went wrong, we want to see the output of the test
        if p.returncode is not 0:
            scripts_failed += 1
            print(file.replace('.blend', '.py') + ' (' + blend_file + ') - exit code: ' + str(p.returncode))
            print('------------------------------------------------------------------')
            print(std_output)
            print('------------------------------------------------------------------\n\n')
            exit_code = p.returncode

if exit_code is not 0:
    print(' > FAILED: ' + str(scripts_failed) + ' out of ' + str(scripts) + ' tests failed')
else:
    print(' > PASSED: all tests passed!')
sys.exit(exit_code)
