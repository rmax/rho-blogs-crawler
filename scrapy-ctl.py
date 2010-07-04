#!/usr/bin/env python

import os
os.environ.setdefault('SCRAPY_SETTINGS_MODULE', 'rho_blogs.settings')

from scrapy.cmdline import execute
execute()
