# UART Control
#
# This example shows how to use the serial port on your OpenMV Cam. Attach pin
# P4 to the serial input of a serial LCD screen to see "Hello World!" printed
# on the serial LCD display.

import time
from pyb import UART,LED

# Always pass UART 3 for the UART number for your OpenMV Cam.
# The second argument is the UART baud rate. For a more advanced UART control
# example see the BLE-Shield driver.
uart = UART(3, 115200)

while(True):
    LED(1).on()
    LED(2).on()
    LED(3).on()
    uart.write("begin\r\n")
    time.sleep(1000)
    uart.write("close\r\n")
    time.sleep(1000)

