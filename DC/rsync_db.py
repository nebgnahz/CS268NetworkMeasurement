import string, subprocess
from multiprocessing import Pool

pl_hosts = [line.split(' ')[0] for line in map(string.strip,open('../king/pl-host-list-geo').readlines())]

def get_db(host):
    file_name = 'gQuery_%s.db' % host

    cp = ["ssh", "-t", "-i", "~/.ssh/id_rsa", "-o StrictHostKeyChecking no",
          "-o UserKnownHostsFile=/dev/null", "ucb_268_measure@%s" % host,
          "sudo cp /root/%s ~/" % file_name]

    rsync = 'rsync -a -v -e ssh -z --progress ucb_268_measure@%s:%s .' % (host, file_name)

    print cp
    print rsync

    subprocess.call(cp)
    subprocess.call(rsync, shell=True)

p = Pool(10)
p.map(get_db, pl_hosts)
