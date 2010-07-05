# See documentation in:
# http://doc.scrapy.org/topics/spiders.html

from scrapy.contrib.loader.processor import Compose

from rho_blogs.processors import StringToDatetime
from rho_blogs.spider import (ElggBlogArchiveSpider,
                              ElggBlogPostLoader,
                              ElggCommentPostLoader)


class AjayuBlogPostLoader(ElggBlogPostLoader):
    posted_out = Compose(ElggBlogPostLoader.default_output_processor,
                         StringToDatetime('%B %d, %Y', locale='en_US.UTF-8'))


class AjayuCommentPostLoader(ElggCommentPostLoader):
    posted_out = Compose(ElggCommentPostLoader.default_output_processor,
                         lambda s: s.split(' on ')[1],
                         StringToDatetime('%A, %d %B %Y, %H:%M %Z |', locale='en_US.UTF-8'))


class AjayuSpider(ElggBlogArchiveSpider):
    name = 'ajayu'
    domain = 'ajayu.memi.umss.edu.bo'
    username = 'rho'

    content_selector_id =  'content'

    post_loader = AjayuBlogPostLoader
    comment_loader = AjayuCommentPostLoader


SPIDER = AjayuSpider()
