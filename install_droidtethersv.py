#!/usr/bin/env python2
"""

Python Script "droidtethersv" to install and use the Droid as a tethered modem

Created by Shannon VanWagner <shannon.vanwagner@linux.com> on 05-07-10, modified 05-17-10

Checkout my blog at http://humans-enabled.com for more information Yes this is
my La Bamba for Python Updated 06-03-10 (added additional device id from lsusb
for HTC phones), and added untested functionality for this script to work with
yum instead of apt-get Updated 06-24-10, changed restart commands to init.d
path style restarts. Added functionality to backup the /etc/resolv.conf as
/etc/resolv.conf.preDroidTetherSV Updated 09-18-10 with newer adb

---

 Modified heavily by jamesob, May 13 2011

 This package now assumes
   i. The user is running under Arch Linux, and
   ii. The user has packages `android-sdk` and `android-sdk-platform-tools`
       installed from the AUR.

 Good luck.
"""

import os, sys, commands

"""
You modify this.
"""
INSTALL_DIR = '/home/job/tmp/DroidTetherSV'

"""
You maybe modify this.
"""
ADB_LOCATION = '/opt/android-sdk/platform-tools/adb'

def shell(*args):
    for a in args:
        os.system(a)

user = os.getlogin()
installdir = os.path.expanduser(INSTALL_DIR)
scriptdir = sys.path[0]

if os.geteuid() != 0:
    print "Not running with root privileges."
    sys.exit(1)
    pass

#Check for and remove an obsolete working dir
if os.path.exists(installdir):
    os.system('rm -rf %s' % installdir)

#Create a dir in the user home dir to contain the run script
os.system('mkdir %s' % installdir)

#Backup the /etc/resolv.conf file... this is the one and only time this will happen (meaning it won't be backed up when the connection script is used)
os.system('cp /etc/resolv.conf /etc/resolv.conf.preDroidTetherSV')

#Create a udev rule to allow connection to the Droid
shell('touch /etc/udev/rules.d/91-android.rules',
'echo SUBSYSTEM==\'"usb"\', ATTRS{idVendor}==\'"22b8"\',SYMLINK+=\'"android_adb"\', MODE=\'"0666"\', OWNER=\'"%s"\' >/etc/udev/rules.d/91-android.rules' % user,
'echo SUBSYSTEM==\'"usb"\', ATTRS{idVendor}==\'"0bb4"\',SYMLINK+=\'"android_adb"\', MODE=\'"0666"\', OWNER=\'"%s"\' >>/etc/udev/rules.d/91-android.rules' % user,
'echo SUBSYSTEM==\'"usb"\', ATTRS{idVendor}==\'"04e8"\',SYMLINK+=\'"android_adb"\', MODE=\'"0666"\', OWNER=\'"%s"\' >>/etc/udev/rules.d/91-android.rules' % user,
'chmod a+r /etc/udev/rules.d/91-android.rules',
#Restart the udev daemon to ensure the device is recognized
'udevadm control --reload-rules')

#1.) Enable "USB debugging" on your Verizon Droid via Settings>Applications>Development
#2.) Connect your Droid to the computer with the USB cable and then use the following adb command to check for your device.
#adb devices
#example for checking to see if your Droid is connected: adb devices

#This will check to see if the Droid is connected and exit the script if not.
shell('%s start-server' % ADB_LOCATION)

var = commands.getstatusoutput('%s get-serialno' % ADB_LOCATION)
if "unknown" in var:
    print "Droid not connected. Enable USB Debug and connect to computer."
    sys.exit(1)
    pass

# Homepage for azilink 2.0.2, has android barcode 
shell('cp %s/azilink-2.0.2.apk %s' % (scriptdir,installdir),
      '%s install -r %s/azilink-2.0.2.apk' % (ADB_LOCATION, installdir),
      # Leave this one commented because we build the azilink.ovpn instead
      'touch %s/azilink.ovpn'% installdir,
      'echo dev tun    > %s/azilink.ovpn'% installdir,
      'echo remote 127.0.0.1 41927 tcp-client >> %s/azilink.ovpn'% installdir,
      'echo proto tcp-client >> %s/azilink.ovpn'% installdir,
      'echo ifconfig 192.168.56.2 192.168.56.1 >> %s/azilink.ovpn'% installdir,
      'echo route 0.0.0.0 128.0.0.0 >> %s/azilink.ovpn'% installdir,
      'echo route 128.0.0.0 128.0.0.0 >> %s/azilink.ovpn'% installdir,
      'echo socket-flags TCP_NODELAY >> %s/azilink.ovpn'% installdir,
      'echo \#keepalive 10 30 >> %s/azilink.ovpn'% installdir,
      'echo ping 10 >> %s/azilink.ovpn'% installdir,
      'echo dhcp-option DNS 192.168.56.1 >> %s/azilink.ovpn'% installdir,
      'cp %s/azilink.ovpn /usr/bin/DroidTetherSV' % installdir)

#11.) Create a replacement resolv.conf file to be copied over to your /etc directory at run-time:
shell('touch %s/resolv.conf'% installdir,
      'echo domain lan > %s/resolv.conf'% installdir,
      'echo search lan >> %s/resolv.conf'% installdir,
      'echo nameserver 192.168.56.1 >> %s/resolv.conf'% installdir)

#12.) Now create a very small script to start the modem
shell('touch %s/droidtethersv'% installdir,
      'echo sudo killall adb openvpn > %s/droidtethersv'% installdir,
      'echo sudo adb forward tcp:41927 tcp:41927 >> %s/droidtethersv'% installdir,
      'echo sudo cp %s/resolv.conf /etc/ >> %s/droidtethersv'% (installdir,installdir),
      'echo sudo openvpn --config %s/azilink.ovpn >> %s/droidtethersv'% (installdir,installdir),
      'chmod a+x %s/droidtethersv'% installdir)

#Set user ownership of everything
shell('chown %s -R %s' % (user,installdir))

#Do some resets to ensure process can work (arch)
shell('/etc/rc.d/network restart')


print """Voila! - Now you can start using your Android to connect to the Internet. 

  1.)Simply enable the azilink service on your Android
  2.)Run the script installed in %s.
  
  Got Feedback? Leave a comment at
  http://tinyurl.com/tetherdroid
  
  Congratulations on your Freedom!
  Shannon VanWagner - humans-enabled.com
  
  Congratulations on running this batshit script,
  jamesob""" % INSTALL_DIR

