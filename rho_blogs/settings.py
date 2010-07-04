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

import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

BOT_NAME = 'rho_blogs'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['rho_blogs.spiders']
NEWSPIDER_MODULE = 'rho_blogs.spiders'
DEFAULT_ITEM_CLASS = 'rho_blogs.items.Post'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

CONCURRENT_ITEMS = 1
CONCURRENT_REQUESTS_PER_SPIDER = 1
CONCURRENT_SPIDERS = 2

DOWNLOAD_DELAY = 2
RETRY_TIMES = 5
HTTPCACHE_DIR = os.path.join(PROJECT_ROOT, 'cache')
HTTPCACHE_EXPIRATION_SECS = -1

STATS_DUMP = True
WEBSERVICE_ENABLED = False
TELNETCONSOLE_ENABLED = False
