import RPi.GPIO as GPIO
import time

output_pin = 26
'''
Name      BOARD     BCM        功能
LED_1      33              13            白色(低电平亮)    
LED_2      35              19            蓝色(低电平亮)   
LED_3      37              26            红色(低电平亮)   
BEEP        31               6              响B (高电平响)
'''

def main():
    GPIO.setmode(GPIO.BCM)  
    GPIO.setup(output_pin, GPIO.OUT, initial=GPIO.HIGH)

    print("Starting demo now! Press CTRL+C to exit")
    curr_value = GPIO.HIGH
    try:
        while True:
            time.sleep(1)
            print("Outputting {} to pin {}".format(curr_value, output_pin))
            GPIO.output(output_pin, curr_value)
            curr_value ^= GPIO.HIGH#反转
            #curr_value = GPIO.LOW#常亮
    finally:
        GPIO.cleanup()

if __name__ == '__main__':
    main()
