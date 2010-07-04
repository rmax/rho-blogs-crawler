# See documentation in:
# http://doc.scrapy.org/topics/spiders.html
import lxml.html

from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.loader.processor import Compose
from scrapy.contrib.spiders import CrawlSpider, Rule

from rho_blogs.loaders import (BlogPostLoader, BlogAuthorLoader,
                               CommentPostLoader, CommentAuthorLoader)
from rho_blogs.processors import StringToDatetime


def process_profile_url(value):
    """strip /weblog/ from profile url"""
    if value.endswith('weblog/'):
        value = value[:-7]
    return value

def clean_comment(value):
    """Remove unwanted elements in comment content"""
    doc = lxml.html.fragment_fromstring(value)
    doc.tag = 'div' # replaces <li>
    doc.attrib.clear()

    # remove empty links without childrens. e.g. name anchors
    for e in doc.xpath('//a'):
        if not e.getchildren() and not e.text:
            e.drop_tag()

    # remove comment owner info
    for e in doc.xpath('//div[@class="comment-owner"]'):
        e.drop_tree()

    return lxml.html.tostring(doc)

def clean_post(value):
    """Remove unwanted elements in post content"""
    doc = lxml.html.fragment_fromstring(value)
    doc.tag = 'div' # replaces <li>
    doc.attrib.clear()

    # remove comment owner info
    for e in doc.xpath('//div[@class="weblog_keywords"]'):
        e.drop_tree()

    return lxml.html.tostring(doc)

class AjayuBlogAuthorLoader(BlogAuthorLoader):
    profile_url_out = Compose(BlogAuthorLoader.default_output_processor,
                              process_profile_url)


class AjayuCommentAuthorLoader(CommentAuthorLoader):
    profile_url_out = Compose(CommentAuthorLoader.default_output_processor,
                              process_profile_url)


class AjayuBlogPostLoader(BlogPostLoader):
    content_out = Compose(BlogPostLoader.default_output_processor,
                          clean_post)
    posted_out = Compose(BlogPostLoader.default_output_processor,
                         StringToDatetime('%B %d, %Y'))


class AjayuCommentPostLoader(CommentPostLoader):
    content_out = Compose(CommentPostLoader.default_output_processor,
                          clean_comment)
    posted_out = Compose(CommentPostLoader.default_output_processor,
                         lambda s: s.split(' on ')[1],
                         StringToDatetime('%A, %d %B %Y, %H:%M %Z |'))


class AjayuSpider(CrawlSpider):
    name = 'ajayu'
    allowed_domains = ['ajayu.memi.umss.edu.bo']
    start_urls = ['http://ajayu.memi.umss.edu.bo/rho/weblog/archive/']

    rules = (
        # follow month's archives
        Rule(SgmlLinkExtractor(allow=r'/archive/\d{4}/\d{2}/',
                               restrict_xpaths=r'//div[@id="content"]/ul/li'),
            follow=True),
        # follow post links
        Rule(SgmlLinkExtractor(allow=r'/weblog/.+',
                               restrict_xpaths=r'//div[@id="content"]//h3'),
             callback='parse_post'),
    )

    def parse_post(self, response):
        hxs = HtmlXPathSelector(response)
        content_hxs = hxs.select('//div[@id="content"]')

        author = AjayuBlogAuthorLoader(selector=content_hxs.select('.//div[@class="user"]'))
        author.add_xpath('name', './/a[2]/text()')
        author.add_xpath('profile_url', './/a[2]/@href')
        author.add_xpath('avatar_url', './/img/@src')

        post = AjayuBlogPostLoader(selector=content_hxs)
        post.add_value('author', [author.load_item()])
        post.add_xpath('title', './/div[@class="weblog-title"]/h3//text()')
        post.add_xpath('content', './div[@class="weblog-post"]/div[@class="post"]')
        post.add_xpath('posted', './/h2[@class="weblog_dateheader"]/text()')
        post.add_value('origin_url', [unicode(response.url)])

        post.add_xpath('tags', './/div[@class="weblog_keywords"]//a/text()')

        comment_list = []
        for comment_hxs in content_hxs.select('.//div[@id="comments"]/ol/li'):
            comment_author = AjayuCommentAuthorLoader(selector=comment_hxs.select('./div[@class="comment-owner"]/p'))
            comment_author.add_xpath('name', './a[2]/text()')
            comment_author.add_xpath('profile_url', './a[2]/@href')
            comment_author.add_xpath('avatar_url', './a[1]/img/@src')

            comment = AjayuCommentPostLoader(selector=comment_hxs)
            comment.add_value('author', [comment_author.load_item()])
            comment.add_xpath('content', '.')
            comment.add_xpath('posted', './div[@class="comment-owner"]/p/text()')
            comment.add_xpath('origin_url', './div[@class="comment-owner"]/p/a[3]/@href')

            comment_list.append(comment.load_item())

        post.add_value('comments', comment_list)

        return post.load_item()


SPIDER = AjayuSpider()
