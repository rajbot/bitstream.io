Title:  Compiling and installing gphoto
Author: raj
Date:   2014-12-12 14:45
Tags:   gphoto

Here are instructions on how to compile and install the latest version of gphoto, from SVN.

```bash
# install dependencies (for Ubuntu 14.04)
$ sudo apt-get install automake autopoint gettext libtool libusb-dev libpopt-dev subversion
$ mkdir gphoto
$ cd gphoto

# compile libphoto2 and install into /usr/local/lib
$ svn co https://svn.code.sf.net/p/gphoto/code/trunk/libgphoto2
$ cd libgphoto2/
$ autoreconf --install --symlink
$ ./configure --prefix=/usr/local
$ make
$ sudo make install
 
# compile gphoto2 and install into /usr/local/bin
$ cd ..
$ svn co https://svn.code.sf.net/p/gphoto/code/trunk/gphoto2
$ cd gphoto2/
$ autoreconf --install --symlink
$ PKG_CONFIG_PATH=/usr/local/lib/pkgconfig ./configure --prefix=/usr/local
$ make
$ sudo make install

```

Be sure to set LD_LIBRARY_PATH so that gphoto can find the correct version of libgphoto2
and libgphoto2_port:

```bash
$ LD_LIBRARY_PATH=/usr/local/lib /usr/local/bin/gphoto2 --version
gphoto2 2.5.5.1

Copyright (c) 2000-2014 Lutz Mueller and others

gphoto2 comes with NO WARRANTY, to the extent permitted by law. You may
redistribute copies of gphoto2 under the terms of the GNU General Public
License. For more information about these matters, see the files named COPYING.

This version of gphoto2 is using the following software versions and options:
gphoto2         2.5.5.1        gcc, popt(m), exif, no cdk, no aa, jpeg, no readline
libgphoto2      2.5.5.3        all camlibs, gcc, ltdl, EXIF
libgphoto2_port 0.12.0         gcc, ltdl, USB, serial without locking
```

These instructions were tested on Ubuntu 14.04, and will compile all camera drivers. 
