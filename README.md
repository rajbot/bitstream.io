This repository contains [Pelican](http://pelican.readthedocs.org/en/3.2/) source files for http://bitstream.io.

To build the site, you will need to install the following:

* [Install pelican in a virtualenv](http://pelican.readthedocs.org/en/3.2/getting_started.html#installing-pelican)
* Clone the source repo: https://github.com/rajbot/bitstream.io
* Clone the build repo: https://github.com/rajbot/rajbot.github.io
* Clone the theme repo: https://github.com/rajbot/bitstream.io_pelican_theme

Now, you can activate your virtualenv, and then use [pelican-themes](http://pelican.readthedocs.org/en/3.2/pelican-themes.html) to install the theme: `pelican-themes --symlink /path/to/theme`

Now, you can edit and publish the site:

```bash
$ cd ~/dev/bitstream.io
$ make devserver   #starts a server on localhost:8000 and auto-regenerates content
$ make html        #useful if content doesn't automatically regenerate
$ ./develop_server.sh stop #stop the dev server

#after making local changes, you can publish:
$ git commit . #commit your source changes
$ git push
$ pelican --verbose content/ -s pelicanconf.py #writes files into the build repo
$ cd ../rajbot.github.io/
$ git commit . #commit your build changes
$ git push

#if you made changes to the theme repo, remember to push those as well
```

