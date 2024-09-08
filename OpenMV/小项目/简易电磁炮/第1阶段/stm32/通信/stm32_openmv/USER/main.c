#include "sys.h"
#include "delay.h"
#include "my_usart.h"
#include "led.h"
#include "key.h"
#include "string.h"
#include "oled.h"
#include "string.h"

/**************����ͨ��IO������***************/
//PA9(TXD)--------P5(RXD)
//PA10(RXD)-------P4(TXD)
//OpenMv��STM32��Ҫ����
/*********************************************/


int main(void)
{
	u8 len;	
	u16 t;
	char cmd[200];


  HAL_Init();                    	//��ʼ��HAL��    
  Stm32_Clock_Init(336,8,2,7);  	//����ʱ��,168Mhz
	delay_init(168);               	//��ʼ����ʱ����
	my_usart_init(115200);
	LED_Init();											//��ʼ��LED	
  KEY_Init();                     //��ʼ������
	OLED_Init();
	
  while(1)
  {
		if( USART_RX_STA & 0x8000 )
		{
			len = USART_RX_STA & 0x3FFF;
			for(t = 0;t < len;t++)
			{
				cmd[t] = USART_RX_BUF[t];
				//Receive_Prepare(USART_RX_BUF[t]);
				while( (USART1->SR&0X40) == 0);
			}
			USART_RX_STA = 0;
			//HAL_UART_Transmit(&UART1_Handler,(u8 *)USART_RX_BUF,len,0xffff);
		}
		//�տ���PF10��������
		if( !(strcmp(cmd,"begin")) )               //�ж�strcmp�������ַ��Ƿ����
		{
			HAL_GPIO_WritePin(GPIOB,GPIO_PIN_8,GPIO_PIN_SET); 	//PB8 ��1  ������
		
      HAL_GPIO_WritePin(GPIOF,GPIO_PIN_10,GPIO_PIN_RESET);   	//PF10��
	
			memset( cmd,0,strlen(cmd) );               //���cmd[]
		}
		else if( !(strcmp(cmd,"close")) )
		{
			HAL_GPIO_WritePin(GPIOB,GPIO_PIN_8,GPIO_PIN_RESET); 	//PB8 ��0 ������
      HAL_GPIO_WritePin(GPIOF,GPIO_PIN_10,GPIO_PIN_SET);   	//PF10��
			memset( cmd,0,strlen(cmd) );               //���cmd[]
		}

	}
		
		
}



