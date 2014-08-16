Title:  Creating a Trivial, Signed APT Repository
Author: raj
Tags:   apt, debian, ubuntu
Date:   2014-08-13


Setting up an APT repository is a reasonable way to distribute `.deb`
packages to end users. You will want to create a signed repository, so
that users can perform automated updates of your software (e.g. using
`apt-get install -y`).

There are [two kinds of repositories](https://wiki.debian.org/HowToSetupADebianRepository#APT_Archive_Types),
"official" and "trivial". Trivial repositories are easier to set up than
the official variety, but setup of *signed* trivial repositories is not
well-documented. Here are instructions on how to set up your own repo:


Prerequisites:

- A `.deb` file, unsigned
- A machine with `gpg` installed
- RSA gpg keys created using `gpg --gen-key`


The repository is a simply a directory hierarchy. It can be local (e.g. on a usb stick) or
published to a web server. Here is what it should look like when we are done:

    - apt-repo/
        - foo.deb
        - Packages
        - Release
        - Release.gpg


Start by creating the hierarchy above with empty directories. Place `foo.deb` in the
`apt-repo` directory, and then follow these instructions to create the signed files:

```bash
#sign the .deb file
cd apt-repo
dpkg-sig --sign builder foo.deb
cd ..

#create the Packages.gz file
cd apt-repo
apt-ftparchive packages . > Packages
cd ..

#create the Release file
apt-ftparchive release apt-repo > apt-repo/Release

#create a detached ascii signature of the Release file
gpg --armor --sign --detach-sign apt-repo/Release.gpg apt-repo/Release
```

Now you can upload the `apt-repo` directory to a webserver. If the repo
path is `http://example.com/foo/apt-repo`, then end users will have to
add a file named `my-repo.list` to the `/etc/apt/sources.list.d` directory
that contains this line:

```bash
deb http://example.com/foo/apt-repo /
```


You now need to distribute your public key to end users, who will need to add it to their
apt keychain. To export the public key to a text file:

```bash
gpg --armor --export foo@example.com --output foo-public-key
```

Then upload `foo-public-key` to a webserver. End users can install the key like so:

```bash
curl http://example.com/foo-public-key | sudo apt-key add -
```

Once the key has been added, end users can install your software using `apt`:

```bash
sudo apt-get update
sudo apt-get install foo
```
