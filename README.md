# icn_sim
simulating icn in lab

#### Ronsumer
修改icn_sim/config/consumer.conf的第一行
- 192.168.80.135 10000 中的ip地址为Router的ip地址

#### Router
修改icn_sim/config/router.conf
- 第一行localip改成自己的IP地址
- 后面几行的ip改成内容对应的publisher的ip地址

#### Publisher
修改icn_sim/config/publisher.conf
- 如果要增加内容的话那就修改

修改publisher.conf
- 第一行_HOST = '192.168.80.134'改为publisher的ip地址

### Three parts of ICN
- Publisher
- Router
- Consumer

### Definition of packet
#### Interest Packet

#### Data Packet


### Publisher

### Router
Read the file *router.config*，get the content for FIB
The format of *router.config* is as follows:

- /aueb.gr/   ip_addr1
- /aueb.gr/cs ip_addr2

#### firewall