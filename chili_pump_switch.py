#!/usr/bin/python3.7
'''
This script controlling pump and valves based on switching the key
'''

import troykahat
import time
import logging
import argparse,sys
from time import sleep
from threading import Thread
from inputimeout import inputimeout, TimeoutOccurred

#Logger configuration
logger=logging.getLogger()
logger.setLevel(logging.INFO)
formatter=logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s')
#Logger to file
fh=logging.FileHandler('/home/pi/projects/results/logs/Chili_pump_switch.log')
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)
logger.addHandler(fh)
#Logger to console
ch=logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)

logger.info('Script started')

#format for --help
class CustomFormatter(argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter):
    pass

#Parsing in user input positional arguments
parser=argparse.ArgumentParser(description=sys.modules[__name__].__doc__, formatter_class=CustomFormatter)
parser.add_argument(dest='pin_valve', type=int, choices=[1,2,3,4,5,6], help='Digital pin where connected valve.')

try:
    args=parser.parse_args()
except AttributeError:
    logger.critical(f'Not enought attributes for work. Read --help')
    sys.exit(1)
    
pin_valve=args.pin_valve
logger.info(f'User input: valve pin = {pin_valve}')

#This is statement of pump and valve. Switch to false for disable.
work_signal=True
#Enable troykahat digital pins
wp = troykahat.wiringpi_io()

def activate_pump_switch(PIN_WP_MOSF):
    '''
    This module activate pump.
    '''
    
        #Digital pin for controlling pump. Its switched on via a mosfet N-type (normally disabled)
        
    wp.pinMode(PIN_WP_MOSF, wp.OUTPUT)                
    try:
        #Changing mosfet statement
        wp.digitalWrite(PIN_WP_MOSF, True) #set True for enable
        logger.info(f'Digital pin {PIN_WP_MOSF} enabled, pump activated')
        #pump will work till 'work_signal' in True statement
        while work_signal is True:
            sleep
    
    except Exception as e:
        logging.exception('Exception occured') 
    
    finally:
        #Changing mosfet statement
        wp.digitalWrite(PIN_WP_MOSF, False)
        logger.info(f'Digital pin {PIN_WP_MOSF} disabled, pump disabled')
    
def activate_valve_switch(PIN_WP_MOSF):
    '''
    This module open valve.
    '''

    #Digital pin for controlling pump. Its switched on via a mosfet N-type (normally disabled)
    wp.pinMode(PIN_WP_MOSF, wp.OUTPUT)
        
    try:
        #Changing mosfet statement
        wp.digitalWrite(PIN_WP_MOSF, True) #set True for enable
        logger.info(f'Digital pin {PIN_WP_MOSF} enabled, valve opened')
        #valve will work till 'work_signal' in True statement
        while work_signal is True:
            sleep
    
    except Exception as e:
        logging.exception('Exception occured')
    
    finally:
        #Changing mosfet statement
        wp.digitalWrite(PIN_WP_MOSF, False)
        logger.info(f'Digital pin {PIN_WP_MOSF} disabled, valve closed')

def user_signal():
    '''
    Function for disabling pump and valve
    '''
    global work_signal
    sleep (0.5)
    #Force stop script after delay
    MAX_TIME=60

    try:
        userinput=inputimeout('Print anything to disactivate pump\n',timeout=MAX_TIME)
        logger.info(f'User input: {userinput}')
        
        work_signal=False
        logger.info(f'Sent signal to stop from user')

    except TimeoutOccurred:
        work_signal=False
        logger.warning(f'Time expired: {MAX_TIME}sec. Script force stopped!')
  
def irrigation_switch(VALVE):
    '''
    Combines the operation of the pump and valves. Disable it when user input 'stop'
    '''
    try:   
        thread1=Thread(target=activate_valve_switch, args=(VALVE,))
        thread2=Thread(target=activate_pump_switch, args=(7,))
        thread3=Thread(target=user_signal)
        
        thread1.start()
        thread2.start()
        thread3.start()

        thread1.join()
        thread2.join()
        thread3.join()
    except (KeyboardInterrupt, SystemExit):        
        global work_signal
        work_signal=False
        logging.exception('Exception occured')
        logger.info('Script interrupted')
    finally:
        wp.digitalWrite(VALVE, False)
        wp.digitalWrite(7, False) 
def main():
    irrigation_switch(pin_valve)
    
if __name__=='__main__':
    main()

logger.info('Script finished')
