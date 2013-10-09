# hijuno.py
#
# 9 Oct 2013
# Jason Milldrum, NT7S
#
# A simple control program for the Hi Juno event on 9 Oct 2013
# http://missionjuno.swri.edu/hijuno/
# 
# A transmitter is keyed via a simple interface on a serial port RTS line.
# Change the values DEVICE, BAUD, and CALLSIGN to customize for yourself.
#
# On a *nix system, you may need to execute under sudo to have proper access
# to the serial port

import serial
import datetime
import time
import sys

DEVICE = '/dev/ttyUSB0'
BAUD = 57600
START_TIME = "1800 9 Oct 2013"
END_TIME = "2040 9 Oct 2013"
KEYDOWN_PERIOD = 30
KEYDOWN = False
CALLSIGN = "N0CALL"
ID_WPM = 25
KEYDOWN_SLOTS = {0, 1, 2, 3, 5, 6}

# The MORSECHAR list maps to the standard ASCII table starting at ASCII 32 (SPACE).
#
# A dit is represented by a "0" bit, while a dah is represented by a "1" bit.
#
# Characters are encoded with the most significant "bit" first so that the byte can be left-shifted
# to read out each element. Each character must be terminated in a "1" so that the reading algorithm
# knows to end when the byte == 0b10000000.
MORSE_CHAR_START = 32
MORSECHAR = [0b11111111,		# Special code for SPACE
             0b10000000,		# Not implemented
             0b10000000,		# Not implemented
             0b10000000,		# Not implemented
             0b10000000,		# Not implemented
             0b10000000,		# Not implemented
             0b10000000,		# Not implemented
             0b10000000,		# Not implemented
             0b10000000,		# Not implemented
             0b10000000,		# Not implemented
             0b10000000,		# Not implemented
             0b10000000,		# Not implemented
             0b10000000,		# Not implemented
             0b11100000,		# Minus sign (indicated by "M" in this implementation)
             0b10000000,		# Not implemented
             0b10010100,		# "/" Slash
             0b11111100,		# "0"
             0b01111100,		# "1"
             0b00111100,		# "2"
             0b00011100,		# "3"
             0b00001100,		# "4"
             0b00000100,		# "5"
             0b10000100,		# "6"
             0b11000100,		# "7"
             0b11100100,		# "8"
             0b11110100,		# "9"
             0b10000000,		# Not implemented
             0b10000000,		# Not implemented
             0b10000000,		# Not implemented
             0b10001100,		# "=" BT prosign/Equal sign
             0b10000000,		# Not implemented
             0b00110010,		# "?" Question mark
             0b10000000,		# Not implemented
             0b01100000,		# "A"
             0b10001000,		# "B"
             0b10101000,		# "C"
             0b10010000,		# "D"
             0b01000000,		# "E"
             0b00101000,		# "F"
             0b11010000,		# "G"
             0b00001000,		# "H"
             0b00100000,		# "I"
             0b01111000,		# "J"
             0b10110000,		# "K"
             0b01001000,		# "L"
             0b11100000,		# "M"
             0b10100000,		# "N"
             0b11110000,		# "O"
             0b01101000,		# "P"
             0b11011000,		# "Q"
             0b01010000,		# "R"
             0b00010000,		# "S"
             0b11000000,		# "T"
             0b00110000,		# "U"
             0b00011000,		# "V"
             0b01110000,		# "W"
             0b10011000,		# "X"
             0b10111000,		# "Y"
             0b11001000]		# "Z"

def id(call):
	# Parse each figure in the callsign
	for ch in call:
		# Get the representation of each character and parse dits and dahs
		morse = MORSECHAR[ord(ch) - MORSE_CHAR_START]
		if(morse == 0b11111111):
			# If a SPACE, delay for a word space (7 dit length)
			time.sleep(ditlength(ID_WPM) * 7)
		else:
			while(morse != 0b10000000):
				# If MSB is a 1, send a dah
				if(morse & 0b10000000 == 0b10000000):
					ser.setRTS(True)
					time.sleep(ditlength(ID_WPM) * 3)
					ser.setRTS(False)
				# Otherwise send a dit
				else:
					ser.setRTS(True)
					time.sleep(ditlength(ID_WPM))
					ser.setRTS(False)
				# Now rotate the last element out of the character
				morse = (morse & 0b01111111) << 1
				# And wait for a dit
				time.sleep(ditlength(ID_WPM))
			# Wait for a dah in between characters
			time.sleep(ditlength(ID_WPM) * 3)
	return

def ditlength(wpm):
	return 1.2 / wpm

# Open serial port
try:
	ser = serial.Serial(DEVICE, BAUD)
except:
	print 'Cannot open serial port'
	sys.exit(0)

# Main processing loop
while 1:
	# Set the RTS line to key the transmitter as appropriate
	ser.setRTS(KEYDOWN)
	# Check to see if we are in the transmitting window
	if(datetime.datetime.utcnow() > datetime.datetime.strptime(START_TIME, "%H%M %d %b %Y") and datetime.datetime.utcnow() < datetime.datetime.strptime(END_TIME, "%H%M %d %b %Y")):
		# Check to see if we are in one of the transmit slots
		if(datetime.datetime.utcnow().minute % 10 in KEYDOWN_SLOTS):
			# Check to see if we are in the keydown period
			if(datetime.datetime.utcnow().second >= 0 and datetime.datetime.utcnow().second < KEYDOWN_PERIOD):
				# TX on
				if(KEYDOWN == False):
					print 'TX On - %s' % datetime.datetime.utcnow().strftime("%H:%M:%S")
					# ID for FCC regulations
					id(CALLSIGN)
				KEYDOWN = True
			else:
				# TX off
				if(KEYDOWN == True):
					print 'TX Off - %s' % datetime.datetime.utcnow().strftime("%H:%M:%S")
				KEYDOWN = False
	time.sleep(0.1)
