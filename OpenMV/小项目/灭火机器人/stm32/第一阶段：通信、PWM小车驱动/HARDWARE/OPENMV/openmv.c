#include "openmv.h"

/******openmv数据解析******/
/*********主要原理*********/
/*openmv通过线性回归得到偏移角度和偏移尺寸，
	并加上0XAA、0XAE两个帧头（可以根据自己自行修改）
	0x0D,0x0A两个帧尾（结束接受数据的标识符，不可修改）
	打包成16进制数据，发送给stm32	*/
//这就是为什么要对接收到的数据进行还原


int X,Y,Z;    

/*************************************/
//对openmv发送的数据进行还原
//最终得到偏移角度和偏移尺寸
/*************************************/
void Data_Processing(u8 *data_buf,u8 num)   
{
	int pan_state, car_angle,car_length;
	/*读取偏移角度原始数据*/
  pan_state = (int)(*(data_buf+1)<<0) | (int)(*(data_buf+2)<<8) | (int)(*(data_buf+3)<<16) | (int)(*(data_buf+4)<<24) ; 
  X = pan_state;
	
	/*读取偏移尺寸原始数据*/
  car_angle = (int)(*(data_buf+5)<<0) | (int)(*(data_buf+6)<<8) | (int)(*(data_buf+7)<<16) | (int)(*(data_buf+8)<<24) ; 
  Y = car_angle; 

	car_length = (int)(*(data_buf+9)<<0) | (int)(*(data_buf+10)<<8) | (int)(*(data_buf+11)<<16) | (int)(*(data_buf+12)<<24) ; 
  Z = car_length; 
  
}


/*************************************/
//用于对openmv发送过来的数据进行解析
//通过对两个帧头的判断进而判断数据的有效性
/*************************************/
void Receive_Prepare(u8 data)    
{
	/*静态局部变量：接收缓存*/
	static u8 RxBuffer[10];
	/*数据长度：数组下标*/
  static u8  _data_cnt = 0;
	/*接受状态*/
  static u8 state = 0;
  if(state == 0 && data == 0xAA)
  {
		state = 1;
  } 
  else if(state==1 && data == 0xAE)
	{
		state = 2;
    _data_cnt = 0; 
  }
  else if(state == 2)  
  {
    RxBuffer[++_data_cnt] = data;
    if(_data_cnt >= 12)
    { 
			state = 0;
      Data_Processing(RxBuffer,_data_cnt);
		}
   } 
   else
		state = 0;   
}
