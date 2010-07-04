# See documentation in:
# http://doc.scrapy.org/topics/loaders.html

from scrapy.contrib.loader import XPathItemLoader
from scrapy.contrib.loader.processor import (Identity, Compose, Join,
                                             TakeFirst, MapCompose)

from rho_blogs.items import BlogPost, BlogAuthor, CommentPost, CommentAuthor


class BaseItemLoader(XPathItemLoader):
    default_input_processor = MapCompose(unicode.strip)
    default_output_processor = Join()


class BaseAuthorLoader(BaseItemLoader):
    pass


class BasePostLoader(BaseItemLoader):
    # author input is an Author item instance
    author_in = Identity()
    author_out = TakeFirst()
    # tags out just as list
    tags_out = Identity()
    # comments are a list of CommentPost item instances
    comments_in = Identity()
    comments_out = Identity()


class BlogPostLoader(BasePostLoader):
    default_item_class = BlogPost


class BlogAuthorLoader(BaseAuthorLoader):
    default_item_class = BlogAuthor


class CommentPostLoader(BasePostLoader):
    default_item_class = CommentPost


class CommentAuthorLoader(BaseAuthorLoader):
    default_item_class = CommentAuthor
