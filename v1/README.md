### 数据包的定义

#### 兴趣包
- 包的数据部分的长度
- 包的类型
#@todo content_name在传输中如何编码
- content_name长度，需要编码吗? 如何编码
为数字1时为兴趣包，为数字2时为数据包

- 包发向的ip
- 包的content name

#### 数据包
- 包的数据部分的长度
- 包的类型
为数字1时为兴趣包，为数字0时为数据包
- content name长度
- content name
- 数据



- 包发向的ip
- 包的内容

### Log File
#### consumer
*格式如下*
时间                        发送还是接受   包类型         content_name   是否成功
2018-05-13 19:23:41.183028  send/receive  interest/data content_name   1(成功)/0(失败)