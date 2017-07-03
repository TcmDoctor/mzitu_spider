#!/usr/bin/env python3
# coding:utf-8

r'''抓取指定页之间所有mzitu套图，保存在当前目录的temp目录下.

'''

import os
from multiprocessing import Pool

import myrequests as requests
from bs4 import BeautifulSoup
from finished import finished


def post_url_list(url, x=1, y=2):
    r'''获取指定页之间所有图集的url.

    :param  url: str, 主链接.
    :param  x: int, 起始页.
    :param  y: int, 结束页.

    :return post_url: str, 图集链接.
    '''

    with requests.Session() as session:
        for i in range(x, y):
            if i == 1:
                page_url = url
            else:
                page_url = '%s/page/%s' % (url, i)
            r = session.get(page_url)
            if r:
                soup = BeautifulSoup(r.text, 'lxml')
                post_tag_list = soup.select('div.postlist li > span > a')
                for post_tag in post_tag_list:
                    post_url = post_tag.get('href')
                    yield post_url


def download(url):
    r'''以图集名创建文件夹, 下载图集中所有图片.

    :param  url: str, 图集链接.
    '''

    with requests.Session() as session:
        r = session.get(url)
        if r:
            soup = BeautifulSoup(r.text, 'lxml')
            post_name = soup.select('h2.main-title')[0].get_text()
            path = 'temp/%s' % post_name
            if not os.path.exists(path):
                os.mkdir(path)
            page_number = soup.select('div.pagenavi a span')[-2].get_text()
            img_url = soup.select('div.main-image img')[0].get('src')
            r = session.get(img_url)
            if r:
                with open('%s/1.jpg' % path, 'wb') as f:
                    f.write(r.content)

            for i in range(2, int(page_number) + 1):
                page_url = '%s/%s' % (url, i)
                r = session.get(page_url)
                if r:
                    soup = BeautifulSoup(r.text, 'lxml')
                    img_url = soup.select('div.main-image img')[0].get('src')
                    r = session.get(img_url)
                    if r:
                        with open('%s/%s.jpg' % (path, i), 'wb') as f:
                            f.write(r.content)


@finished
def main():
    '''主函数.'''

    main_url = 'http://www.mzitu.com'
    if not os.path.exists('temp'):
        os.mkdir('temp')
    with Pool(2) as pool:
        pool.map(download, post_url_list(main_url))


if __name__ == '__main__':
    main()
