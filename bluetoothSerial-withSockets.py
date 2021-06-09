#!/usr/bin/env python3
import serial
import math
from time import sleep
import PG9038S as bt
import subprocess as sp

from rassocketcom import CJetScketUDPSever

m_CJetCom = CJetScketUDPSever()

print("    Differential Drive Remote Control for Serial-Curtis Bridge v1.3 and Generic Bluetooth Controller")
print("    Usage: Left or Right Trigger = Toggle Enable; Left Joystick for left wheels motion and Right Joystick for right wheels motion")
print("    Usage: estop enable = either joystick buttons, cancel estop = both bumper buttons")

controllerMAC = "FB:D4:CA:25:8F:F9" # change to unique MAC address of bluetooth controller

# creates an object for the serial port
try:
    arduinoData = serial.Serial("/dev/ttyUSB0", 115200, timeout=1)
except:
    print("Arduino Failed to connect")
    pass

# So the direction in general can be reversed
direction = False

message = []  # Seems to be necessary to have a placeholder for the message here
last_message = []

# creates an object for the bluetooth control
controller = bt.PG9038S("/dev/input/event1")

# Initialise  values for enable and estop
estopState = False
enable = False
left_y = 128
right_y = 128

## Functions -----------------------------------------------------------------------

def rescale(val, in_min, in_max, out_min, out_max):
    """
    Function to mimic the map() function in processing and arduino.
    """
    return out_min + (val - in_min) * ((out_max - out_min) / (in_max - in_min))

def generateMessage(estopState, enable, right_vel, left_vel):
    """
    Accepts an input of two bools for estop and enable. 
    Then two velocities for right and left wheels between -100 and 100
    """
    # Empty list to fill with our message
    messageToSend = []
    # # Check the directions of the motors, False (0) = (key switch) forward, True (1) = reverse
    # # Velocities are scaled from -100 to +100 with 0 (middle of joystick) = no movement
    # # If vel >= 0 = forward, if vel < 0 backward
    
    if left_vel >= 0:
        left_direction = False
    elif left_vel < 0:
        left_direction = True
    if right_vel >= 0:
        right_direction = False
    elif right_vel < 0:
        right_direction = True

    # Check to see if we're allowed to move. estop and enable
    if estopState or not enable:
        left_vel = 0
        right_vel = 0

    # Build the message. converting everything into positive integers
    # Message is 10 bits [estopState, enable, motor 0 direction, motor 0 velocity, motor 1 direction, motor 1 velocity, motor 2 direction, motor 2 velocity, motor 3 direction, motor 3 velocity]
    # motor numbering:
    #  Front    
    # 0  1
    # 2  3
    # Back (key end)

    messageToSend.append(int(estopState))
    messageToSend.append(int(enable))
    messageToSend.append(int(left_direction))
    messageToSend.append(abs(int(left_vel)))
    messageToSend.append(int(right_direction))
    messageToSend.append(abs(int(right_vel)))
    messageToSend.append(int(left_direction))
    messageToSend.append(abs(int(left_vel)))
    messageToSend.append(int(right_direction))
    messageToSend.append(abs(int(right_vel)))
    
    print("Sending: %s" % str(messageToSend))
    return messageToSend

def send(message_in):
    """
    Function to send a message_in made of ints, convert them to bytes and then send them over a serial port
    message length, 10 bytes.
    """
    messageLength = 10
    message = []
    for i in range(0, messageLength):
        message.append(message_in[i].to_bytes(1, 'little'))
    for i in range(0, messageLength):
        arduinoData.write(message[i])
    #print(message)

def receive():
    """
    Function to read whatever is presented to the serial port and print it to the console.
    Note: For future use: Currently not used in this code.
    """
    messageLength = len(message)
    last_message = []
    try:
        while arduinoData.in_waiting > 0:
            for i in range(0, messageLength):
                last_message.append(int.from_bytes(arduinoData.read(), "little"))
        #print("GOT: ", last_message)
        return last_message
    except:
        print("Failed to receive serial message")
        pass


