## Router

### 初始化
读取router.config文件，获取FIB表的内容
router.config的格式如下（最后会采用一个最长匹配)：

/aueb.gr/   ip_addr1
/aueb.gr/cs ip_addr2

- 接收包
开一个thread
- 发消息给防火墙，同时接受防火墙的信息
- 判断返回，如果False，关闭thread，否则，继续下一步
- 查找CS表(查找这个包在本地是否有缓存)
- 查找PIT表(也就是查找这个包是否已经被查找过了)
- 查找FIB表(转发表)

class Router(threading.Thread)