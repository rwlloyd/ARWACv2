#!/usr/bin/env python3

from evdev import InputDevice, categorize, ecodes

en = False

# creates object 'gamepad' to store the data
gamepad = InputDevice('/dev/input/event0')

# # button code variables (must change to suit input device)
aBtn = 304

def rescale(val, in_min, in_max, out_min, out_max):
    """
    Function to mimic the map() function in processing and arduino.
    """
    return out_min + (val - in_min) * ((out_max - out_min) / (in_max - in_min))

def checkButtons():
    enable = False
    activeKeys = gamepad.active_keys(verbose = False)
    if len(activeKeys) > 0:
        for key in activeKeys:
            if key == aBtn:
                enable = True
                return enable
                #print("Enabled")
            else:
                enable = False
                return enable
                #print("Disabled")
    else:
        enable = False
        #print("NoActiveKeys")
        return enable

def getInputs():
    """
    Gets inputs from the input device and converts to -1 -> 1 values for linear_vel (Y axis) and angular_vel(xAxis)
    """
# loop and filter by event code and print the mapped label
# https://gist.github.com/projetsdiy/63e42eb6d9f0755be9c2e67ae903d413
    for event in gamepad.read_loop():
        if event.type == ecodes.EV_ABS:
            absevent = categorize(event)
            #print(ecodes.bytype[absevent.event.type][absevent.event.code], absevent.event.value)
            if ecodes.bytype[absevent.event.type][absevent.event.code] == "ABS_X":
                x_raw = event.value
                return x_raw, None
                continue
            elif ecodes.bytype[absevent.event.type][absevent.event.code] == "ABS_Y":
                y_raw = event.value
                return None, y_raw  


############ Main Loop ##############################################################
# Initialise values to fail safe and not throw an error
x_in = 127
y_in = 127

while True:
    en = checkButtons()
    events = gamepad.read_loop()
    #x_in = getX(events)
    #y_in = getY(events)
    x_new, y_new = getInputs()
    if x_new is None:
        y_in = y_new
    elif y_new is None:
        x_in = x_new
    if en is False:
        x_in = 128/2
        y_in = 127
    x = rescale(x_in, 0,128,-1,1)
    y = rescale(y_in, 255,0,-1,1)
    # Do Something
    print(en, x, y)
