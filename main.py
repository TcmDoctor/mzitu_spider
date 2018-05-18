#!/usr/bin/env python3
# coding:utf-8

"""抓取mzitu指定页之间所有套图, 保存在当前目录的temp目录下."""

import re
import os
from multiprocessing import Pool

import myrequests as requests
from bs4 import BeautifulSoup
from finished import finished


def post_url_list(x=1, y=2):
    """获取指定页之间所有图集的url.

    :param x: int, 起始页.

    :param y: int, 结束页.

    :return post_url: str, 图集链接.
    """

    url = 'http://www.mzitu.com'
    with requests.Session() as session:
        for i in range(x, y):
            if i == 1:
                page_url = url
            else:
                page_url = '%s/page/%d/' % (url, i)
            r = session.get(page_url)
            if r:
                soup = BeautifulSoup(r.text, 'lxml')
                post_tag_list = soup.select('div.postlist li > span > a')
                for post_tag in post_tag_list:
                    yield post_tag.get('href')
                    

def download(url):
    """以图集名创建文件夹, 下载图集中所有图片.

    :param  url: str, 图集链接.
    """

    pattern = re.compile(r'[\\/:*?"<>| ]')

    with requests.Session() as session:
        session.headers['referer'] = 'http://www.mzitu.com'
        r = session.get(url)
        if r:
            soup = BeautifulSoup(r.text, 'lxml')
            post_name = soup.select('h2.main-title')[0].get_text()
            # 剔除不符合文件夹命名规则的字符
            post_name = pattern.sub('', post_name)
            path = 'temp/%s' % post_name
            if not os.path.exists(path):
                os.mkdir(path)
            # 获取图片数量
            img_num = int(soup.select('div.pagenavi a span')[-2].get_text())
            # 图片url的模板
            temp_url = soup.select('div.main-image img')[0].get('src')[:-6]

            for i in range(1, img_num+1):
                img_url = '%s%02d.jpg' % (temp_url, i)
                r = session.get(img_url)
                if r:
                    with open('%s/%02d.jpg' % (path, i), 'wb') as f:
                        f.write(r.content)


@finished
def main():
    if not os.path.exists('temp'):
        os.mkdir('temp')
    with Pool(8) as pool:
        pool.map(download, post_url_list(x=1, y=2))


if __name__ == '__main__':
    main()
