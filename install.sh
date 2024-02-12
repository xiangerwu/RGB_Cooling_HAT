#!/bin/sh

sudo echo 'hdmi_force_hotplug=1' >> /boot/config.txt

cd /home/Akita/.config/
mkdir /home/Akita/.config/autostart
cd /home/Akita/.config/autostart
cp /home/Akita/RGB_Cooling_HAT/start.desktop /home/Akita/.config/autostart/
echo 'install ok!'
