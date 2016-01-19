import scrapy
from scrapy.http import Request
from scrapy.selector import Selector
from librivox_scrape.items import LibrivoxItem # , DownloadItem
import json
import requests


class LibriVoxSpider(scrapy.Spider):
    """
    This is the spider that crawls the given start_urls.
    """
    name = "librivox"
    allowed_domains = ["librivox.org"]
    start_urls = [
        'https://librivox.org/search/get_results?primary_key=0&search_category=title&sub_category=&search_page=1&search_order=alpha&project_type=either'
    ]
    headers = {
        'Host': 'librivox.org',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://librivox.org/search',
        'Connection': 'keep-alive  '
    }

    def __init__(self, *args, **kwargs):
        self.handle_pagination()
        super(LibriVoxSpider, self).__init__(*args, **kwargs)

    def handle_pagination(self):
        response = requests.get(
            url=self.start_urls[0],
            headers=self.headers
        )
        pagination = json.loads(response.content)['pagination']
        page_selector = Selector(text=pagination)
        last_page_number = page_selector.xpath("//a[@class='page-number last']/@data-page_number").extract()[0]

        start_page = self.start_urls[0]
        start_page_list = start_page.split('search_page=')
        start_page_list[0] += 'search_page='
        start_page_list[1] = start_page_list[1][1:]

        self.start_urls = [
            str(i).join(start_page_list) for i in range(1, int(last_page_number)+1)
        ]


    def make_requests_from_url(self, url):
        return scrapy.Request(
            url=url,
            headers=self.headers
        )

    def parse(self, response):
        body = json.loads(response.body_as_unicode())['results']
        selector = Selector(text=body)
        for sel in selector.xpath("//li[@class='catalog-result']"):
            detailed_page_link = sel.xpath("./div[@class='result-data']/h3/a/@href").extract()[0]
            book_meta = sel.xpath("./div[@class='result-data']/p[@class='book-meta']/text()").extract()
            status = book_meta[0].split('|')[0].strip()
            if status == 'Complete':
                yield Request(
                    detailed_page_link, callback=self.parse_detailed_page
                )


    def parse_detailed_page(self, response):
        item = LibrivoxItem()
        item['Title'] = response.xpath("//div[@class='content-wrap clearfix']/h1/text()").extract()[0].encode('utf-8')
        author_details = response.xpath("//div[@class='content-wrap clearfix']/p[@class='book-page-author']/a/text()").extract()[0]
        item['Author'] = author_details.split('(')[0].strip().encode('utf-8')
        item['AuthorLifetime'] = author_details.split('(')[1].replace(')', '').strip().encode('utf-8')
        try:
            # description is inside <p> tag
            item['DescriptionText'] = response.xpath("//div[@class='content-wrap clearfix']/div[@class='description']/p/text()").extract()[0].encode('utf-8')
        except:
            # description is inside div
            item['DescriptionText'] = response.xpath("//div[@class='content-wrap clearfix']/div[@class='description']/text()").extract()[0].encode('utf-8')
        genre_and_language_sel = response.xpath("//div[@class='content-wrap clearfix']/p[@class='book-page-genre']")
        item['Genre'] = genre_and_language_sel[0].xpath('./text()').extract()[0].encode('utf-8')
        item['Language'] = genre_and_language_sel[1].xpath('./text()').extract()[0].strip().encode('utf-8')
        arts_sel = response.xpath("//div[@class='book-page-book-cover']/a[@class='download-cover']")
        cover_art_link = arts_sel[0].xpath('./@href').extract()[0]
        cd_case_insert_art_link = arts_sel[1].xpath('./@href').extract()[0]

        item['file_urls'] = []
        item['file_urls'].append({
            "file_url": cover_art_link,
            "file_name": cover_art_link.split('/')[-1]
        })
        item['file_urls'].append({
            "file_url": cd_case_insert_art_link,
            "file_name": cd_case_insert_art_link.split('/')[-1]
        })

        item['HasCoverArt'] = 'True' if cover_art_link else 'False'
        item['HasCdInsertArt'] = 'True' if cd_case_insert_art_link else 'False'
        item['TotalLength'] = response.xpath("//dl[@class='product-details clearfix']/dd")[0].xpath('./text()').extract()[0].encode('utf-8')
        item['CatalogedOnDate'] = response.xpath("//dl[@class='product-details clearfix']/dd")[2].xpath('./text()').extract()[0].encode('utf-8')
        try:
            # no link in reader
            item['Readers'] = response.xpath("//dl[@class='product-details clearfix']/dd")[3].xpath('./text()').extract()[0].encode('utf-8')
        except:
            # link of reader
            item['Readers'] = response.xpath("//dl[@class='product-details clearfix']/dd")[3].xpath('./a/text()').extract()[0].encode('utf-8')
        item['NumberOfReaders'] = str(len(item['Readers'].split(',')))
        try:
            item['AuthorWikipediaLink'] = response.xpath("//div[@class='book-page-sidebar']")[2].xpath('./p')[2].xpath('./a/@href').extract()[0].encode('utf-8')
        except:
            # wikipedia link of author not present
            item['AuthorWikipediaLink'] = ''
        try:
            item['WikipediaLink'] = response.xpath("//div[@class='book-page-sidebar']")[2].xpath('./p')[3].xpath('./a/@href').extract()[0].encode('utf-8')
        except:
            # wikipedia link not present
            item['WikipediaLink'] = ''
        item['LibrivoxUrlOfTitle'] = response.request.url.encode('utf-8')
        links_to_all_128k_mp3_files = []
        audio_file_urls = []
        # for count, each_chapter in enumerate(response.xpath("//table[@class='chapter-download']/tbody/tr"), 1):
        for each_chapter in response.xpath("//table[@class='chapter-download']/tbody/tr"):
            chapter_link = each_chapter.xpath('./td')[1].xpath('./a/@href').extract()[0].encode('utf-8')
            links_to_all_128k_mp3_files.append(chapter_link)
            # if count == 26:
            audio_file_urls.append({
                "file_url": chapter_link,
                "file_name": chapter_link.split('/')[-1]
            })
            # break
        item['LinksToAll128kMp3Files'] = ','.join(links_to_all_128k_mp3_files)
        item['file_urls'].extend(audio_file_urls)
        yield item
        # yield item
