#!/usr/bin/env python3
#coding: utf-8
#--------------------------------------
#    ___  ___  _ ____
#   / _ \/ _ \(_) __/__  __ __
#  / , _/ ___/ /\ \/ _ \/ // /
# /_/|_/_/  /_/___/ .__/\_, /
#                /_/   /___/
#
#  lcd_i2c.py
#  LCD test script using I2C backpack.
#  Supports 16x2 and 20x4 screens.
#
# Author : Matt Hawkins
# Date   : 20/09/2015
#
# http://www.raspberrypi-spy.co.uk/
#
# Copyright 2015 Matt Hawkins
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#--------------------------------------
import smbus
import time

# Define some device parameters
I2C_ADDR  = 0x3f # I2C device address
LCD_WIDTH = 20   # Maximum characters per line

# Define some device constants
LCD_CHR = 1 # Mode - Sending data
LCD_CMD = 0 # Mode - Sending command

## commands
LCD_CLEARDISPLAY   = 0x01
LCD_RETURNHOME     = 0x02
LCD_ENTRYMODESET   = 0x04
LCD_DISPLAYCONTROL = 0x08
LCD_CURSORSHIFT    = 0x10
LCD_FUNCTIONSET    = 0x20
LCD_SETCGRAMADDR   = 0x40
LCD_SETDDRAMADDR   = 0x80

#LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
#LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
#LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
#LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line
LCD_LINE_1 = 0x00 # LCD RAM address for the 1st line
LCD_LINE_2 = 0x40 # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x14 # LCD RAM address for the 3rd line
LCD_LINE_4 = 0x54 # LCD RAM address for the 4th line
LCD_LINE_N = (0x00,0x40,0x14,0x54)
LCD_BACKLIGHT  = 0x08  # On
#LCD_BACKLIGHT = 0x00  # Off

ENABLE = 0b00000100 # Enable bit

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

#Open I2C interface
bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
#bus = smbus.SMBus(1) # Rev 2 Pi uses 1

def lcd_init():
    # Initialise display
    lcd_byte(0x33,LCD_CMD) # 110011 Initialise
    lcd_byte(0x32,LCD_CMD) # 110010 Initialise
    lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
    lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off 
    lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
    lcd_byte(LCD_CLEARDISPLAY,LCD_CMD) # 000001 Clear display
    time.sleep(E_DELAY)

def lcd_byte(bits, mode):
    # Send byte to data pins
    # bits = the data
    # mode = 1 for data
    #        0 for command

    bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
    bits_low = mode | ((bits<<4) & 0xF0) | LCD_BACKLIGHT

    # High bits
    bus.write_byte(I2C_ADDR, bits_high)
    lcd_toggle_enable(bits_high)

    # Low bits
    bus.write_byte(I2C_ADDR, bits_low)
    lcd_toggle_enable(bits_low)

def lcd_toggle_enable(bits):
    # Toggle enable
    time.sleep(E_DELAY)
    bus.write_byte(I2C_ADDR, (bits | ENABLE))
    time.sleep(E_PULSE)
    bus.write_byte(I2C_ADDR,(bits & ~ENABLE))
    time.sleep(E_DELAY)

def printline(message,line):
    lcd_string(message,line)

def lcd_string(message,line):
    # Send string to display

    message = message.ljust(LCD_WIDTH," ")

    lcd_byte(LCD_SETDDRAMADDR|line, LCD_CMD)

    for i in range(LCD_WIDTH):
        lcd_byte(ord(message[i]),LCD_CHR)

def clear():
    lcd_byte(LCD_CLEARDISPLAY,LCD_CMD) # 000001 Clear display

def home():
    lcd_byte(LCD_RETURNHOME,LCD_CMD)

def setCursor(x,y):
    # set cursor
    if ( x >= LCD_WIDTH ):
        x = x % 20
    y = x + LCD_LINE_N[y]
    lcd_byte(LCD_SETDDRAMADDR|y, LCD_CMD)

def print(message):
    for i in range(len(message)):
        lcd_byte(ord(message[i]),LCD_CHR)

def lcd_clearBackLightOff():
    clearBackLightOff()

def clearBackLightOff():
    bits_high = LCD_CMD | (0x01 & 0xF0) 
    bits_low = LCD_CMD | ((0x01<<4) & 0xF0) 
    # High bits
    bus.write_byte(I2C_ADDR, bits_high)
    lcd_toggle_enable(bits_high)
    # Low bits
    bus.write_byte(I2C_ADDR, bits_low)
    lcd_toggle_enable(bits_low)


def main():
    # Main program block

    # Initialise display
    lcd_init()

    while True:

        # Send some test
        lcd_string("RPiSpy         <",LCD_LINE_1)
        lcd_string("I2C LCD        <",LCD_LINE_2)

        time.sleep(3)

        # Send some more text
        lcd_string(">         RPiSpy",LCD_LINE_1)
        lcd_string(">        I2C LCD",LCD_LINE_2)

        time.sleep(3)

if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        lcd_byte(0x01, LCD_CMD)
        lcd_clearBackLightOff()

