#ifndef  _SMG_H
#define  _SMG_H
#include "sys.h"

#define SCK PFout(13)
#define RCK PFout(14)
#define SI  PFout(15)

extern u8 Wei_Code[];
extern u8 Duan_Code[];
extern u8 Disp_Code[];
extern u8 Code[];

void SMG_Init(void);
void date_in(u8 temp);
void date_out(void);
void SMG_Disp(u8 *Disp_Code);
void DIV_number(u8 counter);
void SMG_light(void);
void SMG(u8 *Disp_Code);


#endif
