#ifndef _MY_USART_H
#define _MY_USART_H
#include "sys.h"
#include "stdio.h"	



extern UART_HandleTypeDef UART1_Handler;       //UART句柄

void my_usart_init(u32 bound);
void Data_Processing(u8 *data_buf,u8 num) ;
void Receive_Prepare(u8 data);

#define USART_REC_LEN  			200  	             //定义最大接收字节数 200
#define EN_USART1_RX 			1		                 //使能（1）/禁止（0）串口1接收
#define MAX_DATA_LENS       10
	  	 
extern u8  USART_RX_BUF[USART_REC_LEN];        //接收缓冲,最大USART_REC_LEN个字节.末字节为换行符 
extern u16 USART_RX_STA;         		           //接收状态标记	
extern u8 control_data[MAX_DATA_LENS];
extern u8 X;
extern u8 Y;


#define RXBUFFERSIZE   1                       //缓存大小
extern u8 aRxBuffer[RXBUFFERSIZE];             //HAL库USART接收Buffer

#endif



