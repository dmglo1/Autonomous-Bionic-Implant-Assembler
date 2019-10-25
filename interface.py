import sys

def start():
    #Prompts the user to enter the number of assemblies to be completed, then returns this value. Only accepts inputs of 1,2,3 or 4.
    start = input("Please enter the number of assebmlies to be completed (1 to 4): ") #Prompts the user to input a value.
    if start == '1': #Checks if the value is 1.
        print("  " + start + " assembly will be completed.") #Prints the number of assemblies to be completed to the user to confirm.
        return 1
    elif start == '2':
        print("  " + start + " assemblies will be completed.")
        return 2
    elif start == '3':
        print("  " + start + " assemblies will be completed.")
        return 3
    elif start == '4':
        print("  " + start + " assemblies will be completed.")
        return 4
    else: #If the user doesn't input 1,2,3 or 4, will prompt the user to reenter. 
        print("  Invalid input, re-enter.")
        return 0

def insert():
    #Prompts the user to place the preforms and feedthroughs into the distribution funnels and to enter 'y' when this is complete.
    #Operates similar to start() function.
    insert = input("Please insert components into funnels (Enter 'y' to continue): ")
    if insert == 'y':
        print("  Commencing Assembly...")
        return 1
    else:
        print("  Invalid input, re-enter.")
        return 0

def FPickupErr():
    #Prompts the user to check the feedthrough gripper pickup processes to remove fault and to enter 'y' when this is complete.
    #Operates similar to start() function.
    insert = input("  ERROR: An Error with the Feedthrough Gripper has been detected, please manually remove the feedthrough (Enter 'y' when resolved):  ")
    if insert == 'y':
        print("  Continuing assembly...")
        return 1
    else:
        print("  Invalid input, re-enter.")
        return 0
    
def PPickupErr():
    #Prompts the user to check the preform gripper pickup processes to remove fault and to enter 'y' when this is complete.
    #Operates similar to start() function.
    insert = input("  ERROR: An Error with the Preform Gripper has been detected, please manually remove the preform (Enter 'y' when resolved):  ")
    if insert == 'y':
        print("  Continuing assembly...")
        return 1
    else:
        print("  Invalid input, re-enter.")
        return 0

def AssemFail():
    #Informs the user that the assembly process has failed and to enter 'y' when this is understood to complete the assembly.
    #Operates similar to start() function.
    insert = input(" ERROR: An irresolvable error has occured, the assembly will now finish (Enter 'y' to continue):  ")
    if insert == 'y':
        print("  Concluding failed assembly...")
        return 1
    else:
        print("  Invalid input, re-enter.")
        return 0

def restockF():
    #Prompts the user to check the feedthrough distribution to remove fault  or to restock components and to enter 'y' when this is complete.
    #Operates similar to start() function.
    insert = input(" ERROR: An error has occured with feedthrough distribution, please check that there are feedthroughs avaiable (Enter 'y' to continue):  ")
    if insert == 'y':
        print("  Continuing assembly...")
        return 1
    else:
        print("  Invalid input, re-enter.")
        return 0

def restockP():
    #Prompts the user to check the preform distribution to remove fault  or to restock components and to enter 'y' when this is complete.
    #Operates similar to start() function.
    insert = input(" ERROR: An error has occured with preform distribution, please check that there are feedthroughs avaiable (Enter 'y' to continue):  ")
    if insert == 'y':
        print("  Continuing assembly...")
        return 1
    else:
        print("  Invalid input, re-enter.")
        return 0

def calib():
    #Asks the user whether or not to enter calibration mode and to enter 'y' if this is the case, otherwise to enter 'n'.
    #Operates similar to start() function.
    insert = input("  Would you like to enter calibration mode (Enter 'y'/'n' to continue): ")
    if insert == 'y':
        print("  Commencing calibration...")
        return 1
    elif insert == 'n':
        print("  Skipping calibration...")
        return 2
    else:
        print("  Invalid input, re-enter.")
        return 0

def feedIns():
    #Prompts the user to place a single feedthrough in the feedthrough distribution funnel as part of the calibration process and to enter 'y' when this is complete.
    #Operates similar to start() function.
    insert = input("  Please insert 1 feedthrough into the feedthrough distribution funnel only (Enter 'y' to continue): ")
    if insert == 'y':
        print("  Continuing calibration...")
        return 1
    else:
        print("  Invalid input, re-enter.")
        return 0
    
def Xadj():
    #Prompts the user to enter a new starting X value and to enter 'y' when if no change is needed and this is complete.
    #Operates similar to start() function.
    insert = input("  Input new X start coord (between 60 and 65mm to 2 decimal places) or 'y' to exit: ")
    if insert == 'y':
        print("  Continuing calibration...")
        return 'y'
    else:
        try:
           val = float(insert) #Floats the user input variable.
        except ValueError: #If the user has not inputted a numerical value, then results in error.
           print("  Invalid input, re-enter.")
           return 'i'
        return val
    
def Yadj():
    #Prompts the user to enter a new starting Y value and to enter 'y' when if no change is needed and this is complete.
    #Operates similar to start() function.
    insert2 = input("  Input new Y start coord (between 10 and 15mm to 2 decimal places) or 'y' to exit: ")
    if insert2 == 'y':
        print("  Continuing calibration...")
        return 'y'
    else:
        try:
           val2 = float(insert2)
        except ValueError:
           print("  Invalid input, re-enter.")
           return 'i'
        return val2
