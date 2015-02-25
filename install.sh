#!/bin/bash

echo "Installing Screenly..."
cd /home/pi
#curl -sL https://raw.github.com/wireload/screenly-ose/master/misc/install.sh | bash

cd /home/pi/vwall

if [ "$1" = "master" ]; then
	echo "Adding gpio_master to autostart (via Supervisord)"
	sudo ln -s ~/vwall/gpio_master.conf /etc/supervisor/conf.d/gpio_master.conf
	sudo /etc/init.d/supervisor stop > /dev/null
	sudo /etc/init.d/supervisor start > /dev/null

	echo "Installing avconv..."
	#sudo apt-get install libav-tools
	
	echo "Replacing viewer.py with custom viewer..."
	cp viewer_master.py /home/pi/screenly/viewer.py
	echo "Killing viewer.py"
	pkill -f "viewer.py" # xloader zorgt voor auto restart viewer.py	
	
fi
