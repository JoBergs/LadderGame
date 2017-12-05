#!/usr/bin/python
import time
import math

import RPi.GPIO as GPIO


# catching crtl c has to be global

def millis():
    return int(round(time.time() * 1000))

	
class LadderGame(object):
    # GPIO wiring
    ledMap = [9, 10, 7, 8, 4, 25, 24, 23, 22, 27, 18, 17]
    BUTTON = 2

    # Some constants for our circuit simulation
    vBatt = 9.0  # Volts
    capacitor = 0.001  # 1000uF
    rCharge = 2200.0  # ohms
    rDischarge = 68000.0  # ohms
    timeInc = 0.01  # seconds

    vCharge = vCap = vCapLast = None
  
    def __init__(self):
        """ Program the GPIO correctly and initialise the lamps. """
	
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.ledMap,GPIO.OUT )
        GPIO.setup(self.BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
     
        # Calculate the actual charging voltage - standard calculation of
        #  self.vCharge = r2 / (r1 + r2) * self.vBatt
        #
        #   -----+--- self.vBatt
        #        |
        #        R1
        #        |
        #        +---+---- self.vCharge
        #        |   |
        #        R2  C
        #        |   |
        #   -----+---+-----
    
        self.vCharge = self.rDischarge / (self.rCharge + self.rDischarge) * self.vBatt
        self.vCap = self.vCapLast = 0.0

        self.display_info()
        self.introLeds()
        self.play()
	
    def flash_three_times(self):
        """ Flash 3 times. """
        for j in range(3):
            for i in self.ledMap:
                GPIO.output(i, True)
                time.sleep(0.3)
            for i in self.ledMap:
                GPIO.output(i, False)
                time.sleep(0.1)
		
    def chargeCapacitor(self):
        ''' Add charge to the self.capacitor. Standard self.capacitor formulae. '''

        self.vCap = (self.vCapLast - self.vCharge) * math.e ** (-self.timeInc / (self.rCharge * self.capacitor)) + self.vCharge
        self.vCapLast = self.vCap
        # print "+vCap: {0}".format(self.vCap)  # debugging

    def dischargeCapacitor(self):
        ''' Remove charge from the self.capacitor. Standard self.capacitor formulae. '''
        self.vCap = self.vCapLast * math.e ** (-self.timeInc / (self.rDischarge * self.capacitor))
        self.vCapLast = self.vCap 
        # print "-vCap: {0}".format(self.vCap)  # debugging

    def winningLeds(self):
        """  Put a little pattern on the LEDs to start with. """

        self.flash_three_times()
    
        GPIO.output(self.ledMap, True)
        time.sleep(0.5)
    
        # Count Up...
        for i in self.ledMap:
            GPIO.output(i, True)
            time.sleep(0.1)
        time.sleep(0.5)

    def ledBargraph(self, value, topLedOn):
        """  Output the supplied number as a bargraph on the LEDs. """

        topLed = int(round(value / self.vCharge * 12.0)) + 1
  
        if topLed > 12:
            topLed = 12
    
        if not topLedOn:
            topLed -= 1
	
        for i in range(topLed):
            GPIO.output(self.ledMap[i], True)
    
        for i in range(12-topLed):   	
            GPIO.output(self.ledMap[i+topLed], False)
   
    def ledOnAction(self):
        """  Make sure the leading LED is on and check the button. """

        if GPIO.input(self.BUTTON) == 0:
            self.chargeCapacitor()
            self.ledBargraph(self.vCap, True)
	
    def ledOffAction(self):
        """  Make sure the leading LED is off and check the button. """
	
        self.dischargeCapacitor()
    
        # Are we still pushing the button?
        if GPIO.input(self.BUTTON) == 0:
            self.vCap = self.vCapLast = 0.0
            self.ledBargraph(self.vCap, False)
	
        # Wait until we release the button
        while GPIO.input(self.BUTTON) == 0:
            time.sleep(0.01)
	   
    
    def display_info(self):
        print "Pi Ladder\n"
        print "=========\n\n"
        print "       vBatt: {0} volts\n".format(self.vBatt)
        print "     rCharge: {0} ohms\n".format(self.rCharge)
        print "  rDischarge: {0} ohms\n".format(self.rDischarge)
        print "     vCharge: {0} volts\n".format(self.vCharge)
        print "   capacitor: {0} uF\n".format(self.capacitor * 1000.0)
    
    def introLeds(self):
        """ Put a little pattern on the LEDs to start with. """

        self.flash_three_times()
	
        GPIO.output(self.ledMap, True)  # All On
        time.sleep(0.5)

        # Countdown...
        for i in reversed(self.ledMap):
            GPIO.output(i, False)
            time.sleep(0.1)
        time.sleep(0.5)
    
    def play(self):
        ourDelay = self.timeInc
        # Setup the LED times - TODO reduce the ON time as the game progresses
        ledOnTime = ledOffTime = 1000
  
        # This is our Gate/Squarewave loop
        try:
            while True:
		
                self.ledBargraph(self.vCap, True) # LED ON
                then = millis() + ledOnTime
	
                while millis() < then:
                    self.ledOnAction()
                    time.sleep(ourDelay)
	    
                # Have we won yet?
                #  We need self.vCap to be in the top 12th of the self.vCharge	
                if self.vCap > (11.0 / 12.0 * self.vCharge):  # yeehaw!
                    self.winningLeds()
                    while GPIO.input(self.BUTTON) == 1:
                        time.sleep(0.01)
                    while GPIO.input(self.BUTTON) == 0:
                        time.sleep(0.01)
                    self.vCap = self.vCapLast = 0.0
	    
                # LED OFF:
                self.ledBargraph(self.vCap, False)
                then = millis() + ledOffTime
                while millis() < then:
                    self.ledOffAction()		    
                    time.sleep(ourDelay)
        except:
           GPIO.cleanup()

if __name__ == "__main__":
    LadderGame()