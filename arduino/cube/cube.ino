int x;

#define U_ENABLE 22
#define D_ENABLE 22
#define U_STEPS 26
#define U_DIR 24
#define D_STEPS 30
#define D_DIR 28
#define L_ENABLE 32
#define R_ENABLE 32
#define L_STEPS 34
#define L_DIR 36
#define R_STEPS 38
#define R_DIR 40
#define F_ENABLE 42
#define B_ENABLE 42
#define F_STEPS 44
#define F_DIR 46
#define B_STEPS 48
#define B_DIR 50

void setup(){
    Serial.begin(9600); // 9600 bps

    pinMode(U_ENABLE, OUTPUT); // Enable: EN可以使用单片机端口控制，也可以直接连接GND使能
    pinMode(U_STEPS, OUTPUT); // steps:脉冲个数
    pinMode(U_DIR, OUTPUT); // dir:为方向控制
    pinMode(D_STEPS, OUTPUT); // steps:脉冲个数
    pinMode(D_DIR, OUTPUT); // dir:为方向控制
    pinMode(L_ENABLE, OUTPUT); // Enable: EN可以使用单片机端口控制，也可以直接连接GND使能
    pinMode(L_STEPS, OUTPUT); // steps:脉冲个数
    pinMode(L_DIR, OUTPUT); // dir:为方向控制
    pinMode(R_STEPS, OUTPUT); // steps:脉冲个数
    pinMode(R_DIR, OUTPUT); // dir:为方向控制
    pinMode(F_ENABLE, OUTPUT); // Enable: EN可以使用单片机端口控制，也可以直接连接GND使能
    pinMode(F_STEPS, OUTPUT); // steps:脉冲个数
    pinMode(F_DIR, OUTPUT); // dir:为方向控制 
    pinMode(B_STEPS, OUTPUT); // steps:脉冲个数
    pinMode(B_DIR, OUTPUT); // dir:为方向控制
    digitalWrite(U_ENABLE, LOW); // Set Enable low
    digitalWrite(L_ENABLE, LOW); // Set Enable low
    digitalWrite(F_ENABLE, LOW); // Set Enable low
}

void move(char face, int steps)
{
    int ENABLE, STEPS, DIR;
    switch(face)
    {
        case 'U':
        ENABLE = U_ENABLE;
        STEPS = U_STEPS;
        DIR = U_DIR;
        break;

        case 'D':
        ENABLE = D_ENABLE;
        STEPS = D_STEPS;
        DIR = D_DIR;
        break;

        case 'L':
        ENABLE = L_ENABLE;
        STEPS = L_STEPS;
        DIR = L_DIR;
        break;

        case 'R':
        ENABLE = R_ENABLE;
        STEPS = R_STEPS;
        DIR = R_DIR;
        break;

        case 'F':
        ENABLE = F_ENABLE;
        STEPS = F_STEPS;
        DIR = F_DIR;
        break;
        
        case 'B':
        ENABLE = B_ENABLE;
        STEPS = B_STEPS;
        DIR = B_DIR;
        break;
    }
    if(steps == 3)
    {
        digitalWrite(26, HIGH); // Set Dir high
    }
    else
    {
        digitalWrite(26, LOW); // Set Dir low
    }

    Serial.println(ENABLE);
    Serial.println(STEPS);
    Serial.println(DIR);

    
    digitalWrite(22, LOW); // ENABLE
    if(steps == 2)
    {
        for(x=0; x<100; x++) // Loop 100 times for 180 degree
        {
            digitalWrite(24, HIGH); // Output high
            delayMicroseconds(1000); // Wait 1/2 a ms
            digitalWrite(24, LOW); // Output low
            delayMicroseconds(1000); // Wait 1/2 a ms
        }
    }
    else
    {
        for(x=0; x<50; x++) // Loop 50 times for 90 degree
        {
            digitalWrite(24, HIGH); // Output high
            delayMicroseconds(1000); // Wait 1/2 a ms
            digitalWrite(24, LOW); // Output low
            delayMicroseconds(1000); // Wait 1/2 a ms
        }
    }
    
    digitalWrite(22, HIGH); // DISABLE
}

void loop()
{
    
        move('D', 1);
    if (Serial.available())
    {
        
    //Serial.println("move u1");
        /*
        move('R', 1);
        move('F', 1);
        move('D', 1);
        move('L', 1);
        move('B', 1);
        face = Serial.read();
        
        if(face == 85 || face == 68 || face == 76 || face == 82 || face == 70 || face == 66) // UDLRFB
        {
            steps = Serial.read();
            move(face, steps - 48);
        }
        else
        {
            if(face == 72) // double H for init
            {
                if(Serial.read() == 72)
                {
                    Serial.println("Serial is working!");
                }
            }
        }
        */
    }
}

