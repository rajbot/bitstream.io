#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'rajbot'
SITENAME = u'bitstream.io'
SITEURL = ''

TIMEZONE = 'Europe/Paris'

DEFAULT_LANG = u'en'

DEFAULT_DATE = 'fs'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None

# Blogroll
LINKS =  (('TikiRobot', 'http://tikirobot.net'),
          ('Internet Archive', 'http://archive.org'),)

# Social widget
SOCIAL = (('twitter', 'http://twitter.com/rajbot'),
          ('github', 'http://github.com/rajbot'),)

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

THEME = 'notmyidea_bitstream.io'

MD_EXTENSIONS = ['codehilite','extra']
