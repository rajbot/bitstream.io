Title:  Adding gphoto support for the Canon 5D
Author: raj
Date:   2008-08-09 16:23
Tags:   gphoto, canon, 5D

### gphoto for Canon EOS 5D compilation instructions
#### you MUST use svn rev 10595 or greater. We tested with 10597

Building gphoto on Ubuntu 6.10 (note that default 2.6.17 kernel spinlocks, use custom kernel)


    :::bash
    #check out trunk. The checkout will fail when trying to pull the libusb directory
    svn co https://gphoto.svn.sourceforge.net/svnroot/gphoto/trunk gphoto
    cd gphoto
    #fix broken checkout:
    svn up bindings/ gphoto2/ gphoto2-manual/ gphotofs/ gphoto-import/ gphoto-suite/ gtkam/ libgphoto2/ m4/ playground/ project-3/ website/

    #build libgphoto2
    cd libgphoto2
    autoreconf -is
    ./configure --with-camlibs=canon --prefix=/scribe
    make
    sudo make install

    #build gphoto2
    cd ../gphoto2
    autoreconf -is
    ./configure --with-libgphoto2=/scribe --prefix=/scribe
    make
    sudo make install


### linux kernel issues
The kernel used by default in Ubuntu 7.04 (feisty) contains usb autosuspend code. Unfortunately, the Canon EOS 5D does not wake back up properly, which makes capturing images impossible. [[http://lkml.org/lkml/2007/8/16/330|A patch has been submitted]], but until it is accepted, you will have to compile a kernel with USB autosuspend turned off. **Update**: patch [[http://sourceforge.net/mailarchive/message.php?msg_id=20070822220805.GB30603%40kroah.com|accepted]], should be in 2.6.23 kernel. Instructions on how we compiled the kernel are below.

The kernel used by default in Ubuntu 6.10 (edgy) contains a bug that causes a spinlock in the jbd layer. This bug will cause a machine to hang in a completely unresponsive state, although you can use a serial console to see assertions firing in jbd. One workaround is to use a newer version of Ubuntu (7.04) with autosuspend turned off. Another is to use ext2 intead of ext3.

#### Compiling a custom linux kernel

We copied the .config file for the 2.6.17 kernel used by Ubuntu and slightly modified it to turn off usb autosuspend and include the nvidia sata driver.

    :::bash
    # Install kernel build pre-reqs
    sudo apt-get install linux-kernel-devel initrd-tools libncurses-dev

    cd ~
    mkdir linux
    cd linux

    # Download stable kernel tree from www.kernel.org ('F' link)
    wget http://www.kernel.org/pub/linux/kernel/v2.6/linux-2.6.22.2.tar.bz2

    tar xjvf linux-2.6.22.2.tar.bz2

    cd linux-2.6.22.2

    # Copy the Ubuntu kernel .config file into your source tree:
    cp /usr/src/linux-headers-2.6.17-12-generic/.config .

    # Update the .config with any new entries between 2.6.17 and the current kernel
    rev
    # (You just want to wail on the ENTER key here to select all of the defaults)
    yes '' | make oldconfig

    # Edit the .config to disable CONFIG_USB_SUSPEND
    perl -p -i.orig -e 's/CONFIG_USB_SUSPEND=y/CONFIG_USB_SUSPEND=n/' .config

    # Enable the Nvidia SATA driver
    echo CONFIG_ATA=m >> .config
    echo CONFIG_ATA_ACPI=y >> .config
    echo CONFIG_SATA_NV=m >> .config

    # Build kernel (dual-cpu system)
    make -j3 all

    # Install modules & kernel
    sudo make install modules_install

    # Build the boot-time ramdisk of loadable modules, etc.
    sudo mkinitrd -o /boot/initrd.img-2.6.22.2 2.6.22.2

    # Add grub boot section
    echo 'Now edit /boot/grub/menu.lst to add a section for the new kernel'


#### Install custom linux kernel and new nvidia drivers
On homeserver:

    :::bash
    cd ~pjw
    sudo ssh root@host 'cd /;tar -xjvf -' < new-kernel.tar.bz2
    sudo ssh root@host 'cd /home/scribe;tar -xzvf -' < new-kernel-source.tar.gz
    scp NVIDIA-Linux-x86-100.14.11-pkg1.run scribe@host:


Now on the scribe node:

    :::bash
    sudo /etc/init.d/gdm stop
    sudo sh NVIDIA-Linux-x86-100.14.11-pkg1.run
