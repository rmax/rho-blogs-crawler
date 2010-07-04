# Scrapy settings for rho_blogs project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#
# Or you can copy and paste them from where they're defined in Scrapy:
# 
#     scrapy/conf/default_settings.py
#

BOT_NAME = 'rho_blogs'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['rho_blogs.spiders']
NEWSPIDER_MODULE = 'rho_blogs.spiders'
DEFAULT_ITEM_CLASS = 'rho_blogs.items.RhoBlogsItem'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)
