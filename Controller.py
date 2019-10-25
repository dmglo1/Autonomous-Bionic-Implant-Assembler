import time
import serial
import sys
import pickle
from printrun.printcore import printcore
from printrun import gcoder
from imageProc import objectDet
from interface import start, insert, FPickupErr, PPickupErr, AssemFail, restockF, restockP, calib, feedIns, Xadj, Yadj

printer = printcore('/dev/ttyUSB1',115200) #Connects to the printer.
arduino = serial.Serial('/dev/ttyUSB0', 9600) #Connects to the arduino.

#The following imports gcode text files and assigns them to arrays to be sent to the printer.
home = [i.strip() for i in open('/home/pi/Printrun/testfiles/home.gcode')]
home = gcoder.LightGCode(home)
getComponent = [i.strip() for i in open('/home/pi/Printrun/testfiles/getComponent.gcode')] 
getComponent = gcoder.LightGCode(getComponent)
feedthroughView = [i.strip() for i in open('/home/pi/Printrun/testfiles/feedthroughView.gcode')] 
feedthroughView = gcoder.LightGCode(feedthroughView)
preformView = [i.strip() for i in open('/home/pi/Printrun/testfiles/preformView.gcode')] 
preformView = gcoder.LightGCode(preformView)
feedthroughPickup = [i.strip() for i in open('/home/pi/Printrun/testfiles/feedthroughPickup.gcode')] 
feedthroughPickup = gcoder.LightGCode(feedthroughPickup)
preformPickup = [i.strip() for i in open('/home/pi/Printrun/testfiles/preformPickup.gcode')] 
preformPickup = gcoder.LightGCode(preformPickup)
feedthroughDrop = [i.strip() for i in open('/home/pi/Printrun/testfiles/feedthroughDrop.gcode')] 
feedthroughDrop = gcoder.LightGCode(feedthroughDrop)
preformDrop = [i.strip() for i in open('/home/pi/Printrun/testfiles/preformDrop.gcode')] 
preformDrop = gcoder.LightGCode(preformDrop)

#Initialises variables
numberAssem = 0
percent = 0

#Loads values of coordinates of the first placement location saved in a file.
filename = 'startCoords'
infile = open(filename,'rb')
startCoords = pickle.load(infile)
infile.close()

#Takes the values of the first placement location and converts them to floats
X = float(startCoords.get('X'))
Y = float(startCoords.get('Y'))


def FDrop(sec):
    #Defines the process for dropping a feedthrough in the feedthrough bin. Takes 'sec' input as the time delay between previous command and start of this function.
    time.sleep(sec) #Sleeps for the time determined by the variable 'sec'
    print("  Throwing Feedthrough Away...") #Writes information to the screen.
    printer.startprint(feedthroughDrop) #Moves the gripper to the drop location.
    time.sleep(5)
    arduino.write(b'4\n') #Partially opens the feedthrough gripper.

def PDrop(sec):
    #Defines the process for dropping a preform in the preform bin. Takes 'sec' input as the time delay between previous command and start of this function.
    time.sleep(sec) #Sleeps for the time determined by the variable 'sec'
    print("  Throwing Preform Away...") #Writes information to the screen.
    printer.startprint(preformDrop) #Moves the gripper to the drop location.
    time.sleep(5)
    arduino.write(b'7\n') #Partially opens the feedthrough gripper.

