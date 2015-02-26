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
	
fi
if [ "$1" = "slave" ]; then

	echo "Installing pwlibs & pwomxplayer..."
	wget http://dl.piwall.co.uk/pwlibs1_1.1_armhf.deb
	wget http://dl.piwall.co.uk/pwomxplayer_20130815_armhf.deb
	sudo dpkg -i pwlibs1_1.1_armhf.deb
	sudo dpkg -i pwomxplayer_20130815_armhf.deb

	echo "Adding gpio_slave to autostart (via Supervisord)"
	sudo ln -s ~/vwall/gpio_slave.conf /etc/supervisor/conf.d/gpio_slave.conf
	sudo /etc/init.d/supervisor stop > /dev/null
	sudo /etc/init.d/supervisor start > /dev/null

fi
