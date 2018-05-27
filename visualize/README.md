# 可视化实现思路

- src_now和dst_now用于表明是哪一个位置，如果为-1就表示没有新的点。
接下来进入画图的时候就会直接跳出来
- attack_position表明显示到log文件的哪里了。如果没有显示到结尾，就会设置
下次执行的位置

```
init: function(){
    setTimeout(
        jQuery.proxy(this.getData, this),
        this.interval
    );

    this.time_read = this.time_read + this.interval/1000.0;
    if (this.time_read > 3) {
        this.time_read = 0;
        // @todo 在这里读取文件
        d3.csv("../icn_sim/log/test.csv",function(error,attack_data){
            attacks.attack_data = d3.csv.format(attack_data).split('\n');
            if(error){
                console.log(error);
            }
            //console.log(attack_data);
       });
    }
    // 0 1
    if (this.attack_position < this.attack_data.length) {
        this.src_now = parseInt(this.attack_data[this.attack_position].split(",")[0]);
        this.dst_now = parseInt(this.attack_data[this.attack_position].split(",")[1]);
        this.attack_position = this.attack_position + 1;
    } else {
        this.src_now = -1;
        this.dst_now = -1;
    }

},
```