def pickup(obj):
    #Defines the process for picking up distributed object - object to be picked specified through paramater 'obj' by either 'feedthrough' or 'preform'.
    #Function performs all vision, gripper, and movement operation.
    arduino.write(b'6\n') #Open preform grippers.
    time.sleep(1)
    arduino.write(b'3\n') #Open feedthrough grippers.
    if obj == 'feedthrough': #If the object being picked up is specified as a feedthrough.
        print("  Moving to detect Feedthrough...") 
        printer.startprint(feedthroughView) #Positions camera for feedthrough detection.
        while printer.printing: #Checks if the printer is still in operation.
            time.sleep(1)
        arduino.write(b'0\n') #Turns on LEDs for camera.
        time.sleep(7)
        print("  Detecting Feedthrough...") 
        det = objectDet('feedthrough') #Calls detection function.
        print("  " + det) #Prints outcome of detection.
        if det != 'No Feedthrough Detected.': #When an object is in the distribution holder
            print("  Picking-up Feedthrough...") 
            printer.startprint(feedthroughPickup) #Moves object to feedthrough gripper.
            while printer.printing:
                time.sleep(1)
            time.sleep(5)          
            arduino.write(b'5\n') #Closes gripper on feedthrough.
            time.sleep(3)
            printer.send_now('G1 Z30') #Moves gripper up 30mm.
            time.sleep(3)
            print("  Confirming Pickup...") 
            printer.startprint(feedthroughView) #Moves back to camera view of feedthrough.
            while printer.printing:
                time.sleep(1)
            time.sleep(3)
            compCheck = objectDet('feedthrough') #Checks if feedthrough is still in holder.
            if compCheck != 'No Feedthrough Detected.': #Checks if the feedthrough has not been picked up, if so, then executes the following.
                print("  ERROR:Pickup failure. Re-attempting...") 
                arduino.write(b'3\n') #Opens feedthrough gripper.
                printer.startprint(feedthroughPickup) #Moves object to feedthrough gripper.
                while printer.printing:
                    time.sleep(1)
                time.sleep(5)          
                arduino.write(b'5\n') #Closes gripper on feedthrough.
                time.sleep(3)
                printer.send_now('G1 Z30') #Moves gripper up 30mm.
                time.sleep(5)
                print("  Confirming Pickup...") 
                printer.startprint(feedthroughView) #Moves back to camera view of feedthrough.
                while printer.printing:
                    time.sleep(1)
                time.sleep(5)
                compCheck = objectDet('feedthrough') #Checks if feedthrough is still in holder.
                if compCheck != 'No Feedthrough Detected.': #Checks if the feedthrough has not been picked up, if so, then executes the following.
                    arduino.write(b'2\n') #Strobes LEDs.
                    res = FPickupErr() #Calls pickup error function.
                    while res == 0: #Waits for user to input appropriate response.
                        res = PPickupErr()
                    arduino.write(b'3\n') #Opens feedthrough grippers.
                    return 'FPickupErr'
            if det == 'Incorrect Size Feedthrough Detected.': #Checks if the feedthrough dimensions are incorrect.
                return "FSizeErr" #If so, returns incorrect size.
            else: #Else, if the feedthrough dimensions are correct.
                time.sleep(1)
                arduino.write(b'1\n') #Turns off LEDs.
                return "correct" #Returns correct size.
        else: #Else, if no object is detected.
            return "FNoObjErr" #Returns no object.
    elif obj == 'preform': #If the object being picked up is specified as a preform.
        print("  Moving to detect Preform...") 
        printer.startprint(preformView) #Positions camera for preform detection.
        while printer.printing:
            time.sleep(1)
        arduino.write(b'0\n') #Turns on LEDs for camera.
        time.sleep(7)
        print("  Detecting Preform...") 
        det = objectDet('preform') #Calls detection function.
        print("  " + det) #Prints outcome of detection.
        if det != 'No Preform Detected.': #When an object is in the distribution holder
            print("  Picking-up Preform...") 
            printer.startprint(preformPickup) #Moves object to preform gripper.
            while printer.printing:
                time.sleep(1)
            arduino.write(b'7\n') #Partially closes gripper.
            time.sleep(5)          
            arduino.write(b'8\n') #Closes gripper on preform.
            time.sleep(3)
            printer.send_now('G1 Z30') #Moves gripper up 30mm.
            time.sleep(3)
            print("  Confirming Pickup...") 
            printer.startprint(preformView) #Moves back to camera view of preform.
            while printer.printing:
                time.sleep(1)
            time.sleep(3)
            compCheck = objectDet('preform') #Checks if preform is still in holder.
            if compCheck != 'No Preform Detected.':
                print("  ERROR: Pickup failure. Re-attempting...") 
                arduino.write(b'6\n')
                printer.startprint(preformPickup) #Moves object to preform gripper.
                while printer.printing:
                    time.sleep(1)
                arduino.write(b'7\n')
                time.sleep(5)          
                arduino.write(b'8\n') #Closes gripper on preform.
                time.sleep(3)
                printer.send_now('G1 Z30') #Moves gripper up 30mm.
                time.sleep(5)
                print("  Confirming Pickup...") 
                printer.startprint(preformView) #Moves back to camera view of preform.
                while printer.printing:
                    time.sleep(1)
                time.sleep(3)
                compCheck = objectDet('preform') #Checks if preform is still in holder.
                if compCheck != 'No Preform Detected.': #If preform is still detected.
                    arduino.write(b'2\n') #Strobes LEDs.
                    res = PPickupErr() #Calls preform pickup error function.
                    while res == 0: #Waits until user inputs a satisfactory input.
                        res = PPickupErr()
                    arduino.write(b'3\n') #Opens grippers.
                    return 'PPickupErr' #Returns pickup error.
                else: #Otherwise, if there are no issues with the pickup.
                    time.sleep(1)
                    arduino.write(b'1\n') #Turns LEDs off.
                    return "correct" #Returns correct pickup.
            else: #Otherwise, if no preform is detected, meaning pickup is sucessful 
                time.sleep(1)
                arduino.write(b'1\n') #Turns LEDs off.
                return "correct" #Returns correct pickup.
            time.sleep(1)
            arduino.write(b'1\n') #Turns LEDs off.
            return "correct" #Returns correct pickup.
        else: #Otherwise, if no object is detected.
            return "PNoObjErr" #Returns no object error.

