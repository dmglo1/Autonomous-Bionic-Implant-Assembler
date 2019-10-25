# Autonomous-Bionic-Implant-Assembler
A robotic device, capable of assembling bionic vision implants at 10:1 scale

This repository provide the operating code for an autonomous bionic implant assembler which is capable of assembling 10:1 scale implant components for the Monash Bionic Eye project. The device uses a raspberry pi 3 model B+ for overall scheduling operation, an Anet A8 3D printer for XYZ translational movement, and an Arduino Uno for gripper movement and LED control. Additionally, a raspberry pi camera is used for visual inspection. 

The Arduino, printer, and camera all all connected to the pi. The Arduino and printer are connected via USB and the camera is connected via a ribbon cable to the camera specific input.

Start.sh is the main executable file, and starts assembler operations.
Controller.py is the overall controlling script, and oversees all functions.
imageProc.py controls the image inspection function.
All gcode files are stored in the 'testfiles' folder.
MotorLEDDriver.ino must be written to the Arduino and values for servo positions must be changed to fit the system.

For operation, the device requires the instillation of openCV. The version used on this device is 4.0.0, instillation instructions found here: https://www.alatortsev.com/2018/11/21/installing-opencv-4-0-on-raspberry-pi-3-b/
The raspberry pi is running Raspbian Buster, found here: https://downloads.raspberrypi.org/raspbian_full_latest