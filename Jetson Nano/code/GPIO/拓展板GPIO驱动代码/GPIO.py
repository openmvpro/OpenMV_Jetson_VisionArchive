import RPi.GPIO as GPIO
import time
#舵机部分
from adafruit_servokit import ServoKit

def LED(
                    LED_blue    = GPIO.HIGH,
                    LED_red      = GPIO.HIGH,
                    LED_green = GPIO.HIGH,
                    STATE           = 1                         #0为翻转，1为常亮，
                ):

    GPIO.setmode(GPIO.BCM)  
    GPIO.setup(17, GPIO.OUT, initial=LED_blue)
    GPIO.setup(18, GPIO.OUT, initial=LED_red)
    GPIO.setup(27, GPIO.OUT, initial=LED_green)

    curr_value_blue    = GPIO.HIGH
    curr_value_red      = GPIO.HIGH
    curr_value_green = GPIO.HIGH

    if STATE == 0:
        while(True):
            time.sleep(1)
            if LED_blue == GPIO.LOW:GPIO.output(17, curr_value_blue)
            if LED_red   == GPIO.LOW:GPIO.output(18, curr_value_red)
            if LED_green   == GPIO.LOW:GPIO.output(27, curr_value_green)
            curr_value_blue ^= GPIO.HIGH#反转
            curr_value_red ^= GPIO.HIGH
            curr_value_green ^= GPIO.HIGH
    else:
        while(True):
            if LED_blue == GPIO.LOW:GPIO.output(17, GPIO.LOW)
            if LED_red   == GPIO.LOW:GPIO.output(18, GPIO.LOW)
            if LED_green   == GPIO.LOW:GPIO.output(27, GPIO.LOW)

def BEEP(STATE=0):
    beep_pin=6
    GPIO.setmode(GPIO.BCM)  
    GPIO.setup(beep_pin, GPIO.OUT, initial=GPIO.HIGH)

    beep_value = GPIO.HIGH
    if STATE == 0:
        while(True):
            time.sleep(1)
            GPIO.output(beep_pin, beep_value)
            beep_value ^= GPIO.HIGH#反转
    else:
        while(True):GPIO.output(beep_pin, GPIO.HIGH)

def KEY(key=1):
    GPIO.setmode(GPIO.BCM)
    while True:
        #读取按键一
        key_1=26
        GPIO.setup(key_1, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(key_1, GPIO.IN)
        KEY_1_value = GPIO.input(key_1)
        #读取按键二
        key_2=19
        GPIO.setup(key_2, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(key_2, GPIO.IN)
        KEY_2_value = GPIO.input(key_2)

        if key == 0:
            return KEY_1_value , KEY_2_value
        if key == 1:
            return KEY_1_value 
        else:
            return KEY_2_value 
    
def Servos():
    #选择通道
    kit=ServoKit(channels=16)
    #复位
    kit.servo[0].angle=90
    kit.servo[1].angle=90
    #测试
    i=0
    a=0
    while(True):
        if i  == 180 :a=1
        if i  ==  0:     a=0
        if a == 1:      i = i-1
        if a == 0:      i = i+1
        print(i)
        kit.servo[0].angle=i
        kit.servo[1].angle=i

'''
    Name      BOARD     BCM        功能
    LED_1      11              17            蓝色(低电平亮)    
    LED_2      12              18            红色(低电平亮)   
    LED_3      13              27            绿色(低电平亮)   
    BEEP        31               6              响B (高电平响)
    KEY_1      37              26             按键一(按下置低)
    KEY_2      35              19             按键二(按下置低)
'''
    
def main():
    while(True):
        #LED(LED_red=GPIO.LOW,LED_blue=GPIO.LOW,STATE=0)#LED灯为低电平有效，STATE是0时翻转，1时常亮,   可实现RGB 颜色组合，色调自查
        #BEEP(STATE=0)#高电平有效，STATE是0时翻转，1时常响,
        KEY(key=0)#key为0时接收两按键返回值，1为按键一返回值，2为按键二返回值
        #Servos()#仅驱动测试

