#include <Servo.h>

Servo gripperLeft;  //Creates servo object to control the left gripper servo motor.
Servo gripperRight; //Creates servo object to control the right gripper servo motor.

const int ledPin =  11; //Assigns a pin to the led array.

const int openLeft = 100;    //Variable to store the left servo open position.
const int midLeft = 155;    //Variable to store the left left servo partially open position.
const int closeLeft = 160;    //Variable to store the servo closed position.

const int openRight = 130; //Variable to store the right servo open position.
const int midRight = 70;
const int closeRight = 63;

int posLeft = openLeft;    //Assigns initial position of servo.
int posRight = openRight;

char data; //Variable for reading serial port.

void setup() {
  Serial.begin(9600);
  pinMode(ledPin, OUTPUT);  //Sets LED pin.
  digitalWrite(ledPin, LOW);  //Turns LEDs off.
  gripperLeft.attach(6);  //Attaches the left gripper servo on pin 6 to the servo object.
  gripperRight.attach(5); //Attaches the right gripper servo on pin 5 to the servo object.
  
  gripperLeft.write(posLeft); //Moves left gripper to open position.
  gripperRight.write(posRight); //Moves right gripper to open position.
  
  for(int i = 0; i<3; i++){ //Flashes LEDs to show user that the Arduino is active and ready to receive input commands.
    digitalWrite(ledPin, HIGH); //Turns on LEDs.
    delay(25);
    digitalWrite(ledPin, LOW); //Turns off LEDs.
    delay(25);
  }
  
  while (!Serial) {
    ; //Waits for serial port to connect. 
  }
}

void loop() {
  //Code runs through continuous loop, reading if there is any new instructional data, and if so, executing the instruction.
    while(Serial.available()){  //If there is new data.
      data = Serial.read(); //Reads the data available.
      if(data == '0'){ledOn();} //Turns the LEDs on.
      if(data == '1'){ledOff();}  //Turns the LEDs off
      if(data == '2'){ledErr();}  //Strobes the LEDs three times.
      if(data == '3'){for(int i=0; i<7; i++){lMotorOpen();}}  //Opens the left gripper.
      if(data == '4'){for(int i=0; i<7; i++){lMotorMid();}} //Partially opens the left gripper.
      if(data == '5'){for(int i=0; i<7; i++){lMotorClose();}} //Closes the left gripper.
      if(data == '6'){for(int i=0; i<7; i++){rMotorOpen();}}  //Opens the right gripper.
      if(data == '7'){for(int i=0; i<7; i++){rMotorMid();}} //Partially opens the right gripper.
      if(data == '8'){for(int i=0; i<7; i++){rMotorClose();}} //Closes the right gripper.
      Serial.println(data); //Prints the data that has been read.
    }   
    delay(1);
}

void ledOn() {
  //Function which turns the LEDs on for the camera.
    analogWrite(ledPin, 30); //LEDs set to reduced brightness.
}

void ledOff() {
  //Function which turns off the LEDs.
    digitalWrite(ledPin, LOW);
}

void ledErr() {
  //Flashes the LEDs on and off three times in three seconds.
  for(int i = 0; i<3; i++){
    digitalWrite(ledPin, HIGH);
    delay(500);
    digitalWrite(ledPin, LOW);
    delay(500);
  }
}

void rMotorOpen() {
  //Opens the right gripper.
  for(int i=0; i<(openRight - posRight); i++){ //Changes the position of the motor until it has reached its target position.
    posRight++; //Increments position value.
    gripperRight.write(posRight); //Writes position to the grippers.
    delay(20);
  }
}

void rMotorMid() {
  //Partially opens the right gripper, functions similarly to rMotorOpen().
  if(posRight > midRight){ //If the motor is closed, and needs to open outwards to be partially open.
    for(int i=0; i<(posRight - midRight); i++){
      posRight--; //Decrements position value.
      gripperRight.write(posRight);
      delay(20);
    }
  } else{ //If the motor is open and needs to close inwards to be partially open.
    for(int i=0; i<(midRight - posRight); i++){
      posRight++;
      gripperRight.write(posRight);
      delay(20);
    }
  }
}

void rMotorClose() {
  //Closes the right gripper, functions similarly to rMotorOpen().
  for(int i=0; i<(posRight - closeRight); i++){
    posRight--;
    gripperRight.write(posRight);
    delay(20);
  }
}

void lMotorOpen() {
  //Opens the left gripper, functions similarly to rMotorOpen(), however, increments and decrements of position are reversed.
    for(int i=0; i<(posLeft - openLeft); i++){
      posLeft--;
      gripperLeft.write(posLeft);
      delay(20);
    }
  }

void lMotorMid() {
  //Partially opens the left gripper, functions similarly to rMotorMid().
  if(posLeft < midLeft){
    for(int i=0; i<(midLeft - posLeft); i++){
      posLeft++;
      gripperLeft.write(posLeft);
      delay(20);
    }
  } else{
    for(int i=0; i<(posLeft - midLeft); i++){
      posLeft--;
      gripperLeft.write(posLeft);
      delay(20);
    }
  }
}

void lMotorClose() {
  //Closes the left gripper, functions similarly to rMotorOpen().
  for(int i=0; i<(closeLeft - posLeft); i++){
    posLeft++;
    gripperLeft.write(posLeft);
    delay(20);
  }
}
