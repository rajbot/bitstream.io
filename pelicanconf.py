#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

DELETE_OUTPUT_DIRECTORY = False
OUTPUT_PATH = '../rajbot.github.io/'

AUTHOR = u'rajbot'
SITENAME = u'bitstream.io'
SITEURL = ''

TIMEZONE = 'America/Los_Angeles'

DEFAULT_LANG = u'en'

DEFAULT_DATE = 'fs'

# Feed generation is usually not desired when developing
#FEED_ALL_ATOM = None
#CATEGORY_FEED_ATOM = None
#TRANSLATION_FEED_ATOM = None

# Blogroll
LINKS =  (('raj.blog.archive.org', 'http://raj.blog.archive.org'),
          ('TikiRobot', 'http://tikirobot.net'),
          ('Archives', '/archives.html'),
         )

# Social widget
SOCIAL = (('github', 'http://github.com/rajbot'),
          ('twitter', 'http://twitter.com/rajbot'),
          ('email', 'mailto:raj@bitstreamFIXME.eyeoh'),
         )

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

THEME = 'bitstream.io_pelican_theme'
