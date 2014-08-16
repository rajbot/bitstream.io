Title:  Packaging and Distributing a Kivy application on Linux
Author: raj
Tags:   kivy, linux, ubuntu
Date:   2014-08-16


The [Kivy library](http://kivy.org) can be used to create cross-platform desktop and
mobile apps that can be distributed on Linux, OS X, Windows, iOS, and Android. Packaging
Kivy apps on Linux is not well-supported. Here is how to get it to work:


## 1. Install Kivy using `pip`, and not from the provided PPA or `.deb`

We are going to use PyInstaller to create a linux executable. Kivy provides PyInstaller
hooks in the `kivy.tools` package, but PPA does not include `kivy.tools`


## 2. Use a Vagrantfile to bootstrap a development environment

There are a lot of dependencies for kivy development, and a lot of different ways to
install them. In order to help you get started, I made a Vagrantfile to set up a
Kivy dev environment.

The Vagrantfile installs `python`, `kivy`, and `pyinstaller` in an Ubuntu VM, and then
packages a kivy example app into a `.deb`. You end up with a double-clickable application
that works like a regular linux desktop app.

The Vagrantfile and instructions on how to use it are here:
[https://github.com/rajbot/kivy_pyinstaller_linux_example](https://github.com/rajbot/kivy_pyinstaller_linux_example)


## 3. Strip system libraries from the pyinstaller executable to ensure your app is relocatable

If you follow the setup instructions above, you will end up an executable that works only
on the machine it was built. If you try to copy it to another linux box, kivy will often
segfault on startup with this error message:

    Fatal Python Error: (pygame parachute) Segmentation Fault

To ensure the executable can run on as many different flavors of linux as possible, we
are going to strip out all binaries provided by system packages. We will distribute the
application in a `.deb` file and and use `.deb` dependencies to ensure required libraries
are installed on the target machine.

Here is a copy of a PyInstaller `.spec` file that installs Kivy hooks and strips out all
binaries that `dpkg -S` finds in a system-installed library:

```python
# -*- mode: python -*-
from kivy.tools.packaging.pyinstaller_hooks import install_hooks
install_hooks(globals())

def filter_binaries(all_binaries):
    '''Exclude binaries provided by system packages, and rely on .deb dependencies
    to ensure these binaries are available on the target machine.

    We need to remove OpenGL-related libraries so we can distribute the executable
    to other linux machines that might have different graphics hardware. If you
    bundle system libraries, your application might crash when run on a different
    machine with the following error during kivy startup:

    Fatal Python Error: (pygame parachute) Segmentation Fault

    If we strip all libraries, then PIL might not be able to find the correct _imaging
    module, even if the `python-image` package has been installed on the system. The
    easy way to fix this is to not filter binaries from the python-imaging package.

    We will strip out all binaries, except libpython2.7, which is required for the
    pyinstaller-frozen executable to work, and any of the python-* packages.
    '''

    print 'Excluding system libraries'
    import subprocess
    excluded_pkgs  = set()
    excluded_files = set()
    whitelist_prefixes = ('libpython2.7', 'python-')
    binaries = []

    for b in all_binaries:
        try:
            output = subprocess.check_output(['dpkg', '-S', b[1]], stderr=open('/dev/null'))
            p, path = output.split(':', 2)
            if not p.startswith(whitelist_prefixes):
                excluded_pkgs.add(p)
                excluded_files.add(b[0])
                print ' excluding {f} from package {p}'.format(f=b[0], p=p)
        except Exception:
            pass

    print 'Your exe will depend on the following packages:'
    print excluded_pkgs

    inc_libs = set(['libpython2.7.so.1.0'])
    binaries = [x for x in all_binaries if x[0] not in excluded_files]
    return binaries


a = Analysis(['scribe.py'],
             pathex=['.'],
             hiddenimports=[],
            )
pyz = PYZ(a.pure)

binaries = filter_binaries(a.binaries)

exe = EXE(pyz,
          [('scribe.kv', 'scribe.kv', 'DATA')],
          a.scripts,
          binaries, #a.binaries,
          a.zipfiles,
          a.datas,
          name='ia-scribe',
          debug=False,
          strip=None,
          upx=True,
          console=False )
```


## 4. Set up a signed trivial APT repository to distribute your `.deb`

Once you make an executable, you can give it a nice icon and `.desktop` file
and package it in a `.deb` for distribution. Steps to create the `.deb` can be
found in the `bootstrap.sh` file, run by the Vagrantfile in step #2 above.

To distribute your `.deb` file to end users, you will want to set up an APT
repository, which must be signed with a GPG key if you want to allow for
programatic installation or automatic updates.

Instructions for [setting up a signed trivial repo are provided here](/creating-a-trivial-signed-apt-repository.html).
