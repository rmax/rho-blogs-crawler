# See documentation in:
# http://doc.scrapy.org/topics/spiders.html

from scrapy.contrib.loader.processor import Compose

from rho_blogs.processors import StringToDatetime
from rho_blogs.spider import (ElggBlogArchiveSpider,
                              ElggBlogPostLoader,
                              ElggCommentPostLoader)


class SlobBlogPostLoader(ElggBlogPostLoader):
    posted_out = Compose(ElggBlogPostLoader.default_output_processor,
                         StringToDatetime('%B %d, %Y', locale='es_ES.UTF-8'))


class SlobCommentPostLoader(ElggCommentPostLoader):
    posted_out = Compose(ElggCommentPostLoader.default_output_processor,
                         lambda s: s.split(' on ')[1],
                         StringToDatetime('%A, %d %B %Y, %H:%M %Z |', locale='es_ES.UTF-8'))


class SlobSpider(ElggBlogArchiveSpider):
    name = 'slob'
    domain = 'www.softwarelibre.org.bo'
    username = 'rolando'

    content_selector_id = 'splitpane-content'

    post_loader = SlobBlogPostLoader
    comment_loader = SlobCommentPostLoader


SPIDER = SlobSpider()
