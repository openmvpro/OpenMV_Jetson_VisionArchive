#include "car.h"


//***************************配置电机驱动IO口***************************//
//电机驱动L298N模块
//硬件连接说明：
//PD12----ENA   右后轮电机PWM
//PC0----IN1    控制右后轮电机正反
//PC1----IN2    控制右后轮电机正反

//PD13----ENB   右前轮电机PWM
//PC2----IN3    控制右前轮电机正反
//PC3----IN4    控制右前轮电机正反

//PD14----ENC   左后轮电机PWM
//PC4----IN5    控制左后轮电机正反
//PC5----IN6    控制左后轮电机正反

//PD15----END   左后轮电机PWM
//PC6----IN7    控制左后轮电机正反
//PC7----IN8    控制左后轮电机正反


void CAR_Init(void)
{
	GPIO_InitTypeDef GPIO_Initure;
  __HAL_RCC_GPIOC_CLK_ENABLE();           //开启GPIOF时钟
	
  GPIO_Initure.Pin = GPIO_PIN_0|GPIO_PIN_1|GPIO_PIN_2|GPIO_PIN_3
											|GPIO_PIN_4|GPIO_PIN_5|GPIO_PIN_6|GPIO_PIN_7; //PF9,10
  GPIO_Initure.Mode = GPIO_MODE_OUTPUT_PP;  //推挽输出
  GPIO_Initure.Pull = GPIO_PULLUP;          //上拉
  GPIO_Initure.Speed = GPIO_SPEED_HIGH;     //高速
  HAL_GPIO_Init(GPIOC,&GPIO_Initure);
	
  HAL_GPIO_WritePin(GPIOC, GPIO_PIN_0|GPIO_PIN_1|GPIO_PIN_2|GPIO_PIN_3
													|GPIO_PIN_4|GPIO_PIN_5|GPIO_PIN_6|GPIO_PIN_7,GPIO_PIN_SET);	//PF9置1，默认初始化后灯灭
}

void CAR_Stop(void)        //停车
{
	IN1 = 1;   IN2 = 1;
	IN3 = 1;   IN4 = 1;
	IN5 = 1;   IN6 = 1;
	IN7 = 1;   IN8 = 1;
}

void CAR_GoForward(void)    //前进
{
	IN1 = 1;   IN2 = 0;
	IN3 = 1;   IN4 = 0;
	IN5 = 1;   IN6 = 0;
	IN7 = 1;   IN8 = 0;
}

void CAR_GoBack(void)      //后退
{
	IN1 = 0;   IN2 = 1;
	IN3 = 0;   IN4 = 1;
	IN5 = 0;   IN6 = 1;
	IN7 = 0;   IN8 = 1;
}

void CAR_TurnLeft(void)     //左转
{
	IN1 = 1;   IN2 = 0;
	IN3 = 1;   IN4 = 0;
	IN5 = 0;   IN6 = 1;
	IN7 = 0;   IN8 = 1;
}

void CAR_TurnRight(void)     //右转
{
	IN1 = 0;   IN2 = 1;
	IN3 = 0;   IN4 = 1;
	IN5 = 1;   IN6 = 0;
	IN7 = 1;   IN8 = 0;
}
