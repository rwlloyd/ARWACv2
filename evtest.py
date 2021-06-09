from evdev import InputDevice, categorize, ecodes
dev = InputDevice('/dev/hidraw0') #/input/event0')

print(dev)
#device /dev/input/event1, name "Dell Dell USB Keyboard", phys "usb-0000:00:12.1-2/input0"

for event in dev.read_loop():
    #print(event)
    if event.type == ecodes.EV_KEY:
        #if event.value == 1:
        print(event.code)
        #print((categorize(event).keycode))
        #
        # print((categorize(event).scancode))
#if event.type == ecodes.EV_KEY:
     #   print(event)
