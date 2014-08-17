Title:  Packaging and Distributing a Kivy application on Linux
Author: raj
Tags:   kivy, linux, ubuntu
Date:   2014-08-16


The [Kivy library](http://kivy.org) can be used to create cross-platform desktop and
mobile apps that can be distributed on Linux, OS X, Windows, iOS, and Android. Packaging
Kivy apps on Linux is not well-supported. Here is how to get it to work:



## 1. Use a Vagrantfile to bootstrap a development environment

There are a lot of dependencies for kivy development, and a lot of different ways to
install them. In order to help you get started, I made a Vagrantfile to set up a
Kivy dev environment.

The Vagrantfile installs `python`, `kivy`, and `pyinstaller` in an Ubuntu VM, and then
packages a kivy example app into a `.deb`. You end up with a double-clickable application
that works like a regular linux desktop app.

The Vagrantfile and instructions on how to use it are here:
[https://github.com/rajbot/kivy_pyinstaller_linux_example](https://github.com/rajbot/kivy_pyinstaller_linux_example)


<br/>


## 2. Install Kivy using `pip`, and not from the provided PPA

If you don't use the Vagrantfile above and want to install Kivy yourself, do not
install it using the PPA. This is because we are going to use PyInstaller to
create a linux executable, and we will need the PyInstaller hooks from the `kivy.tools`
package, but the PPA does not include `kivy.tools`.

This [bash script](https://github.com/rajbot/kivy_pyinstaller_linux_example/blob/master/bootstrap.sh)
will show you how to install Kivy in a virtualenv so that you can use the PyInstaller hooks.


<br/>


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


<br/>


## 4. Package your executable in a `.deb` file

Once you make an executable, you can give it a nice icon and Ubuntu `.desktop`
file and package it in a `.deb` for distribution. Steps to create the `.deb` can
be found in [bootstrap.sh](https://github.com/rajbot/kivy_pyinstaller_linux_example/blob/master/bootstrap.sh),
from step #1 above. At minimum, your `.deb` package should:

- Install your application in a binary directory, such as `/usr/local/bin/my-app`
- Install an icon in `/usr/share/pixmaps/my-app.png`
- Install a `.desktop` file in `/usr/share/applications/my-app.desktop`

Debian version numbers are in the form {major}.{minor}-{patchlevel}. To make the `.deb`,
first create the directory structure below:

    - my-app_1.0-1
        - DEBIAN
            - control
        - usr
            - local
                - bin
                    - my-app
            - share
                - applications
                    - my-app.desktop
                - pixmaps
                    - my-app.png

Now you can package your app by typing `dpkg-deb --build myapp_1.0-0`. You can then
install the resulting package by typing `sudo dpkg -i myapp_1.0-0.deb`.

The `DEBIAN/control` file should look like this:

    Source: my-app
    Priority: extra
    Maintainer: raj <raj@unknown>
    Build-Depends: debhelper (>= 8.0.0)
    Standards-Version: 3.9.2
    Package: my-app
    Version: 1.0-0
    Architecture: i386
    Description: Should description
     Long description string (starts with a whitespace)

To give your executable a first-class Ubuntu application, you will need to create a
`.desktop` file, which will tell Ubuntu about its icon, version, and name. `my-app.desktop`
should look like this:

    [Desktop Entry]
    Version=1.0
    Name=My Application
    Comment=Example App
    Exec=/usr/local/bin/my-app
    Icon=my-app
    Type=Application
    Categories=Utility;Application;

Note that `Version` above refers to the version of the `.desktop` format (and
not the version of the app), and should always be "1.0". The `Icon` entry does
not need a full path or extension. Ubuntu will look for your icon in
`/usr/share/pixmaps`.

<br/>


## 5. Set up a signed trivial APT repository to distribute your `.deb`

To distribute your `.deb` file to end users, you will want to set up an APT
repository, which must be signed with a GPG key if you want to allow for
programatic installation or automatic updates.

Instructions for [setting up a signed trivial repo are provided here](/creating-a-trivial-signed-apt-repository.html).
