yum -y install git python-setuptools python-setuptools-devel python-twisted
yum -y install make gcc gcc-c++ kernel-devel m4 ncurses-devel openssl-devel
easy_install pip
pip install --insecure dnspython rpyc

mkdir -p .ssh
echo "-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA6J47jGKWt0NZ9vNndoDSPLv5rBLj8Jn22HhiyRvpC4Tx7GHP
ioTWyTQhRha3R5B0M4UW88WTqQPA5lUayuJxm2kC4TMY/j8CN8DlI6bHBf1mm5Oa
W/PbcteIyO1xM+xV/Y4S/d8LuqsP8v/XclGd92Soi5ENWv1IW6YN3j6kGMzd2xLe
htarASx3IbaFNpn5OoVA+rboMzLxIgigWuGyEHD3GR+bOZP9Q54SCTXW9ZyrA29K
IgMQbOR9gRuz7NuC1cA7Xa2Q/2J1DkE0aqo3MNHu9ikoPQ2ORtyZBL8Bycie5yAJ
/1hr6597Mx3lyDB3jmxeb7yJZrSN0vqXX+EDPQIDAQABAoIBACcbgxNk98WzswpL
fZd0rOO9DoqZWmz21YMrKiB5asKfBTUidIvrLVkCRJ3N794+MOsAcw1kqCCAGwwe
PrThQQxJqUxHFOqZmTvaWCuYPFmLcpaxSAAxjTFPfxWYpbF/CC3qltLLjuNBIxtN
W+FCS3ZuG8/rAP3NGz8dObOlgF0SshJ6trQDVHMYWLNaOLzoNvaejkACh5vDh99f
mGuJpPcf8SSvMK5IcbKWzkCIxppUv8pmvl6Mb0wxJc3XX6FbmHXwGJCMBfJbf2mg
mJuHF0YniXqUm85UyPiBN5FxunciVwR1yfxXY69aRvSkdWuemt4asFIoPU8WCVnB
KwSQgIECgYEA/kJuuUqcC0erMQ44DpfZ/fn86UScqoO/kPR2d4XoyQ9Ji8eh/ZJo
iOd+WjlFNgKJ0AJtNgCxSSGi83+LOBYWVGNepgSnKerRtg59EcIySdJAa/YkXcaA
umRdk5jnSBMNkdOepQ+QZjKJXnbSEdjnQkJ/JOQjBYOIq3bWJFMG/Q0CgYEA6jXg
HCgnSCqX0O8KYXNHZXY3R56p7umyZYwmB6xDe12Dm7mTDZBH2Qj6efoQV0UPjabw
H5/iKZvS2VpXD1DdBkL4LdhuNC/+yn9TEeE28cFMDGhLRqdsFTy8RCO9DdmQY32f
cxtWc1O8ynabDofkFFVS49YH2JIBKy6u6QrRcvECgYB3GNMYg/Q37Ggp4EktvL9l
kfV/pp3j2TagRYJAVj9F/p0qlmYwiqXgit7KkEz1EZdQEfLp+sUQRms3t6SUrvPi
r3EkPsW2gsGcj4jSCq7XmV6Hs5IxQswFgwG6I0MipZoTlpaXJoUy+bUSxIF9zqX0
iYVY2Gv3JzebaVzBQwrg+QKBgDCo4Nb4wLCNqN0PzOhSOxMpbHLE1Cl/BEF0zLHr
aFnJI/7Gn3bB8yt0YhXVjm+TOZgEhv8LCMH8TeI6krvr4P/cChP8U2kkT5tiuK+O
SwwPTO2G/ZzATARdif/eLPkjqowBHY+crmlnjGHEIpLySMCwuXf8j8S/EN8X498n
ED0BAoGBAJNFhfH5njDgPSw0XESCYMV9wQ5Hw0Hwn0SWHwvI3aAHTeMHU9AOoeH6
qaw8PA7Wz2r2C2m7TgWr4STswuqw183/JLlowYPWPdnbp4csLQJMcJ+K9QulLYQ3
cYzZWzXlCZwLBjJBXSvbPnQHAlbYuUxjf+d5rtrNCCLNKOuOX1jm
-----END RSA PRIVATE KEY-----" > ~/.ssh/id_rsa

echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDonjuMYpa3Q1n282d2gNI8u/msEuPwmfbYeGLJG+kLhPHsYc+KhNbJNCFGFrdHkHQzhRbzxZOpA8DmVRrK4nGbaQLhMxj+PwI3wOUjpscF/Wabk5pb89ty14jI7XEz7FX9jhL93wu6qw/y/9dyUZ33ZKiLkQ1a/Uhbpg3ePqQYzN3bEt6G1qsBLHchtoU2mfk6hUD6tugzMvEiCKBa4bIQcPcZH5s5k/1DnhIJNdb1nKsDb0oiAxBs5H2BG7Ps24LVwDtdrZD/YnUOQTRqqjcw0e72KSg9DY5G3JkEvwHJyJ7nIAn/WGvrn3szHeXIMHeObF5vvIlmtI3S+pdf4QM9 ahirreddy@gmail.com" > ~/.ssh/id_rsa.pub

chmod 600 ~/.ssh/id_rsa*

git clone git@github.com:nebgnahz/CS268NetworkMeasurement.git

