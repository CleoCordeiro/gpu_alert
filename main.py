import time
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from gpus.gpus.spiders.kabum import KabumSpider

from multiprocessing import Process
def execute_crawling():
    process = CrawlerProcess(get_project_settings())#same way can be done for Crawlrunner
    process.crawl(KabumSpider)
    process.start()

if __name__ == '__main__':
   while True:
        p = Process(target=execute_crawling)
        p.start()
        p.join() # this blocks until the process terminates
        time.sleep(5)