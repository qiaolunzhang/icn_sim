# -*- coding:utf-8 -*-
import gensim
module_path = "/home/zhang/mycode/firewall_icn/wiki.zh.text.model"
model = gensim.models.Word2Vec.load(module_path)
result = model.most_similar(u"法轮功")
for e in result:
    print e[0], e[1]

