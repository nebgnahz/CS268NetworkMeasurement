# main.py
from config import Configuration # import the configuration class
from commands import count_beans # import our command


if __name__ == '__main__':
    beans = raw_input('How many beans? ')
    count_beans(int(beans))
    print 'Enqueued job to count %s beans' % beans
