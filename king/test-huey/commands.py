# commands.py
from huey import queue_command

from config import invoker # import the invoker we instantiated in config.py


@queue_command(invoker)
def count_beans(num):
    print 'Counted %s beans' % num