def place(coords, sec, fVal):
    #Defines the method for placing both the feedthrough and preform components on the assembly bed with only one call.
    #Takes the coordinates for the placement, the time delay between placement and opening the grippers, and the feedthrough error value which is already defined.
    print("  Retrieving Components...")
    printer.startprint(getComponent) #Moves the assembly bed to distribute a preform and feedthrough component.
    while printer.printing:
        time.sleep(1)
    time.sleep(2)
    
    det = pickup('preform') #Calls the pickup function for the preform.
    if fVal == 0: #Check that there is no feedthrough error.
        if det == 'correct': #If the preform has been picked up correctly.
            print("  Placing Preform...")
            printer.send_now('G1 ' + coords) #Moves to feedthrough placement coordinates.
            time.sleep(1)
            printer.send_now('G91') #Changes printer to incremental values.
            time.sleep(1)
            printer.send_now('G1 X-68.5 Y2') #Moves the preform to the place where the feedthrough gripper just was.
            time.sleep(3)
            printer.send_now('G90') #Changes back to absolute values.
            time.sleep(1)
            printer.send_now('G1 Z14') #Moves to 14mm in Z axis.
            time.sleep(sec)
            arduino.write(b'7\n') #Partially opens preform gripper.
            time.sleep(1)
            printer.send_now('G1 Z30') #Moves gripper back up to 30mm in Z axis.
            time.sleep(4)
            arduino.write(b'6\n') #Fully opens preform gripper.
            time.sleep(2)
            print("  Successful Placement.")
        elif det == "PNoObjErr" or det == "PPickupErr": #Otherwise, if there was a preform pickup error or there was no preform.
            det = pickup('feedthrough') #Moves to the feedthrough and picks it up.
            if det == "FSizeErr" or det == "correct": #If feedthrough pickup is successful.
                FDrop(1) #Throws the feedthrough away.
            return "repeat" #Returns try again.
    else: #If there is a feedthrough error.
        if det == 'correct': #If the preform has been correctly picked up.
            PDrop(1) #Throw the deedthrough away.
                   
    det = pickup('feedthrough') #Calls the pickup function for the feedthrough.
    if det == 'correct': #If the feedthrough is correctly picked up.
        print("  Placing Feedthrough...")
        printer.send_now('G1 ' + coords) #Moves feedthrough gripper to placement location.
        printer.send_now('G1 Z15.5') #Moves gripper to Z15.5mm in Z axis.
        time.sleep(sec)
        arduino.write(b'4\n') #Partially opens feedthrough gripper.
        time.sleep(1)
        printer.send_now('G1 Z30') #Moves gripper back up to 30mm in Z axis.
        time.sleep(2)
        arduino.write(b'3\n') #Fully opens feedthrough gripper.
        time.sleep(1)
        print("  Successful Placement.")
        return 'success' #Returns sucessful feedthrough preform placement.
    elif det == "FSizeErr": #If there is a feedthrough size error.
        print("  Throwing Incorrect Feedthrough Away...")
        FDrop(1) #Throws feedthrough away.
    return 'FRepeat' #Returns repeat but with consideration of feedthrough.

