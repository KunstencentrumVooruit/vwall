#!/bin/bash

if [ "$1" = "master" ]; then
	echo "Adding gpio_master to autostart (via Supervisord)"
	sudo ln -s ~/vwall/gpio_master.conf /etc/supervisor/conf.d/gpio_master.conf
	sudo /etc/init.d/supervisor stop > /dev/null
	sudo /etc/init.d/supervisor start > /dev/null

	echo "Installing avconv..."
	sudo apt-get install libav-tools
fi
