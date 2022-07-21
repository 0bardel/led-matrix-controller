#include <FastLED.h>
#include "PROGMEM_readAnything.h"
#include "animations.h"
#include <Adafruit_TiCoServo.h>
#include <avr/io.h>
#include <avr/interrupt.h>


#define LED_PIN     13
#define NUM_LEDS    72
#define BRIGHTNESS  10
#define LED_TYPE    WS2812B
#define COLOR_ORDER GRB

#define SERVO1_PIN    11
#define SERVO2_PIN    12
#define SERVO_MIN 600// shortest pulse
#define SERVO_MAX 2400 // longest pulse
#define BUT_1 6
#define BUT_2 7
#define BUT_3 8
#define BUT_4 9

#define BUT_INTERRUPT 2
#define TRIGGER_DELAY 300
static volatile int triggerTime = 0;
static volatile bool flag1 = 0;
    static volatile bool flag2 = 0;
    static volatile bool flag3 = 0;
    static volatile bool flag4 = 0;

int switchPin = 12;                        // button pin
int switchState = HIGH;                    // button value

#define ENC_A 3                            // Rotary encoder Pin A
#define ENC_B 4                              // Rotary encoder Pin B
static volatile bool a0 = 0; // Remembers last ENC_A position
static volatile bool c0 = 0; // Remembers last ENC_B position during ENC_A Change

Anim a;
Adafruit_TiCoServo servo1;
Adafruit_TiCoServo servo2;
int ledBrightness = BRIGHTNESS;
void setup() {
    delay( 500 ); // power-up safety delay
    FastLED.addLeds<LED_TYPE, LED_PIN, COLOR_ORDER>(a.leds, NUM_LEDS).setCorrection( TypicalLEDStrip );
    FastLED.setBrightness(  ledBrightness );
    servo1.attach(SERVO1_PIN, SERVO_MIN, SERVO_MAX);
    servo2.attach(SERVO2_PIN, SERVO_MIN, SERVO_MAX);

    pinMode(LED_BUILTIN, OUTPUT);
    pinMode(BUT_1, INPUT_PULLUP);
    pinMode(BUT_2, INPUT_PULLUP);
    pinMode(BUT_3, INPUT_PULLUP);
    pinMode(BUT_4, INPUT_PULLUP);
    pinMode(BUT_INTERRUPT, INPUT_PULLUP);
    pinMode(ENC_A, INPUT_PULLUP);
    pinMode(ENC_B, INPUT_PULLUP);

    attachInterrupt(digitalPinToInterrupt(ENC_A), encoderUpdate, CHANGE);
    attachInterrupt(digitalPinToInterrupt(BUT_INTERRUPT), buttonUpdate, FALLING);

    a.load(gifs[0]);
    a.uniformColorIndex = 0;
}


void loop()
{   

    resolveInputs();

    a.updateMatrix();
    FastLED.show();
    //int x = map(time%50, 0, 50, SERVO_MIN, SERVO_MAX);
    //servo1.write(x);
    //servo2.write(SERVO_MAX + SERVO_MIN - x);
    //time++;
    FastLED.delay(a.getDelay());
    digitalWrite(LED_BUILTIN, LOW);
}

void adjustBrightness(bool increase, int val = 1){
    int dir = increase?1:-1;
    ledBrightness = ledBrightness + dir*val > 255? 255: (ledBrightness + dir*val) <0?0:ledBrightness + dir*val;

    
    FastLED.setBrightness(ledBrightness);
}

void encoderUpdate() {
    
   int a =digitalRead(ENC_A);
  int b =digitalRead(ENC_B);
  if (a != a0) {              // A changed
    a0 = a;
    if (b != c0) {
      c0 = b;
      adjustBrightness(a==b, 5);
    }
  }
}


void buttonUpdate(){
    static bool  but1;
    static bool  but2;
    static bool  but3;
    static bool  but4;
    do{
    but1 = !digitalRead(BUT_1);
    but2 = !digitalRead(BUT_2);
    but3 = !digitalRead(BUT_3);
    but4 = !digitalRead(BUT_4);
    flag1 = but1+flag1?1:0;
    flag2 = but2+flag2?1:0;
    flag3 = but3+flag3?1:0;
    flag4 = but4+flag4?1:0;
    }while(but1+but2+but3+but4);
}

void resolveInputs(){
    char flag = 0;
    flag += flag1?1:0;
    flag += flag2?2:0;
    flag += flag3?4:0;
    flag += flag4?8:0;
    if(!flag)
        return;

    if(flag<sizeof(gifs)/sizeof(Gif)+1)
        a.next = gifs+flag-1;
    flag1 = false;
    flag2 = false;
    flag3 = false;
    flag4 = false;
}