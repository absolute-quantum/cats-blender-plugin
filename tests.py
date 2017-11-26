import glob
import sys
from subprocess import Popen, PIPE
import download_armature

blenderExecutable = 'blender'
exit_code = 0
globber = '*'

# allow override of blender executable (important for CI!)
if len(sys.argv) > 1:
    blenderExecutable = sys.argv[1]

if len(sys.argv) > 2:
    globber = sys.argv[2]

# iterate over each *.test.blend file in the "tests" directory
# and open up blender with the .test.blend file and the corresponding .test.py python script
for file in glob.glob('./tests/' + globber + '.test.py'):
    for armature in glob.glob('./tests/armatures/armature.*.blend'):
        p = Popen([blenderExecutable, '--addons', 'cats', '--addons', 'mmd_tools', '--factory-startup', '-noaudio', '-b', armature, '--python', file], stdout=PIPE)
        output = p.communicate()[0]
        print(file.replace('.blend', '.py') + ' ('+armature+') - exit code: ' +  str(p.returncode))
        print('------------------------------------------------------------------')
        print(output)
        print('------------------------------------------------------------------\n\n')
        if p.returncode is not 0:
            exit_code = p.returncode

if exit_code is not 0:
    print('Unit test: FAILED')
else:
    print('Unit test: PASSED')
sys.exit(exit_code)
