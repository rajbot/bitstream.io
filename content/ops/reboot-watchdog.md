Title:  Rebooting a linux node, even if shutdown hangs on a stuck device.
Author: raj
Tags:   linux, watchdog, softdog, ubuntu
Date:   2015-01-14


Sam showed me how to force a linux box to reboot, even if shutdown gets wedged on a stuck
device. In our case, we had a devicemanager device that had hung (which you could see by
running `iostat -xm 1`)

We use `softdog`, the nonhardware assisted watchdog driver to hard reset the
machine if needed. `softdog` will hard reset the machine if it doesn't receive
data every 60 seconds, so we open `/dev/watchdog` for write and then issue a
`shutdown -r`:

```bash
modprobe softdog
sudo bash -c "cat > /dev/watchdog" &
shutdown -r now
```

Thanks, Sam!
