Title:  Creating a Trivial, Signed APT Repository
Author: raj
Tags:   apt, debian, ubuntu
Date:   2014-08-13


Setting up an APT repository is a reasonable way to distribute `.deb`
packages to end users. You will want to create a signed repository, so
that users can perform automated updates of your software (e.g. using
`apt-get install -y`).

There are two kinds of repositories, "official" and "trivial". Trivial
repositories are easier to set up than the official variety, but setup
of signed trivial repositories is not well-documented. Here are
instructions on how to set up your own repo:


Prerequisites:

- A `.deb` file, unsigned
- A machine with `gpg` installed
- RSA gpg keys created using `gpg --gen-key`


The repository is a simply a directory hierarchy. It can be local (e.g. on a usb stick) or
published to a web server. Here is what it should look like when we are done:

    - aptrepo/
        - binary/
            - Packages.gz
            - foo.deb
        - Release
        - Release.gpg


Start by creating the hierarchy above with empty directories. Place `foo.deb` in the
`binary` directory, and then follow these instructions to create the signed files:

```bash
#sign the .deb file
cd ~/aptrepo/binary
dpkg-sig --sign builder foo.deb

#create the Packages.gz file
cd ~/aptrepo
apt-ftparchive packages binary | gzip -9c > binary/Packages.gz

#create the Release file
cd ~/aptrepo
apt-ftparchive release . > Release

#create a detached ascii signature of the Release file
gpg --armor --sign --detach-sign Release.gpg Release
```

Now you can upload the `aptrepo` directory to a webserver. If the repo
path is `http://example.com/foo/aptrepo`, then end users will have to
add this line to their  `/etc/apt/sources.list`:

```bash
deb http://example.com/foo/aptrepo binary/
```

Note that the `add-apt-repository` tool makes it easy for end users to
add repos to `sources.list`, but older versions of this tool contain a
bug ([now fixed](https://bugs.launchpad.net/ubuntu/+source/software-properties/+bug/987264))
that adds a `deb-src` line in addition to the `deb` line, which will
cause `apt-get update` to fail.


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