def complete():
    #Once the assembly has been complete, the assembler presents the bed to the user, and moves the grippers out of the way.
    printer.send_now('G1 Z30') #Moves gripper up to 30mm in Z axis.
    time.sleep(3)
    printer.send_now('G1 X200 Y160') #Moves gripper to the right and brings assembly bed forward.
    arduino.write(b'3\n') #Opens feedthrough grippers.
    time.sleep(1)
    arduino.write(b'6\n') #Opens preform grippers.
    time.sleep(1)
    arduino.write(b'2\n') #Strobes LEDs.
    print("\nAssembly Complete!")
    sys.exit() #Exits code.

def percentDisp():
    #Displays the percentage of the assemmbly that has been complete, subject to the number of assemblies being assembled.
    global percent #Takes the percentage variable for the function.
    if numberAssem == 1: #Changes the increment in percentage for each preform-feedthrough placement subject to the number of assemblies being assembled.
        percent += 2.3255813953 #Adds the percentage to the total percent complete.
        print("Assembly " + str(round(percent, 2)) + "% Complete") #Writes the rounded value to the assembler screen.
    elif numberAssem == '2':
        percent += 1.1627906977
        print("Assembly " + str(round(percent, 2)) + "% Complete")
    elif numberAssem == '3':
        percent += 0.7751937984
        print("Assembly " + str(round(percent, 2)) + "% Complete")
    elif numberAssem == '4':
        percent += 0.5813953488
        print("Assembly " + str(round(percent, 2)) + "% Complete")

def tManage(Xcoord, Ycoord, sec):
    #Organises the higher level functions of the assembler, takes the coordinates for placement, as well as the delay in distributing components as inputs.
    #Manages the error values of feedthroughs. If a feedthrough is thrown away or not distributed, then the function throws the next preform away after collection.
    Xcoord = str(Xcoord) #Takes coordinates and turns to string.
    Ycoord = str(Ycoord)
    coords = 'X' + Xcoord + ' ' + 'Y' + Ycoord #Places coordinates in correct G-code format.
    outcome = place(coords, sec, 0) #Calls placement function, sending coordinates for placement.
    if outcome == 'repeat': #If the preform collection needs to be repeated.
        outcome = place(coords, sec, 0) #Calls the placement function again.
        if outcome == 'repeat': #If the preform collection still needs to be repeated.
            arduino.write(b'2\n') #Strobes LEDs
            restock = restockP() #Calls the restock preforms function.
            while restock == 0: #Waits for user to input proper response.
                restock == restockP()
            outcome = place(coords, sec, 0) #Calls the placement function again.
            if outcome == 'repeat': #If the preform collection still needs to be repeated.
                arduino.write(b'2\n') #Strobes LEDs.
                fail = AssemFail() #Assembly fail function called.
                while fail == 0: #Waits for user to input proper response.
                    fail = AssemFail()
                complete() #Completes the assembly.
    elif outcome == 'FRepeat': #If feedthrough collection needs to be repeated.
        outcome = place(coords, sec, 1) #Calls the placement function again with the feedthrough flag.
        if outcome == 'FRepeat': #If the feedthrough collection still needs to be repeated.
            arduino.write(b'2\n') #Strobe LEDs.
            restock = restockF() #Calls the restock feedthrough function.
            while restock == 0: #Waits for user to input proper response.
               restock == restockF()
            outcome = place(coords, sec, 1) #Calls the placement function again with the feedthrough flag.
            if outcome == 'FRepeat': #If the feedthrough collection still needs to be repeated.
                arduino.write(b'2\n') #Strobes LEDs.
                fail = AssemFail() #Assembly fail function called.
                while fail == 0: #Waits for user to input proper response.
                    fail = AssemFail() 
                complete() #Completes the assembly.
    percentDisp() #Calls the percentage displat function.
            