def socket_receive_camera():
     ############################################
    # socket communication - dom
    # Check to see if there is new input from the external, TX2
    msg = {}
    try:

        msg = m_CJetCom.RasReceive_data()       
        
        print('Recieved data: ', msg)
        return msg        
        

        """
        msg = m_CJetCom.RasReceive()
        if msg[0]['L']==1:
            return msg[0]['L']
        elif msg[0]['R']==1:
            return msg[0]['L']

        else:
            return msg[0]['L']        

        print('Recieved data: ', msg[0]['L'])
        """
        # plt.pause(0.25)
    except IOError:
        return msg.clear() # error so return empty message
        pass
    ############################################
    ############################################


# Main Loop
while True:
    stdoutdata = sp.getoutput("hcitool con") # hcitool check status of bluetooth devices

    # check bluetooth controller is connected if not then estop
    if controllerMAC not in stdoutdata.split():
        print("Bluetooth device is not connected")
        estopState = True

    # read inputs
    try:
        newStates = controller.readInputs()
    except IOError:
        pass

    #last_message = receive()
    #print(last_message)

    # enable = bool(newStates["trigger_l_1"])# Dead mans switch left trigger button

    # reset after estop
    # left and right bumper buttons
    if newStates["trigger_l_1"] == 1 and newStates["trigger_r_1"] == 1:
        estopState = False

    # left and right joystick buttons
    if newStates["button_left_xy"] == 1 or newStates["button_right_xy"] == 1:
        estopState = True
    
    if estopState == True:
        enable = False

    # dead mans switch left or right trigger button
    if newStates["trigger_l_2"] == 1 or newStates["trigger_r_2"] == 1:
        if estopState == False:
            enable = True
    else:
        enable = False

    if enable == True: 
        # Reverse direction respect to joysticks e.g. left up = right reverse
        left_y = newStates["right_y"] # Right joystick up / down == left velocity
        right_y = newStates["left_y"] # Left joystick up / down == right velocity
    
        # Calculate the final velocities rescaling the absolute value to between -100 and 100
        left_vel = rescale(left_y, 255,0,-100,100)
        right_vel = rescale(right_y, 255,0,-100,100)

        # This feels hacky..... 
        # 1/8 sec (125 ms) slowest "frame rate" / data rate from Doms code to get robot moving
        if newStates["button_b"] == 1: # if enabled and B button pressed enter row rollowing mode
            left_vel = 31
            right_vel = 30
            #print("button b pressed")
            try:
                message = socket_receive_camera()
                #print("message" + str(message))
            except:
                print("what message?")
                pass
            #print("row following mode")
            if bool(message): # if message is not empty drive, else stop
                currentMessage = float(message)
                fudge = 30
                if currentMessage == 0:
                    pass
                elif currentMessage > 0: # robot is reversed so swap left/right, so Doms number > 0 steer right, < 0 steer left
                    right_vel += fudge * abs(currentMessage)
                elif currentMessage < 0:
                    left_vel += fudge * abs(currentMessage)
        
        if newStates["button_x"] == 1:
            left_vel = 30
            right_vel = 30

            currentMessage = 0
            fudge = 30

            if currentMessage == 0:
                pass
            elif currentMessage > 0: # robot is reversed so swap left/right, so Doms number > 0 steer right, < 0 steer left
                right_vel += fudge * abs(currentMessage)
            elif currentMessage < 0:
                left_vel += fudge * abs(currentMessage)


    # motor numbering:
    #  Front (key end) 
    # 3  2
    # 1  0
    # Back


            
    else:
        right_y = 128 # Right joystick up / down = 128 == 0 motor stop
        left_y = 128 # Left joystick up / down = 128 == 0 motor stop

        # Calculate the final velocities rescaling the absolute value to between -100 and 100
        left_vel = 0
        right_vel = 0

    # Build a new message with the correct sequence for the Arduino
    new_message = generateMessage(int(estopState), int(enable), right_vel, left_vel)
    #print(int(estopState), int(enable), right_vel, left_vel)
    # Send the new message
    send(new_message)
    # So that we don't keep spamming the Arduino....
    sleep(0.05)