# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class LibrivoxItem(scrapy.Item):
    # define the fields for the item here
    Title = scrapy.Field()
    Author = scrapy.Field()
    AuthorLifetime = scrapy.Field()
    TotalLength = scrapy.Field()
    Language = scrapy.Field()
    Genre = scrapy.Field()
    Readers = scrapy.Field()
    NumberOfReaders = scrapy.Field()
    WikipediaLink = scrapy.Field()
    AuthorWikipediaLink = scrapy.Field()
    CatalogedOnDate = scrapy.Field()
    DescriptionText = scrapy.Field()
    LibrivoxUrlOfTitle = scrapy.Field()
    LinksToAll128kMp3Files = scrapy.Field()
    HasCoverArt = scrapy.Field()
    HasCdInsertArt = scrapy.Field()

    file_urls = scrapy.Field()
    files = scrapy.Field()
