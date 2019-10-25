# Autonomous-Bionic-Implant-Assembler
A robotic device, capable of assembling bionic vision implants at 10:1 scale

This repository provide the operating code for an autonomous bionic implant assembler which is capable of assembling 10:1 scale implant components for the Monash Bionic Eye project. The device uses a raspberry pi 3 model B+ for overall scheduling operation, an Anet A8 3D printer for XYZ translational movement, and an Arduino Uno for gripper movement and LED control. Additionally, a raspberry pi camera is used for visual inspection. 


The Arduino, printer, and camera all all connected to the pi. The Arduino and printer are connected via USB and the camera is connected via a ribbon cable to the camera specific input.


Start.sh is the main executable file, and starts assembler operations.
Controller.py is the overall controlling script, and oversees all functions.
imageProc.py controls the image inspection function.
interface.py manages most user inputs via text.
All gcode files are stored in the 'testfiles' folder.
MotorLEDDriver.ino must be written to the Arduino and values for servo positions must be changed to fit the system.


For operation, the device requires the instillation of openCV. The version used on this device is 4.0.0, instillation instructions found here (instillation is done in a virtual environment): https://www.alatortsev.com/2018/11/21/installing-opencv-4-0-on-raspberry-pi-3-b/

The raspberry pi is running Raspbian Buster, found here: https://downloads.raspberrypi.org/raspbian_full_latest

The raspberry pi also has printrun installed, which facilitates communications with the printer. This can be found here: https://github.com/kliment/Printrun


For printrun, certain changes have been made to prevent errors showing on screen. To include this, a folder entitled 'Printrun' is also available. This includes all code for running the assembler on the raspberry pi including Controller.py, all gcode etc already in the folder. The only file which needs to be changed is Start.sh to point to the location of the Printrun folder. Additionally, the arduino code must still be installed. 

* All intellectual property relating to the Monash Bionic Eye project itself has been removed from these files.
