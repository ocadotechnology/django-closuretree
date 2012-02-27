from subprocess import Popen, PIPE


p = Popen(['git', 'describe', '--tags'], stdout=PIPE, stderr=PIPE)
p.stderr.close()
__version__ = p.stdout.readlines()[0].strip()
del p
