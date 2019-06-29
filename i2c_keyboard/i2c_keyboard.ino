#include<Wire.h>

#define R0 23
#define R1 22
#define R2 21
#define R3 20
#define R4 17
#define R5 16
#define R6 15
#define R7 14

#define C0 2
#define C1 3
#define C2 4
#define C3 5
#define C4 6
#define C5 7
#define C6 8
#define C7 9


byte keys[8] = { 0, 0, 0, 0, 0, 0, 0, 0 };

void requestEvent()  
{
    Wire.write(keys, 8);
    for (int i=0; i<8; ++i) {
        keys[i] = 0;
    }
}

void setup() {
    pinMode(R0, OUTPUT);
    pinMode(R1, OUTPUT);
    pinMode(R2, OUTPUT);
    pinMode(R3, OUTPUT);
    pinMode(R4, OUTPUT);
    pinMode(R5, OUTPUT);
    pinMode(R6, OUTPUT);
    pinMode(R7, OUTPUT);

    pinMode(C0, INPUT);
    pinMode(C1, INPUT);
    pinMode(C2, INPUT);
    pinMode(C3, INPUT);
    pinMode(C4, INPUT);
    pinMode(C5, INPUT);
    pinMode(C6, INPUT);
    pinMode(C7, INPUT);
  
    Wire.begin();
    Serial.begin(9600);
    Wire.begin(8);     
    Wire.onRequest(requestEvent); 
}

void loop() {
    for (int r=0; r<8; r++) {
        digitalWrite(R0, (r == 0) ? HIGH : LOW);
        digitalWrite(R1, (r == 1) ? HIGH : LOW);
        digitalWrite(R2, (r == 2) ? HIGH : LOW);
        digitalWrite(R3, (r == 3) ? HIGH : LOW);
        digitalWrite(R4, (r == 4) ? HIGH : LOW);
        digitalWrite(R5, (r == 5) ? HIGH : LOW);
        digitalWrite(R6, (r == 6) ? HIGH : LOW);
        digitalWrite(R7, (r == 7) ? HIGH : LOW);

        if (digitalRead(C0) == HIGH) keys[r] |= 1 << 0;
        if (digitalRead(C1) == HIGH) keys[r] |= 1 << 1;
        if (digitalRead(C2) == HIGH) keys[r] |= 1 << 2;
        if (digitalRead(C3) == HIGH) keys[r] |= 1 << 3;
        if (digitalRead(C4) == HIGH) keys[r] |= 1 << 4;
        if (digitalRead(C5) == HIGH) keys[r] |= 1 << 5;
        if (digitalRead(C6) == HIGH) keys[r] |= 1 << 6;
        if (digitalRead(C7) == HIGH) keys[r] |= 1 << 7;
    }
    /*
    for (int r=0; r<8; ++r) {
        Serial.print(keys[r]);
    }
    Serial.println("");
    delay(1000);
    */
}
