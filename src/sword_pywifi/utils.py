# -*- coding: utf-8 -*-
import itertools as its

def make_dictionary():
    # 单个字符的集合
    words = "0123456789"

    # 每次任选一个字符，重复8次
    arrays = its.product(words, repeat=8)

    # 写入txt文本文件
    dictionary = open("../dictionary/dictionary.txt", "a")

    for item in arrays:
        # 一行密码
        dictionary.write("".join(item))
        # 换行
        dictionary.write("".join("\n"))
        print(item)

    # 关闭文件
    dictionary.close()

    print("[mission completion]")
