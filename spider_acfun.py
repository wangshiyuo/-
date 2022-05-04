import asyncio
import random
import shutil
import aiofiles
import requests
import aiohttp
import re
import m3u8
import os


class Spider:
    """一个爬虫类"""
    def __init__(self, path, page):
        self.base_url = 'https://www.acfun.cn/{}'  # Acfun首页
        self.page_url = 'https://www.acfun.cn/v/list218/index.htm\
            ?sortField=rankScore&duration=all&date=default&page={}'  # 详情页
        self.page = page  # 下载页数
        self.path = path  # 存放目录
        self.data_url = 'https://tx-safety-video.acfun.cn/mediacloud/acfun/acfun_video/{}'  # ts文件页
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)\
             AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'
        }

    async def parse_page(self, url):
        """获取首页页面，并提取m3u8视频链接"""
        async with aiohttp.request('GET', url=url, headers=self.headers) as res:
            m3u8_links = re.findall('<a.href=\'(.*?)\'', await res.text())  # 提取m3u8视频链接
            for m3u8_link in m3u8_links:
                async with aiohttp.request('GET', url='https://www.acfun.cn' + m3u8_link, headers=self.headers) as r:
                    result = await r.text()
                    backupurl = re.findall(r'backupUrl(.+?)\"]', result)[0].replace('"', '').split('\\')[-2]
                    name = re.findall('<h1.class="title"><span>(.*?)</span></h1>', result)[0]
                    author = re.findall("<div.class='up-info'>.*?>(.*?)</a>", result)[0]
                    video_name = str(name) + '-' + str(author)
                    await self.loading_m3u8(backupurl, video_name)

    async def loading_m3u8(self, url, file_name):
        """下载m3u8视频"""
        ts_list = m3u8.load(url).segments  # 获取每个ts文件的链接
        if len(ts_list) == 1:  # 如果只有一个ts文件，可以直接保存
            file_name = f'{file_name}.mp4'
            async with aiofiles.open(f'{self.path}/{file_name}', 'wb') as f:
                t_url = self.data_url.format(ts_list[0].uri)  # 获取ts链接
                await f.write(requests.get(t_url).content)  # 保存视频
            print(f'{file_name}  下载完成!')
            return ''

        download_path = self.path + '/' + str(random.randint(100000, 666666))  # 随机生成一个临时目录来存放ts文件
        os.mkdir(download_path)  # 创建这个目录
        for i, ts in enumerate(ts_list):  # 遍历m3u8所有ts地址
            ts_url = self.data_url.format(ts.uri)  # 获取ts链接
            async with aiohttp.request('GET', url=ts_url, headers=self.headers) as res:
                ts_data = await res.read()  # 下载ts文件
            async with aiofiles.open(f'{download_path}/{i}', mode='wb') as f:
                await f.write(ts_data)  # 保存ts文件
        await self.combine_ts_video(download_path, file_name)

    async def combine_ts_video(self, download_path, file_name):
        """对ts文件合并"""
        all_ts = os.listdir(download_path)  # 遍历ts文件个数
        all_ts.sort(key=lambda x: int(x))  # 对ts文件进行排序
        file_name = f'{file_name}.mp4'  # 文件存放路径和文件名
        async with aiofiles.open(f'{self.path}/{file_name}', mode='wb+') as f:
            for i in range(len(all_ts)):  # 遍历每个ts视频
                ts_video = open(os.path.join(download_path, all_ts[i]), 'rb')  # 打开ts视频
                await f.write(ts_video.read())  # 保存ts视频
                ts_video.close()  # 关闭ts视频
        shutil.rmtree(download_path)  # 删除临时存放目录
        print(f'{file_name}  下载完成!')

    async def run(self):
        """ 运行入口"""
        if os.path.exists(self.path) is False:
            os.mkdir(self.path)    # 生成下载存放目录
        tasks = [self.parse_page(self.page_url.format(i)) for i in range(1, self.page)]
        await asyncio.wait(tasks)   # 启动运行


if __name__ == '__main__':
    load_path = 'video'  # 设置下载路径
    load_page = 10  # 设置下载的页数
    spider = Spider(load_path, load_page)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(spider.run())
