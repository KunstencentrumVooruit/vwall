#!/usr/bin/python

from pyA20.gpio import gpio
from pyA20.gpio import port
from pyA20.gpio import connector
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
	
    gpio.init() #Initialize module. Always called first
    gpio.setcfg(port.PG0, gpio.OUTPUT) #Configure LED1 as output
    

def setGpios(state):
	gpio.output(port.PG0, state)
	
def sigusr1(signum, frame):
    logging.info('USR1 received, gonna set pins HIGH.')
    setGpios(1)

def sigusr2(signum, frame):
    logging.info("USR2 received, gonna set pins LOW.")
    setGpios(0)

def exit_handler():
    print 'Cleaning up GPIO stuff..'
    gpio.close()

def main():
    setup()
    setup_gpio()
    logging.debug('Entering infinite loop.')
    while True:
        time.sleep(1)
    gpio.close()
if __name__ == "__main__":
    main()





