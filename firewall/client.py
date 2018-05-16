#-*- coding:utf-8 -*-
import gensim

blacklist = [u'邪教']

class Client:
    def load_model(self):
        self.blacklist = blacklist
        self.model = gensim.models.Word2Vec.load("wiki.zh.text.model")
        self.model.init_sims(replace=True)

    def judge_content_name(self, content_name):
        try:
            for blacklist_element in blacklist:
                # 通过content name来生成
                content_name_result = self.model.most_similar(content_name)
                content_name_result_list = []
                for e in content_name_result:
                    content_name_result_list.append(e[0])
                for i in content_name_result_list:
                    if i in self.blacklist:
                        return False
                # 通过blacklist来生成
                element_result = self.model.most_similar(blacklist_element)
                element_result_list = []
                for e in element_result:
                    element_result_list.append(e[0])
                if content_name in element_result_list:
                    return False
            return True
        except:
            print('did not find the word')
