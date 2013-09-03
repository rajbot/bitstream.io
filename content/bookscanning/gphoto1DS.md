Title:  Adding gphoto support for the Canon 1DS
Author: shag
Date:   2008-08-09 16:23
Tags:   gphoto, canon, 1DS

Canon 1Ds HackiWiki!!

## 2007 Aug 20: Raj and I discovered some interesting stuff!!!




    606527  dest=WINDOZE, tl=0x39, read_block_request, src=CAMERA, offs=0x000004da60a8, data_length=0x0020, extended_tcode=0x0000, ack_pending

    606554  dest=CAMERA, tl=0x39, read_block_response, src=WINDOZE, complete, data_length=0x0020, extended_tcode=0x0000, data=[
     ffffffff ffffffff ffc30000 04bf2000
     8a98000e 28000000 000000ff 00000000

    ], ack_complete



  * bytes 0-3 are always(?) ffffffff
  * bytes 4-7 are always(?) ffffffff
  * bytes 8-11 are always ffc30000 -- Shag is willing to bet that this 0xffc3 is the Firewire bus address of 'WINDOZE' ...
    * A 16-bit firewire address is divided into two parts. The top 10 bits are the bus ID and the bottom 6 are the node ID. In the case of 0xffc3, the top ten bits are 1063 (base 10), which is a special value meaning 'local bus' ([reference](http://www.linux1394.org/doc/libraw1394/intro1394.html#AEN25))
  * bytes 12-15 [0x04bf2000] is the offset for the S/G list
  * byte 17 & mask 0x08: if true, then apparently means 'S/G list' - "counter packet" below byte 17 is 0x90
  * byte 19 (base 10) [0xe] above is the number of entries in the "S/G list" ...

----

    608909  dest=WINDOZE, tl=0x1c, read_block_request, src=CAMERA, offs=0x000004bf2000, data_length=0x0070, extended_tcode=0x0000, ack_pending

    608951  dest=CAMERA, tl=0x1c, read_block_response, src=WINDOZE, complete, data_length=0x0070, extended_tcode=0x0000, data=[
     0fb00000 0b23f050 10000000 0b48d000
     10000000 0afe7000 10000000 0b468000
     10000000 0b449000 20000000 0b4ba000
     10000000 0a3fc000 10000000 0a3dd000
     10000000 0a9de000 10000000 0b437000
     10000000 0b488000 10000000 0b461000
     20000000 0a3ea000 0f500000 0b48e000

    ], ack_complete



First two bytes are length of transfer; next two bytes apparently are ignored; next four bytes is
address on WINDOZE to transfer to.  After this the JPEG data starts.

----

These wacky packets (wackets?) are from a completely different part of the file.


    507816  dest=CAMERA, tl=0x39, read_block_response, src=WINDOZE, complete, data_length=0x0020, extended_tcode=0x0000, data=[
     ffffffff ffffffff ffc30000 172e6380
     8a90005c 28000000 00000000 5c000000

    ], ack_complete


Above we see that byte 17 & mask 0x08 is false.  So something is up.  Byte 19 [0x5c] happens to represent the number of bytes in the response packet.  Interesting...


    521267  dest=WINDOZE, tl=0x15, write_block_request, src=CAMERA, offs=0x0000172e6380, data_length=0x005c, extended_tcode=0x0000, data=[
     10000020 42000000 02000000 1d001022
     42000000 7ced2501 00000000 2e000100
     00010002 00030004 00050006 00070008
     0009000a 000b000c 000d000e 000f0010
     00110012 00130014 00150200 ff0100ff
     0200ff01 05ff0200 ff0106ff
    ], ack_complete


What's interesting is that the middle of the packet counts from 0x0001 to 0x0015 in 16-bit words.  Then after that there appear to be six 3-byte strings: 0x0200ff, 0x0100ff, 0x0200ff, 0x0105ff, 0x0106ff.

----

Okay I'm pretty interested in this 0x5c thing.  That is a magic number that I remember from the gphoto2 Canon USB driver.  0x5c is the number of bytes in a 'release params' data structure from the camera.  Release params are things like shutter speed, ISO, etc.  Let's look at the gphoto2 usb source and see if anything matches up.   I think this picture was captured at ISO 640... (looks at camlibs/canon source) ... let's see, for the EOS 5D, that would be a value of 0x5d, offset 0x1a bytes into the packet .... doh, doesn't match.  false alarm...  XXX Turns out this is because I'm looking in the wrong place!  See below!

----

Camera idle loop:

This sequence occurs every second under Windows.  0xffc3 is WINDOZE, 0xffc0 is CAMERA.


    363034  dest=0xffc0, tl=0x2a, write_quadlet_request, src=0xffc3, offs=0xfffff0010810, data=0x0000000f, ack_pending
    363064  dest=0xffc3, tl=0x2a, write_response, src=0xffc0, complete, ack_complete
    363090  dest=0xffc3, tl=0x38, read_block_request, src=0xffc0, offs=0x000004da60d0, data_length=0x0008, extended_tcode=0x0000, ack_pending
    363117  dest=0xffc0, tl=0x38, read_block_response, src=0xffc3, complete, data_length=0x0008, extended_tcode=0x0000, data=[
     00000000 04da60a8
    ], ack_complete
    363762  dest=0xffc3, tl=0x39, read_block_request, src=0xffc0, offs=0x000004da60a8, data_length=0x0020, extended_tcode=0x0000, ack_pending
    363788  dest=0xffc0, tl=0x39, read_block_response, src=0xffc3, complete, data_length=0x0020, extended_tcode=0x0000, data=[
     ffffffff ffffffff ffc30000 0cf5ed20
     8a900054 03000000 54000000 00000000

    ], ack_complete
    364702  dest=0xffc3, tl=0x16, write_block_request, src=0xffc0, offs=0x00000cf5ed20, data_length=0x0054, extended_tcode=0x0000, data=[
     70000900 00000058 00000000 80000000
     00000000 00000000 00000000 00000000
     00000000 00000000 00000000 00000000
     00000000 00000000 00000000 00000000
     00000000 00000000 00000000 00000000
     00000000
    ], ack_complete
    365127  dest=0xffc3, tl=0x0b, write_block_request, src=0xffc0, offs=0x000900000020, data_length=0x0008, extended_tcode=0x0000, data=[
     41000000 04da60a8
    ], ack_complete


----

**Aha! Byte diff for an F-stop setting change**


    325342  dest=0xffc0, tl=0x09, write_quadlet_request, src=0xffc3, offs=0xfffff0010810, data=0x0000000f, ack_pending
    325368  dest=0xffc3, tl=0x09, write_response, src=0xffc0, complete, ack_complete
    325393  dest=0xffc3, tl=0x38, read_block_request, src=0xffc0, offs=0x000004da60a8, data_length=0x0008, extended_tcode=0x0000, ack_pending
    325419  dest=0xffc0, tl=0x38, read_block_response, src=0xffc3, complete, data_length=0x0008, extended_tcode=0x0000, data=[
     00000000 04da60d0
    ], ack_complete
    325751  dest=0xffc3, tl=0x39, read_block_request, src=0xffc0, offs=0x000004da60d0, data_length=0x0020, extended_tcode=0x0000, ack_pending
    325780  dest=0xffc0, tl=0x39, read_block_response, src=0xffc3, complete, data_length=0x0020, extended_tcode=0x0000, data=[
     ffffffff ffffffff ffc30000 0775f480
     8a900054 28000000 00000000 54000000

    ], ack_complete
    343041  dest=0xffc3, tl=0x15, write_block_request, src=0xffc0, offs=0x00000775f480, data_length=0x0054, extended_tcode=0x0000, data=[
     10000020 4c000000 02000000 25001022
     4c000000 38e92501 00000000 0a000000
     30000000 20ff0100 0000ffff 04010000
     03020000 09030000 007f7f7f 70005800
     2d007800 0000ff00 20005800 64006400
     64000100
    ], ack_complete


Take a look at byte 64 [0x2d] in the above packet.  That was with one particular aperture setting -- not sure if it's 4.5 or 5.0.  Diffing this against traffic from changing the wheel back changed byte 64 to 0x2b.  Woo hoo!

----

One other thing from that last aperture wheel setting change.  How did the computer know that the camera settings had changed, and that it should query them?  Take a look at the write_block_request in the idle loop packets above.  Then check this out (scroll down to the write_block_request pkt):


    289212  dest=0xffc0, tl=0x05, write_quadlet_request, src=0xffc3, offs=0xfffff0010810, data=0x0000000f, ack_pending
    289242  dest=0xffc3, tl=0x05, write_response, src=0xffc0, complete, ack_complete
    289269  dest=0xffc3, tl=0x38, read_block_request, src=0xffc0, offs=0x000004da60a8, data_length=0x0008, extended_tcode=0x0000, ack_pending
    289296  dest=0xffc0, tl=0x38, read_block_response, src=0xffc3, complete, data_length=0x0008, extended_tcode=0x0000, data=[
     00000000 04da60d0
    ], ack_complete
    289881  dest=0xffc3, tl=0x39, read_block_request, src=0xffc0, offs=0x000004da60d0, data_length=0x0020, extended_tcode=0x0000, ack_pending
    289908  dest=0xffc0, tl=0x39, read_block_response, src=0xffc3, complete, data_length=0x0020, extended_tcode=0x0000, data=[
     ffffffff ffffffff ffc30000 0cf5ed20
     8a900054 03000000 54000000 00000000

    ], ack_complete
    290452  dest=0xffc3, tl=0x11, write_block_request, src=0xffc0, offs=0x00000cf5ed20, data_length=0x0054, extended_tcode=0x0000, data=[
     70000900 00000058 00000000 80000000
     00000000 02000000 0a000000 10000000
     1b000000 00000000 00000000 00845400
     f4ff9500 d17b4100 0f05ffff ffff0106
     ffffffff 0102ffff ffff0200 ff0100ff
     0200ff01
    ], ack_complete


See all that junk at the end?  I think that's how the computer knows to follow up queries.

----

Okay, just changed ISO and did the same thing as the aperture thing.  Changed ISO 250 to 320.  Byte 66 changed to 0x7b.  Changed back.  Byte 66 changed to 0x78.  Those two values match exactly with the shutter speed table in gphoto2 camlibs/canon.  Shutter speed offset is 0x1e, and aperture offset is 0x1c in the gphoto USB code; this seems to jive with those defines if we consider the 'start' of the release params payload to start at byte 36 of the packet.

It's interesting that the capture.log.txt that we took has 0xff for both of these parameters.  Perhaps that is because we took those shots in full-auto mode?

Anyway, it looks like the magic hex string to search for to find get-release-param commands is '8a900054 28'.

----

**libraw1394**

I'll bet this is what we'd need to use to start testing these commands out: <http://www.linux1394.org/doc/libraw1394/>

XXX On the other hand, if this device really just speaks SCSI, then we don't need libraw1394 at all..

----

## Arrrr!


![paul_and_raj_r0xx0rs](|filename|/images/paul_and_raj_r0xx0rs.jpg)

----





## 2007 Aug 24: SBP and SCSI and Wireshark oh my

**SCSI and SBP2**

So today Raj and shag had an interesting thought.  We noticed that when we plugged in the camera to our Linux box that [SBP-2](http://t10.org/ftp/t10/drafts/sbp2/sbp2r04.pdf) kicked in and the SCSI layer identified the camera and decided it was a scanner (at least in terms of SCSI).  This made us think, "Selves, what if we nosy'd the Linux->camera communication upon initial plugin and compared that the communication on the Windows side to see if that was using SBP-2 also?"  So we did.  And guess what?  We found a lot of similar packets!  So now we think that the Canon software is just sending down SCSI commands over SBP-2 over Firewire to get the camera to do things.

So then the question became, well, how do we snoop SCSI?  And it turns out that we could not find any SCSI snoopers that were not hardware based and therefore cost a gazillion dollars and probably did not have any Firewire ports on them anyway.  ... at least until we discovered that Wireshark nee Ethereal had an interesting thingamabob called packet-scsi.c written by some dude at Cicsoc who probably got paid to write that thing for iSCSI.  but maybe we can use that too!!! all wee need to do is to write something where Wireshark can load up nosy-dump files, then we need to write a dissector thingie for SBP-2 (since that does not appear to exist).  Then in the best of all possible worlds, packet-scsi would then magically parse all of the data.

yeah.

----

So we think we'll also probably have to write a basic Firewire -- really, a nosy-dump file format -- dissector.  The traces we've read look pretty simple so far in terms of commands - there aren't any isochronous transfers, all we should need are:

  * self id
  * bus reset
  * {read,write}_{quadlet,block}_{,response}

looks like we can pull the format right out of the nosy-dump.c source code, [krh's](http://bitplanet.net/) structs are really nicely formatted and this should be straightforward.

  * Wireshark Developer's Guide: [PDF](http://www.wireshark.org/download/docs/developer-guide-us.pdf)

----

So to write a new file format importer for Wireshark, one must modify this library that comes with it called Wiretap.  unfortunately the current format of nosy-dump files doesn't have any magic numbers that can be used to identify them, so probably the best thing to do is to prepend some magic number/string with an external tool, and modify nosy-dump to prepend these itself for future revs.





## 2007 Nov 1: nosy-dump file format

So the current rev of nosy-dump has a really simple file format: PASCAL strings (basically).  It writes exactly what nosy-dump receives from the kernel: an int, representing the number of bytes to follow, and then writes the bytes.

**Hack libpcap instead**

Probably the best thing to do is to hack FireWire sniffing support into libpcap.  libpcap already has Bluetooth and USB sniffing support in it...



## 2007 Late November: adding FireWire support to Wireshark

Shelved the libpcap idea for the time being.  Wrote a basic nosydump wiretap reader, and hacked up basic Firewire phy & link protocol dissectors to Wireshark.  Next step is to hack up something for SBP2.

![wireshark](|filename|/images/wireshark1.jpg)
