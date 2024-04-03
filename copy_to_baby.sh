ssh -t pi@babyberry.duckdns.org "rm -rf ~/MusiQ"
ssh -t pi@babyberry.duckdns.org "mkdir MusiQ"
scp -rp ./Backend pi@babyberry.duckdns.org:~/MusiQ/
