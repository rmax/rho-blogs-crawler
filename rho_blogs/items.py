# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class Author(Item):
    name = Field()
    profile_url = Field()
    avatar_url = Field()

class BlogAuthor(Author):
    pass

class CommentAuthor(Author):
    pass

class Post(Item):
    author = Field()
    title = Field(default="")
    content = Field()
    posted = Field()
    origin_url = Field()

class BlogPost(Post):
    tags = Field(default=[])
    comments = Field(default=[])

class CommentPost(Post):
    pass


