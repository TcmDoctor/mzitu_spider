#!/usr/bin/env python3
# coding:utf-8

'''抓取mzitu套图'''

import os
from multiprocessing import Pool

from bs4 import BeautifulSoup
import myrequests as requests
from finished import finished


def post_info_list(url, x, y):
    r'''获取图集名字和url.
    
    :param  url: str, 主链接.
    :param  x: int, 起始页.
    :param  y: int, 结束页.
    :return post_name: str, 图集名字.
            post_url: str, 图集链接.
    '''

    for i in range(x, y):
        if i == 1:
            page_url = url
        else:  
            page_url = '%s/page/%s' % (url, i)
        r = requests.get(page_url)
        soup = BeautifulSoup(r.text, 'lxml')
        post_tag_list = soup.select('div.postlist li > span > a')
        for post_tag in post_tag_list:
            post_name = post_tag.get_text()
            post_url = post_tag.get('href')
            yield post_url, post_name


def img_url_list(url):
    r'''获取每个图集的所有图片链接.
    
    :param  url: str, 图集链接.
    :return img_url: str, 图集中每张图片链接.
    '''

    r = requests.get(url)
    if r:
        soup = BeautifulSoup(r.text, 'lxml')
        page_number = soup.select('div.pagenavi a span')[-2].get_text()
        img_url = soup.select('div.main-image img')[0].get('src')
        yield img_url
        with requests.Session() as session:
            for i in range(2, int(page_number) + 1):
                page_url = '%s/%s' % (url, i)
                r = session.get(page_url)
                if r:
                    soup = BeautifulSoup(r.text, 'lxml')
                    img_url = soup.select('div.main-image img')[0].get('src')
                    yield img_url


def download(info):
    r'''下载图片.
    
    :param  info: tuple,
        info[0]: 图集链接,
        info[1]: 图集名称.
    '''

    url, name = info
    path = 'temp/%s' % name
    if not os.path.exists(path):
        os.mkdir(path)
    with requests.Session() as session:
        for i, img_url in enumerate(img_url_list(url), 1):
            r = session.get(img_url)
            if r:
                with open('%s/%s.jpg' % (path, i), 'wb') as f:
                    f.write(r.content)


@finished
def main():
    main_url = 'http://www.mzitu.com'
    if not os.path.exists('temp'):
        os.mkdir('temp')
    pool = Pool(4)
    pool.map(download, post_info_list(main_url, 1, 2))


if __name__ == '__main__':
    main()