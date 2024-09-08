#include "car.h"


//***************************���õ������IO��***************************//
//�������L298Nģ��
//Ӳ������˵����
//PD12----ENA   �Һ��ֵ��PWM
//PC0----IN1    �����Һ��ֵ������
//PC1----IN2    �����Һ��ֵ������

//PD13----ENB   ��ǰ�ֵ��PWM
//PC2----IN3    ������ǰ�ֵ������
//PC3----IN4    ������ǰ�ֵ������

//PD14----ENC   ����ֵ��PWM
//PC4----IN5    ��������ֵ������
//PC5----IN6    ��������ֵ������

//PD15----END   ����ֵ��PWM
//PC6----IN7    ��������ֵ������
//PC7----IN8    ��������ֵ������


void CAR_Init(void)
{
	GPIO_InitTypeDef GPIO_Initure;
  __HAL_RCC_GPIOC_CLK_ENABLE();           //����GPIOFʱ��
	
  GPIO_Initure.Pin = GPIO_PIN_0|GPIO_PIN_1|GPIO_PIN_2|GPIO_PIN_3
											|GPIO_PIN_4|GPIO_PIN_5|GPIO_PIN_6|GPIO_PIN_7; //PF9,10
  GPIO_Initure.Mode = GPIO_MODE_OUTPUT_PP;  //�������
  GPIO_Initure.Pull = GPIO_PULLUP;          //����
  GPIO_Initure.Speed = GPIO_SPEED_HIGH;     //����
  HAL_GPIO_Init(GPIOC,&GPIO_Initure);
	
  HAL_GPIO_WritePin(GPIOC, GPIO_PIN_0|GPIO_PIN_1|GPIO_PIN_2|GPIO_PIN_3
													|GPIO_PIN_4|GPIO_PIN_5|GPIO_PIN_6|GPIO_PIN_7,GPIO_PIN_SET);	//PF9��1��Ĭ�ϳ�ʼ�������
}

void CAR_Stop(void)        //ͣ��
{
	IN1 = 1;   IN2 = 1;
	IN3 = 1;   IN4 = 1;
	IN5 = 1;   IN6 = 1;
	IN7 = 1;   IN8 = 1;
}

void CAR_GoForward(void)    //ǰ��
{
	IN1 = 1;   IN2 = 0;
	IN3 = 1;   IN4 = 0;
	IN5 = 1;   IN6 = 0;
	IN7 = 1;   IN8 = 0;
}

void CAR_GoBack(void)      //����
{
	IN1 = 0;   IN2 = 1;
	IN3 = 0;   IN4 = 1;
	IN5 = 0;   IN6 = 1;
	IN7 = 0;   IN8 = 1;
}

void CAR_TurnLeft(void)     //��ת
{
	IN1 = 1;   IN2 = 0;
	IN3 = 1;   IN4 = 0;
	IN5 = 0;   IN6 = 1;
	IN7 = 0;   IN8 = 1;
}

void CAR_TurnRight(void)     //��ת
{
	IN1 = 0;   IN2 = 1;
	IN3 = 0;   IN4 = 1;
	IN5 = 1;   IN6 = 0;
	IN7 = 1;   IN8 = 0;
}
