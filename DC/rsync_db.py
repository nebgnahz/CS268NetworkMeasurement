import string, subprocess
from multiprocessing import Pool

pl_hosts = [line.split(' ')[0] for line in map(string.strip,open('../king/pl-host-list-geo').readlines())]

def get_db(host):
    file_name = 'gQuery_%s.db' % host
    log_file = open(file_name + '.log', 'w')

    cp = ["ssh", "-t -t", "-i", "~/.ssh/id_rsa", "-o StrictHostKeyChecking no",
          "-o UserKnownHostsFile=/dev/null", "ucb_268_measure@%s" % host,
          "sudo cp /root/%s ~/" % file_name]

    rsync = 'rsync -a -v -e ssh -z --progress --partial ucb_268_measure@%s:%s .' % (host, file_name)

    print file_name,
    print subprocess.call(cp, stdin=subprocess.PIPE, stdout=log_file, stderr=log_file),
    print subprocess.call(rsync, shell=True, stdin=subprocess.PIPE, stdout=log_file, stderr=log_file)

p = Pool(10)
p.map(get_db, pl_hosts)
