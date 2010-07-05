import lxml.html

from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.loader.processor import Compose
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import HtmlXPathSelector

from rho_blogs.loaders import (BlogPostLoader, BlogAuthorLoader,
                               CommentPostLoader, CommentAuthorLoader)
from rho_blogs.processors import StringToDatetime


def strip_profile_url(value):
    """strip /weblog/ from profile url"""
    if value.endswith('weblog/'):
        value = value[:-7]
    return value

def clean_post(value):
    """Remove unwanted elements in post content"""
    doc = lxml.html.fragment_fromstring(value)
    doc.tag = 'div' # replaces <li>
    doc.attrib.clear()

    # remove comment owner info
    for e in doc.xpath('//div[@class="weblog_keywords"]'):
        e.drop_tree()

    return lxml.html.tostring(doc)

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


class ElggBlogAuthorLoader(BlogAuthorLoader):
    profile_url_out = Compose(BlogAuthorLoader.default_output_processor,
                              strip_profile_url)


class ElggBlogPostLoader(BlogPostLoader):
    content_out = Compose(BlogPostLoader.default_output_processor,
                          clean_post)
    posted_out = Compose(BlogPostLoader.default_output_processor,
                         StringToDatetime('%B %d, %Y'))


class ElggCommentAuthorLoader(CommentAuthorLoader):
    profile_url_out = Compose(CommentAuthorLoader.default_output_processor,
                              strip_profile_url)


class ElggCommentPostLoader(CommentPostLoader):
    content_out = Compose(CommentPostLoader.default_output_processor,
                          clean_comment)
    posted_out = Compose(CommentPostLoader.default_output_processor,
                         lambda s: s.split(' on ')[1],
                         StringToDatetime('%A, %d %B %Y, %H:%M %Z |'))



class ElggBlogArchiveSpider(CrawlSpider):

    username = None
    domain = None

    archive_url = 'http://%(domain)s/%(username)s/weblog/archive/'

    content_selector_id = ''
    content_selector_xpath = ''

    post_loader = ElggBlogPostLoader
    author_loader = ElggBlogAuthorLoader
    comment_loader = ElggCommentPostLoader
    comment_author_loader = ElggCommentAuthorLoader

    def __init__(self):
        assert self.username and self.domain
        self.allowed_domains = [self.domain]
        self.start_urls = [self.archive_url % {'username': self.username,
                                               'domain': self.domain}]

        archives_le = SgmlLinkExtractor(allow=self.get_archive_links_re(),
                                        restrict_xpaths=self.get_archive_links_xpath())
        posts_le = SgmlLinkExtractor(allow=self.get_post_links_re(),
                                     restrict_xpaths=self.get_post_links_xpath())

        self.rules = (
            Rule(archives_le, follow=True),
            Rule(posts_le, callback='parse_post'),
        )

        super(ElggBlogArchiveSpider, self).__init__()

    def get_content_xpath(self):
        if self.content_selector_xpath:
            return self.content_selector_xpath
        else:
            return '//div[@id="%s"]' % self.content_selector_id

    def get_archive_links_re(self):
        return r'/archive/\d{4}/\d{2}/'

    def get_archive_links_xpath(self):
        return '%s/ul/li' % self.get_content_xpath()

    def get_post_links_re(self):
        return r'/weblog/.+'

    def get_post_links_xpath(self):
        return '%s//div[@class="weblog-title"]' % self.get_content_xpath()

    def get_post_author_xpaths(self):
        """
        Returns a tuple of xpath rules (container, name, profile_url, avatar_url)
        """
        return ('%s//div[@class="user"]' % self.get_content_xpath(),
                './/a[2]/text()',
                './/a[2]/@href',
                './/img/@src')

    def get_post_xpaths(self):
        """
        Returns a tuple of xpath rules:
            (container, title, content, tags, posted)

        Does not return origin_url because is taked from response.url
        """
        return (self.get_content_xpath(),
                './/div[@class="weblog-title"]//text()',
                './div[@class="weblog-post"]/div[@class="post"]',
                # only extract tags with links
                './/div[@class="weblog_keywords"]//a/text()',
                './/h2[@class="weblog_dateheader"]/text()',
               )

    def get_comments_xpath(self):
        return '%s//div[@id="comments"]/ol/li' % self.get_content_xpath()

    def get_comment_author_xpath(self):
        """
        Returns a tuple of relative xpath rules to each comment xpath rule:
            (container, name, profile_url, avatar_url)
        """
        return ('./div[@class="comment-owner"]/p',
                './a[2]/text()',
                './a[2]/@href',
                './a[1]/img/@src',
               )

    def get_comment_post_xpath(self):
        """
        Returns a tuple of relative xpath rules to each comment xpath rule:
            (container, content, posted, origin_url)
        """
        return ('.',
                '.',
                './div[@class="comment-owner"]/p/text()',
                './div[@class="comment-owner"]/p/a[3]/@href',
               )

    def parse_post_author(self, response):
        hxs = HtmlXPathSelector(response)
        container, name, profile_url, avatar_url = self.get_post_author_xpaths()

        author = self.author_loader(selector=hxs.select(container))
        author.add_xpath('name', name)
        author.add_xpath('profile_url', profile_url)
        author.add_xpath('avatar_url', avatar_url)

        return author.load_item()

    def parse_post_comments(self, response):
        hxs = HtmlXPathSelector(response)

        (author_container,
         author_name,
         author_profile_url,
         author_avatar_url) = self.get_comment_author_xpath()

        (container, content,
         posted, origin_url) = self.get_comment_post_xpath()

        comment_list = []
        for comment in hxs.select(self.get_comments_xpath()):
            author = self.comment_author_loader(selector=comment.select(author_container))
            author.add_xpath('name', author_name)
            author.add_xpath('profile_url', author_profile_url)
            author.add_xpath('avatar_url', author_avatar_url)

            comment = self.comment_loader(selector=comment.select(container))
            comment.add_xpath('content', content)
            comment.add_xpath('posted', posted)
            comment.add_xpath('origin_url', origin_url)

            comment.add_value('author', [author.load_item()])

            comment_list.append(comment.load_item())

        return comment_list

    def parse_post(self, response):
        hxs = HtmlXPathSelector(response)
        container, title, content, tags, posted = self.get_post_xpaths()

        post = self.post_loader(selector=hxs.select(container))
        post.add_value('origin_url', [unicode(response.url)])
        post.add_xpath('title', title)
        post.add_xpath('content', content)
        post.add_xpath('tags', tags)
        post.add_xpath('posted', posted)

        author = self.parse_post_author(response)
        post.add_value('author', [author])

        comments = self.parse_post_comments(response)
        post.add_value('comments', comments)

        return post.load_item()
