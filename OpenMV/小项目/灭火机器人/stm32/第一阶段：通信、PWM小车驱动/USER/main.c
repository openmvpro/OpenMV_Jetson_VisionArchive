#include "sys.h"
#include "delay.h"
#include "my_usart.h"
#include "led.h"
#include "key.h"
#include "string.h"
#include "oled.h"
#include "openmv.h"
#include "pwm.h"
#include "timer.h"
#include "car.h"

/**************����ͨ��IO������***************/
//PA9(TXD)--------P5(RXD)
//PA10(RXD)-------P4(TXD)
//OpenMv��STM32��Ҫ����
/*********************************************/


int main(void)
{
  HAL_Init();                    	//��ʼ��HAL��    
  Stm32_Clock_Init(336,8,2,7);  	//����ʱ��,168Mhz
	delay_init(168);               	//��ʼ����ʱ����
	my_usart_init(115200);
	LED_Init();											//��ʼ��LED	
  KEY_Init();                     //��ʼ������
	OLED_Init();
	CAR_Init();
	TIM3_Init(5000-1,8400-1);       //��ʱ��3��ʼ��������Ϊ500ms
	TIM4_PWM_Init(1000-1,84-1);    	//84M/84=1M�ļ���Ƶ�ʣ��Զ���װ��Ϊ500����ôPWMƵ��Ϊ1M/500=2kHZ
	
  while(1)
  {
		LED0 = 0;
	}
		
		
}


