
/* 
 Arduino program that controlls the motor speed
 */

#include <Stepper.h>
#include <stdio.h>

int stepsPerRevolution = 20;  // change this to fit the number of steps per revolution
// for your motor, actually this is the number of degrees of rotation per step.

// initialize the stepper library on pins 8 through 11:
Stepper myStepper(stepsPerRevolution, 8,9,10,11);            

int stepCount = 0;  
int x ='f';// number of steps the motor has taken

void setup() {
  // set the speed at 60 rpm:
  myStepper.setSpeed(120);
  // initialize the serial port:
  Serial.begin(9600);
}

void loop() {
  // step one step:
  if(Serial.available()){
    x = Serial.read();
    /*
    When the controlling program passed command, preceded by "v", then 
     read the "StepsPerRevolution" value from it. For e.g:
     v24,
     The above message implies, takes 24 steps for one revolution
     */
    if (x == 'v') {
      int val = 0;
      // keep reading until an integer is fed
      char ch;
      do {
        delay(50);
        ch = Serial.read();
        if (ch >= '0' && ch <= '9') {
          int num = ch - '0';
          val = val*10 + num;
        } 
        else if (ch == ',') { // terminate on ','
          Serial.print(val);
          // update the number of revolutions to conduct in this test run
          stepsPerRevolution = val;
          val =0;
        }
      }
      while (ch != ',') ;
    }

    if(x=='h')
    {
      myStepper.step(stepsPerRevolution);
      Serial.print("steps:" );
      Serial.print(stepCount);
      Serial.println(stepsPerRevolution);
      stepCount++;
      delay(200);
    }
  }
}


