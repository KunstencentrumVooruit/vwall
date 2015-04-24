#!/bin/bash

echo "Installing Screenly..."
cd /home/pi
#curl -sL https://raw.github.com/wireload/screenly-ose/master/misc/install.sh | bash

cd /home/pi/vwall

if [ "$1" = "master" ]; then
	echo "Adding gpio_master to autostart (via Supervisord)"
	sudo ln -s ~/vwall/gpio_master.conf /etc/supervisor/conf.d/gpio_master.conf
	echo "Adding viewer_master to autostart (via Supervisord)"
	sudo ln -s ~/vwall/viewer_master.conf /etc/supervisor/conf.d/viewer_master.conf
	sudo /etc/init.d/supervisor stop > /dev/null
	sudo /etc/init.d/supervisor start > /dev/null

	echo "Installing avconv..."
	#sudo apt-get install libav-tools
	
	echo "Replacing viewer.py with custom viewer..."
	cp viewer_master.py /home/pi/screenly/viewer.py
	echo "Killing viewer.py"
	pkill -f "viewer.py" # xloader zorgt voor auto restart viewer.py

	echo "Auto setting hostname"
	CURRENT_HOSTNAME=`cat /etc/hostname | tr -d " \t\n\r"`
	NEW_HOSTNAME="vwallMASTER"
	echo $NEW_HOSTNAME
	sudo sh -c "echo $NEW_HOSTNAME > /etc/hostname"
	sudo sed -i "s/127.0.1.1.*$CURRENT_HOSTNAME/127.0.1.1\t$NEW_HOSTNAME/g" /etc/hosts
	
fi
if [ "$1" = "slave" ]; then

	echo "Installing pwlibs & pwomxplayer..."
	#wget http://dl.piwall.co.uk/pwlibs1_1.1_armhf.deb
	#wget http://dl.piwall.co.uk/pwomxplayer_20130815_armhf.deb
	#sudo dpkg -i pwlibs1_1.1_armhf.deb
	#sudo dpkg -i pwomxplayer_20130815_armhf.deb

	echo "Adding gpio_slave to autostart (via Supervisord)"
	#sudo ln -s ~/vwall/gpio_slave.conf /etc/supervisor/conf.d/gpio_slave.conf
	#sudo /etc/init.d/supervisor stop > /dev/null
	#sudo /etc/init.d/supervisor start > /dev/null

	echo "Auto setting hostname"
	CURRENT_HOSTNAME=`cat /etc/hostname | tr -d " \t\n\r"`
	STAM="vwallSLAVE"
	NEW_HOSTNAME=$STAM$2
	echo $NEW_HOSTNAME
	sudo sh -c "echo $NEW_HOSTNAME > /etc/hostname"
	sudo sed -i "s/127.0.1.1.*$CURRENT_HOSTNAME/127.0.1.1\t$NEW_HOSTNAME/g" /etc/hosts

fi

echo "Auto setting network"
        sudo sh -c "echo auto lo > /etc/network/interfaces"
        sudo sh -c "echo iface lo inet loopback >> /etc/network/interfaces"
        sudo sh -c "echo iface eth0 inet static >> /etc/network/interfaces"
        sudo sh -c "echo address 192.168.0.$2 >> /etc/network/interfaces"
        sudo sh -c "echo netmask 255.255.255.0 >> /etc/network/interfaces"
        sudo sh -c "echo up route add -net 224.0.0.0 netmask 240.0.0.0 eth0 >> /etc/network/interfaces"
        sudo sh -c "echo >> /etc/network/interfaces"    
        sudo sh -c "echo allow-hotplug wlan0 >> /etc/network/interfaces"
        sudo sh -c "echo auto wlan0 >> /etc/network/interfaces"
        sudo sh -c "echo iface wlan0 inet dhcp >> /etc/network/interfaces"
        sudo sh -c "echo wpa-ssid "ifoon" >> /etc/network/interfaces"
        sudo sh -c "echo wpa-psk "xxxxxxxxxx" >> /etc/network/interfaces"
        sudo sh -c "echo >> /etc/network/interfaces"
        sudo sh -c "echo iface default inet dhcp >> /etc/network/interfaces"

echo "Adding crontab entries...."
	add_to_crontab
