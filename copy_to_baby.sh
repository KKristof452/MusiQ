ssh -t pi@babyberry.duckdns.org "rm -rf ~/MusiQ"
scp -rp ../MusiQ pi@babyberry.duckdns.org:~/
