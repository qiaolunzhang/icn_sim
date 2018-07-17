#-*- coding:utf-8 -*-
import gensim

model = gensim.models.Word2Vec.load("wiki.zh.text.model")
model.init_sims(replace=True)
while True:
    word = raw_input("Please the word of the blacklist of firewall: ")
    result = model.most_similar(word)
    for e in result:
        print(e[0], e[1])
