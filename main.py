import re

import openpyxl
import requests
from lxml import etree

def seafood_spider(year):
    search_data = ["对虾", "鲈鱼", "黑鱼", "鲤鱼", "草鱼"]
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    index = etree.HTML(requests.get("https://jiage.cngold.org/shuichan/list_3104_all.html").text)
    data_links = index.xpath("//div[@class='history_news_content']//a/@href")
    data_times = index.xpath("//div[@class='history_news_content']//a/text()")

    for data_index, now_link in enumerate(data_links):
        if str(year) in data_times[data_index]:
            items_res = requests.get(now_link)
            items_res.encoding = "utf-8"
            items_html = etree.HTML(items_res.text)
            items_title = items_html.xpath("//ul[@class='news_list pb20']//a/text()")
            items_links = items_html.xpath("//ul[@class='news_list pb20']//a/@href")
            if len(items_title) == 0 and len(items_links) == 0:
                items_title = items_html.xpath("//div[@class='left_info']//a/text()")
                items_links = items_html.xpath("//div[@class='left_info']//a/@href")
                second_page = items_html.xpath("//div[@class='show_info_page']//a/@href")
                if len(second_page) != 0:
                    print(second_page[0])
                    items_res = requests.get(second_page[0])
                    items_res.encoding = "utf-8"
                    items_html = etree.HTML(items_res.text)
                    items_title = items_title + items_html.xpath("//div[@class='left_info']//a/text()")
                    items_links = items_links + items_html.xpath("//div[@class='left_info']//a/@href")
            for index, title in enumerate(items_title):
                for search in search_data:
                    if search in title:
                        detail_res = requests.get(items_links[index])
                        detail_res.encoding = "utf-8"
                        detail_html = etree.HTML(detail_res.text)
                        if "2014" in data_times[data_index]:
                            money = detail_html.xpath("//div[@class='art_content']//tr[2]//td[2]/text()")
                            if len(money) == 0:
                                continue
                            elif bool(re.search(r'\d', money[0])) == 0:
                                money = detail_html.xpath("//tbody[@id='price_tbody']//tr[1]//td[3]/text()")
                            if len(money) == 0:
                                money = detail_html.xpath("//div[@class='art_content']//tbody//tr[1]//td[4]/text()")[0]
                            else:
                                money = re.findall(r'[1-9]\d*.\d*|0.\d*[1-9]\d*', money[0])[0]
                            sheet.append((search, data_times[data_index], money.strip()))
                        elif "2015" in data_times[data_index]:
                            money = detail_html.xpath("//div[@class='art_content']//table//tr[4]//td[2]/text()")
                            if len(money) == 0:
                                money = detail_html.xpath("//div[@id='zoom']//table//tr[2]//td[2]//text()")
                                if len(money) != 0:
                                    money = re.findall(r'[1-9]\d*.\d*|0.\d*[1-9]\d*', money[0])[0]
                                else:
                                    money = 0
                            else:
                                money = money[0].strip()
                            sheet.append((search, data_times[data_index], money))
                        else:
                            money = detail_html.xpath("//div[@class='art_content']//table//tr[4]//td[2]/text()")
                            if len(money) != 0:
                                sheet.append((search, data_times[data_index], money[0].strip()))
    workbook.save("./seafoods_{year}.xlsx".format(year=year))

if __name__ == '__main__':
    seafood_spider(2021)
