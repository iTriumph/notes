#!python
# -*- coding:utf-8 -*-
"""
Created on 2014/9/25
Updated on 2019/1/18
@author: Holemar

本模块专门处理文件用
"""
import os
import urllib
import urllib2
import logging

__all__=('get_first_lines', 'get_last_lines', 'remove', 'clear', 'download_file')


def get_first_lines(file_path, num=1, include_blank=False):
    """
    获取文件的开头几行
    :param {string} file_path: 要读取的文件路径
    :param {int} num: 要读取的行数(默认读取最后一行)
    :param {bool} include_blank: 获取的内容是否包含空行
    :return {string | list<string>}: 开头几行内容的字符串列表(如果是只读取最后一行,则返回那一行字符串)
    """
    assert isinstance(num, (int, long)) and num >= 1

    n_lines = []
    with open(file_path, 'rb') as fp:
        #n_lines = fp.readlines(num) # 为了便于去掉空行，改成逐行读取
        for line in fp:
            if len(n_lines) >= num: break
            if line:
                # 判断空行
                if not include_blank:
                    line = line.strip()
                    if not line:
                        continue
                    n_lines.append(line)
                else:
                    n_lines.append(line.rstrip()) # 去掉最后边的换行符
    # 返回内容
    if num == 1 and len(n_lines) == 1:
        return n_lines[0]
    return n_lines


def get_last_lines(file_path, num=1, include_blank=False):
    """
    获取文件的最后几行
    :param {string} file_path: 要读取的文件路径
    :param {int} num: 要读取的行数(默认读取最后一行)
    :param {bool} include_blank: 获取的内容是否包含空行
    :return {string | list<string>}: 最后几行内容的字符串列表(如果是只读取最后一行,则返回那一行字符串)
    """
    blk_size_max = 4096
    n_lines = []
    with open(file_path, 'rb') as fp:
        fp.seek(0, os.SEEK_END)
        cur_pos = fp.tell()
        while cur_pos > 0 and len(n_lines) < num:
            blk_size = min(blk_size_max, cur_pos)
            fp.seek(cur_pos - blk_size, os.SEEK_SET)
            blk_data = fp.read(blk_size)
            assert len(blk_data) == blk_size
            lines = blk_data.split('\n')

            # adjust cur_pos
            if len(lines) <= 2:
                if len(lines[1]) > 0:
                    n_lines[0:0] = lines[1:]
                    cur_pos -= (blk_size - len(lines[0]))
                else:
                    n_lines[0:0] = lines[0:]
                    cur_pos -= blk_size
            elif len(lines) > 1 and len(lines[0]) > 0:
                n_lines[0:0] = lines[1:]
                cur_pos -= (blk_size - len(lines[0]))
            else:
                n_lines[0:0] = lines
                cur_pos -= blk_size
            fp.seek(cur_pos, os.SEEK_SET)
        fp.close()
    # 去掉空行
    if not include_blank:
        n_lines[:] = [r.strip() for r in n_lines if r.strip()]
    else:
        n_lines[:] = [r.rstrip() for r in n_lines] # 去掉最后边的换行符
    # 最后一行如果是空值，则删掉
    if len(n_lines) > 0 and len(n_lines[-1]) == 0:
        del n_lines[-1]
    # 返回内容
    res = n_lines[-num:]
    if num == 1 and len(res) == 1:
        res = res[0]
    return res


def remove(file_path):
    """
    删除文件
    :param {string} file_path: 要删除的文件路径
    """
    file_path = os.path.abspath(file_path)
    if os.path.isfile(file_path):
        try:
            os.remove(file_path) # 不知道什么原因，这句会报错
        except:
            os.popen('del /q /f "%s"' % file_path)


def clear(file_path):
    """
    清空文件
    :param {string} file_path: 要清空的文件路径
    """
    file_path = os.path.abspath(file_path)
    if os.path.isfile(file_path):
        try:
            open(file_path, mode="w").close()
        except:
            os.popen('echo""> "%s"' % file_path)


def download_file(url, file_path):
    """
    下载网络文件
    :param {string} url: 要下载的文件网址
    :param {string} file_path: 要下载到本地的文件名(包含目录+文件名的路径)
    """
    try:
        remove(file_path) # 先删除旧文件
        file_dir = os.path.dirname(file_path)
        # 没有文件的目录，则先创建目录，避免因此报错
        if not os.path.isdir(file_dir):
            os.makedirs(file_dir)
        # 文件下载
        urllib.urlretrieve(url, file_path)
    except urllib2.HTTPError as e:
        status_code = e.code
        res = e.read()
        logging.error("文件下载失败, 返回码:%s, 返回内容:%s" , status_code, res, exc_info=True)
