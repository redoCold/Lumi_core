from Lumi_hub.commands import LumiHub
import keyboard
import time

lumi = LumiHub('COM12') # Change to your port ok

print("Lumi is Ready!")
print("WASD to drive | Z/X for Arms | Q/E for Neck | R to Stop")

def greet():
    print("Lumi says hello!")
    lumi.look(512)
    lumi.sync_arms(300)
    time.sleep(0.5)
    lumi.sync_arms(700)
    time.sleep(0.5)
    lumi.sync_arms(512)

while True:
    if keyboard.is_pressed('w'):
        lumi.sync_drive(200) 
    elif keyboard.is_pressed('s'):
        lumi.sync_drive(-200)
    elif keyboard.is_pressed('a'):
        lumi.drive(-150, -150)
    elif keyboard.is_pressed('d'):
        lumi.drive(150, 150)
    elif keyboard.is_pressed('r'):
        lumi.stop()
    else:
        lumi.drive(0, 0)
    # --- Arms ---
    if keyboard.is_pressed('z'):
        lumi.arm_cross()
    elif keyboard.is_pressed('x'):
        lumi.arm_opposite()
    # --- neck ---
    if keyboard.is_pressed('q'):
        lumi.look(300)
    elif keyboard.is_pressed('e'):
        lumi.look(700)
    # --- delay ---
    time.sleep(0.05)