def assem1():
    #Function organises the placement for the entire first assembly bed.
    #It increments X axis placement locations until it gets to the end of a row, then it increments the Y axis placement and moves to the start of the next row in the X axis.
    global X
    global Y
    
    #First Row
    tManage(X, Y, 10)    
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    
    #Second Row
    X -= 55 #2nd row start distance in X axis.
    Y += 8.66 #2nd row start row distance in Y axis.
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)

    #Third Row
    X -= 55
    Y += 8.67
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    
    #Fourth Row
    X -= 55
    Y += 8.66
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    
    #Fifth Row
    X -= 55
    Y += 8.67
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    
    #Sixth Row
    X -= 55
    Y += 8.66
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    
    #Seventh Row
    X -= 55
    Y += 8.67
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    
def assem2():
    #Function organises the placement for the entire second assembly bed.
    #Operation is the same as for assem1().
    global X
    global Y

    X -= 30 #Moves to the starting location of assembly bed 2 from the end location of assembly bed 1.
    Y += 44.34
    
    #First Row
    tManage(X, Y, 8)    
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    
    #Second Row
    X -= 55
    Y += 8.66
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)

    #Third Row
    X -= 55
    Y += 8.67
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    
    #Fourth Row
    X -= 55
    Y += 8.66
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    
    #Fifth Row
    X -= 55
    Y += 8.67
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    
    #Sixth Row
    X -= 55
    Y += 8.66
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    
    #Seventh Row
    X -= 55
    Y += 8.67
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    

def assem3():
    #Function organises the placement for the entire third assembly bed.
    #Operation is the same as for assem1().
    global X
    global Y

    X += 66.3
    Y -= 52
    
    #First Row
    tManage(X, Y, 8)    
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    
    #Second Row
    X -= 55
    Y += 8.66
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)

    #Third Row
    X -= 55
    Y += 8.67
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    
    #Fourth Row
    X -= 55
    Y += 8.66
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    
    #Fifth Row
    X -= 55
    Y += 8.67
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    
    #Sixth Row
    X -= 55
    Y += 8.66
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    
    #Seventh Row
    X -= 55
    Y += 8.67
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)

def assem4():
    #Function organises the placement for the entire fourth assembly bed.
    #Operation is the same as for assem1().
    global X
    global Y

    X -= 30
    Y -= 148.34
    
    #First Row
    tManage(X, Y, 8)    
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    
    #Second Row
    X -= 55
    Y += 8.66
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)

    #Third Row
    X -= 55
    Y += 8.67
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    
    #Fourth Row
    X -= 55
    Y += 8.66
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    
    #Fifth Row
    X -= 55
    Y += 8.67
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    
    #Sixth Row
    X -= 55
    Y += 8.66
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    
    #Seventh Row
    X -= 55
    Y += 8.67
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)
    X += 10
    tManage(X, Y, 8)

def calMove(coords):
    #Moves to the required coordinates specified during calibration mode - Takes the coordinates as an input.
    printer.send_now('G1 ' + coords) #Moves to the coordinates send.
    printer.send_now('G1 Z23') #Moves to 23mm in the Z axis.
    time.sleep(1)

