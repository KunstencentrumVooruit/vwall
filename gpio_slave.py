#!/usr/bin/python
import logging
import atexit

from subprocess import Popen
from subprocess import call
import RPi.GPIO as GPIO

def setup():
	# Initiate logging
	logging.basicConfig(level=logging.DEBUG,
                    filename='/tmp/vwall_gpio.log',
                    format='%(asctime)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')
	logging.debug("------------------ COLD START ------------------")
	atexit.register(exit_handler)
 	logging.debug("setup completed!")

def exit_handler():
    print 'Cleaning up GPIO stuff..'
    GPIO.cleanup()

def setup_gpio():
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # pud_down niet vergeten, anders random low/high

def startListening():
	call(['pkill', '-STOP', '-f', 'viewer.py']) # send STOP signal to viewer.py / -f option om ook in volledige processstring te kijken, ipv alleen python (/home/pi/screenly/viewer.py) 
	call(['pkill', '-STOP', 'uzbl-core'])
	global p
	p  = Popen(['su', '-', 'pi', '-c pwomxplayer --config=4bez udp://239.0.1.23:1234?buffer_size=1200000B']) # something long running
	logging.info ("............ running pwomxplayer ............ ")
	
def stopListening():
	call(['pkill', '-CONT', '-f', 'viewer.py'])
	call(['pkill', '-CONT', 'uzbl-core']) 
	global p
	logging.info ("terminating pwomx")
	p.terminate()
	call (['pkill', 'pwomxplayer'])

def main():
    setup()
    setup_gpio()
    logging.debug('Entering infinite loop.')
    while True:
        GPIO.wait_for_edge(4, GPIO.RISING)
        startListening()
        logging.info ("Low->high detected")
        GPIO.wait_for_edge(4, GPIO.FALLING)
        stopListening()
        logging.info ("High->low detected!")
	


if __name__ == "__main__":
    main()

