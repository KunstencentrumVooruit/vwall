#!/usr/bin/python

import RPi.GPIO as GPIO
import atexit
import time
from subprocess import call
import logging
from signal import signal, SIGUSR1, SIGUSR2

def setup():
	# Initiate logging
	logging.basicConfig(level=logging.DEBUG,
                    filename='/tmp/vwall_gpio.log',
                    format='%(asctime)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')
	logging.debug("------------------ COLD START ------------------")
	signal(SIGUSR1, sigusr1) # register signal USR1
	signal(SIGUSR2, sigusr2) # register signal USR2
	atexit.register(exit_handler)
 	logging.debug("setup completed!")

def setup_gpio():
	#set up GPIO using BCM numbering
	GPIO.setmode(GPIO.BCM)
	# setup gpio4 & 17 als output
	GPIO.setup(4, GPIO.OUT)
	GPIO.setup(17, GPIO.OUT)

def setGpios(state):
	GPIO.output(4, state)
	GPIO.output(17, state)

def sigusr1(signum, frame):
    logging.info('USR1 received, gonna set pins HIGH.')
    setGpios(True)

def sigusr2(signum, frame):
    logging.info("USR2 received, gonna set pins LOW.")
    setGpios(False)

def exit_handler():
    print 'Cleaning up GPIO stuff..'
    GPIO.cleanup()

def main():
    setup()
    setup_gpio()
    logging.debug('Entering infinite loop.')
    while True:
        time.sleep(1)
    GPIO.cleanup()
if __name__ == "__main__":
    main()





