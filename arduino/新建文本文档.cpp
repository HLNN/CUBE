int x;
#define COUNT  100
#define SLEEPTIME 400
 
#define U_ENABLE 22
#define D_ENABLE 22
#define U_DIR 24
#define U_STEPS 26
#define D_DIR 28
#define D_STEPS 30
#define L_ENABLE 32
#define R_ENABLE 32
#define L_DIR 34
#define L_STEPS 36
#define R_DIR 38
#define R_STEPS 40
#define F_ENABLE 42
#define B_ENABLE 42
#define F_DIR 44
#define F_STEPS 46
#define B_DIR 48
#define B_STEPS 50

void setup()
{
    // init serial 9600 bps
    Serial.begin(9600);

    // set pins
    pinMode(U_ENABLE, OUTPUT);
    pinMode(U_STEPS, OUTPUT);
    pinMode(U_DIR, OUTPUT);
    pinMode(D_STEPS, OUTPUT);
    pinMode(D_DIR, OUTPUT);
    pinMode(L_ENABLE, OUTPUT);
    pinMode(L_STEPS, OUTPUT);
    pinMode(L_DIR, OUTPUT);
    pinMode(R_STEPS, OUTPUT);
    pinMode(R_DIR, OUTPUT);
    pinMode(F_ENABLE, OUTPUT);
    pinMode(F_STEPS, OUTPUT);
    pinMode(F_DIR, OUTPUT);
    pinMode(B_STEPS, OUTPUT);
    pinMode(B_DIR, OUTPUT);
    // disable all steper
    digitalWrite(U_ENABLE, HIGH);
    digitalWrite(L_ENABLE, HIGH);
    digitalWrite(F_ENABLE, HIGH);
}


void move(char face, int steps)
{
    // define tmp pin
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
        // Set Dir HIGH
        digitalWrite(DIR, HIGH);
    }
    else
    {
        // Set Dir LOW
        digitalWrite(DIR, LOW);
    }

    
    digitalWrite(U_ENABLE, LOW);
    if(steps == 2)
    {
        // Loop COUNT * 2 times
        for(x = 0; x < COUNT * 2; x++)
        {
            digitalWrite(STEPS,HIGH);
            delayMicroseconds(SLEEPTIME);
            digitalWrite(STEPS,LOW);
            delayMicroseconds(SLEEPTIME);
        }
    }
    else
    {
        // Loop COUNT times
        for(x = 0; x < COUNT; x++)
        {
            digitalWrite(STEPS,HIGH);
            delayMicroseconds(SLEEPTIME);
            digitalWrite(STEPS,LOW);
            delayMicroseconds(SLEEPTIME);
        }
    }
    digitalWrite(U_ENABLE, HIGH);

    //delay(1000);
} 


void lop()
{
    int face, steps;
    face = Serial.read();
    steps = Serial.read();

    // in UDLRFB
    if(face == 85 || face == 68 || face == 76 || face == 82 || face == 70 || face == 66)
    {
        move(face, steps - 48);
        Serial.println("OK!");
        Serial.println(face);
        Serial.println(steps);
    }
    else
    {
        if(face == 72) // double H for init
        {
            if(steps == 72)
            {
                Serial.println("Serial is working!");
            }
        }
    }
}


void loop()
{
    Serial.println(Serial.readString());
}