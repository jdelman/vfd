# sync this directory to clockpi

rsync --update --exclude 'node_modules' --exclude '__pycache__' -P -a . pi@clockpi:~/vfd