def calibrate():
    #Calibration function. Pickups up a feedthrough and places it at the starting coordinates for user to determine if starting coordinated need to be changed. 
    global X
    global Y
    
    Xcoord = str(X)
    Ycoord = str(Y)
    coords = 'X' + Xcoord + ' ' + 'Y' + Ycoord
    
    inserted = feedIns() #Calls insert feedthrough function.
    while inserted == 0: #Waits for proper response.
        inserted = feedIns()
        
    print("  Retrieving Feedthrough...")
    printer.startprint(getComponent) #Picks up feedthrough.
    while printer.printing:
        time.sleep(1)
    time.sleep(2)
    det = pickup('feedthrough')
    if det == "FSizeErr" or det == "correct": #If a feedthrough has been properly picked up.
        calMove(coords) #Moves to starting coordinates.
        time.sleep(4)
        print("  Current X starting coord is: " + Xcoord + "mm") #Prints current X coordinate.
        insert = Xadj() #Reads adjusted amount.
        while insert == 'i': #Waits to proper response.
            insert = Xadj()
        while insert != 'y': #While there are adjustments being made.
            if insert <= 60: #Sets boundaries for the adjustment.
                insert = 60
            elif insert >= 65:
                insert = 65
            X = insert #Sets X starting value to input value.
            Xcoord = str(X)
            coords = 'X' + Xcoord + ' ' + 'Y' + Ycoord 
            calMove(coords) #Moves gripper to new value.
            print("  Current X starting coord is: " + Xcoord + "mm")
            insert = Xadj() #Confirms if further adjustments are still to be made.
            while insert == 'i':
                insert = Xadj()
        
        print("  Current Y starting coord is: " + Ycoord + "mm") #Performs the same operation for the Y axis as for the X.
        insert = Yadj()
        while insert == 'i':
            insert = Yadj()
        while insert != 'y':
            if insert <= 10:
                insert = 10
            elif insert >= 15:
                insert = 15
            Y = insert
            Ycoord = str(Y)
            coords = 'X' + Xcoord + ' ' + 'Y' + Ycoord
            calMove(coords)
            print("  Current Y starting coord is: " + Ycoord + "mm")
            insert = Yadj()
            while insert == 'i':
                insert = Yadj()
        printer.send_now('G1 Z30') #Moves the gripper back up to 30mm in the Z acis.
        time.sleep(3)
        FDrop(1) #Throws the feedthrough away.
        arduino.write(b'3\n') #Opens the feedthrough gripper.
        time.sleep(1)
        printer.send_now('G1 X140') #Moves the gripper out of the way of the screen.
        time.sleep(3)
        print("  Calibration complete.")
        
        startCoords.update({'X': X, 'Y': Y}) #Sets the starting location.

        #Saves the starting location to a file.
        outfile = open(filename, 'wb')
        pickle.dump(startCoords,outfile)
        outfile.close()
    else:
        print("  ERROR: Calibration failure, continuing assembly.") #If there was an issue with the feedthrough distribution or pickup, exits calibration.
    return

time.sleep(3)

arduino.write(b'2\n') #Strobes LEDs
print("\nPlease do not load assembly components until instructed.\n")
numberAssem = start() #Prompts user for number of assemblies to be completed.
while numberAssem == 0:
    numberAssem = start()
    
time.sleep(1)

printer.startprint(home) #Homes printer.
while printer.printing:
    time.sleep(1)
printer.send_now('G1 F1600 Z30')
time.sleep(3)
printer.send_now('G1 X140 Y20 Z30') #Moves grippers out of the way.
time.sleep(8)
arduino.write(b'6\n') #Opens preform grippers.
time.sleep(8)

arduino.write(b'2\n')
calVal = calib() #Checks if the user wishes to enter calibration mode.
while calVal == 0:
    calVal = calib()
if calVal == 1:
    calibrate()

arduino.write(b'2\n')
ready = insert() #Prompts the user to insert feedthroughs and preforms.
while ready == 0:
    ready = insert()
    
assem1() #Calls the assembly functions subject to the number of asssemblies specified by the user.
if numberAssem > 1:
    assem2()
    if numberAssem > 2:
        assem3()
        if numberAssem > 3:
            assem4()
complete() #Once complete, finished assembly process.
