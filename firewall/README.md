## Firewall

### How to Use

### Problems
#### port already in use

- linux
A more simple solution just type sudo fuser -k 8000/tcp. This should kill all the processes associated with port 8000.

- For osx users you can use sudo lsof -t -i tcp:8000 | xargs kill -9