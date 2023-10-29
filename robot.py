from machine import Pin
import time
from servo import Servo

import aioble
import bluetooth
import machine
import uasyncio as asyncio

# Bluetooth UUIDS can be found online at https://www.bluetooth.com/specifications/gatt/services/
_REMOTE_UUID = bluetooth.UUID(0x1848)
_ENV_SENSE_UUID = bluetooth.UUID(0x1800) 
_REMOTE_CHARACTERISTICS_UUID = bluetooth.UUID(0x2A6E)

# Pico onboard LED for bluetooth connectivity indication
led = machine.Pin("LED", machine.Pin.OUT)
connected = False
alive = False

wrist_led = Pin(16, Pin.OUT)
wrist_led.value(0)

# Finger Servo Pin Definitions
ib = 8
im = 11
it = 7

mb = 2
mm = 0
mt = 6

rb = 4
rm = 5
rt = 3

pb = 10
pm = 9
pt = 1

tb = 12
tm = 13
tt = 14

# Knuckles servo Pin definition
w = 15

# Create servo objects for all the joints
# Index Finger
i_b = Servo(pin_id=ib)
i_m = Servo(pin_id=im)
i_t = Servo(pin_id=it)
# Middle Finger
m_b = Servo(pin_id=mb)
m_m = Servo(pin_id=mm)
m_t = Servo(pin_id=mt)
# Ring FInger
r_b = Servo(pin_id=rb)
r_m = Servo(pin_id=rm)
r_t = Servo(pin_id=rt)
# Pinky 
p_b = Servo(pin_id=pb)
p_m = Servo(pin_id=pm)
p_t = Servo(pin_id=pt)
# Thumb
t_b = Servo(pin_id=tb)
t_m = Servo(pin_id=tm)
t_t = Servo(pin_id=tt)
# Knuckles
wrt = Servo(pin_id=w)

delay_ms = 20


async def find_remote():
    # Scan for 5 seconds, in active mode, with very low interval/window (to
    # maximise detection rate).
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:

            # See if it matches our name
            if result.name() == "TheThing":
                print("Found The_Thing")
                for item in result.services():
                    print (item)
                if _ENV_SENSE_UUID in result.services():
                    print("Found Robot Remote Service")
                    return result.device
            
    return None

async def blink_task():
    """ Blink the LED on and off every second """
    
    toggle = True
    
    while True and alive:
        led.value(toggle)
        toggle = not toggle
        # print(f'blink {toggle}, connected: {connected}')
        if connected:
            blink = 1000
        else:
            blink = 250
        await asyncio.sleep_ms(blink)

async def peripheral_task():
    print('starting peripheral task')
    global connected
    connected = False
    device = await find_remote()
    if not device:
        print("Robot Remote not found")
        return
    try:
        print("Connecting to", device)
        connection = await device.connect()
        
    except asyncio.TimeoutError:
        print("Timeout during connection")
        return
      
    async with connection:
        print("Connected")
        connected = True
        alive = True
        while True and alive:
            try:
                robot_service = await connection.service(_REMOTE_UUID)
                print(robot_service)
                control_characteristic = await robot_service.characteristic(_REMOTE_CHARACTERISTICS_UUID)
                print(control_characteristic)
            except asyncio.TimeoutError:
                print("Timeout discovering services/characteristics")
                return
            while True:
                if control_characteristic != None:
                    try:
                        command = await control_characteristic.read()
                        if command == b'r':
                            print("a button pressed")
                            crouch_pos()
                        if command == b'b':
                            print("b button pressed")
                            get_up()
                        if command == b'g':
                            print("x button pressed")
                            finger_stamp()
                        if command == b'y':
                            print("y button pressed")
                            point_finger()
                        if command == b'w':
                            print("y button pressed")
                            bow_down()
                        if command == b'k':
                            print("y button pressed")
                            rise_up()
                        if command == b'x':
                            print("y button pressed")
                            crouch_walk_forward()
                        if command == b'z':
                            print("y button pressed")
                            crouch_walk_backward()
                        if command == b'v':
                            print("y button pressed")
                            stand_walk()
                    except TypeError:
                        print(f'something went wrong; remote disconnected?')
                        connected = False
                        alive = False
                        return
                    except asyncio.TimeoutError:
                        print(f'something went wrong; timeout error?')
                        connected = False
                        alive = False
                        return
                    except asyncio.GattError:
                        print(f'something went wrong; Gatt error - did the remote die?')
                        connected = False
                        alive = False
                        return
                else:
                    print('no characteristic')
                await asyncio.sleep_ms(10)

async def main():
    tasks = []
    tasks = [
        asyncio.create_task(blink_task()),
        asyncio.create_task(peripheral_task()),
    ]
    await asyncio.gather(*tasks)

def wrist_led_seq():
    wrist_led.value(0)
    time.sleep(2)
    wrist_led.value(0)
    for i in range (3):
        wrist_led.value(1)
        time.sleep(0.1)
        wrist_led.value(0)
        time.sleep(0.1)
    wrist_led.value(1)

def straight_fingers():
    i_b.write(76)
    i_m.write(15)
    i_t.write(55)

    m_b.write(87)
    m_m.write(44)
    m_t.write(58)

    r_b.write(85)
    r_m.write(35)
    r_t.write(60)

    p_b.write(88)
    p_m.write(45)
    p_t.write(45)
    
    t_b.write(88)
    t_m.write(48)
    t_t.write(78)
    
    time.sleep(1)
   
def rise_up():
    straight_fingers()
    time.sleep(2)

    t_b.write(84)
    t_m.write(80)
    t_t.write(170)
    time.sleep(2)

    t_b.write(84-50)
    t_m.write(48+100)
    time.sleep(1)
    t_b.write(88-50)
    t_m.write(48+70)
    t_t.write(78+52)
    time.sleep(1)

    t_b.write(88-60)
    t_m.write(48+90)
    t_t.write(78+52)

    time.sleep(0.5)

    i_b.write(76-20)
    i_m.write(15)
    i_t.write(55)
    time.sleep(1)
    m_b.write(87-20)
    m_m.write(44)
    m_t.write(58)

    r_b.write(85-20)
    r_m.write(35)
    r_t.write(60)

    p_b.write(88-20)
    p_m.write(45)
    p_t.write(45)

    time.sleep(1)

    t_b.write(88-4)
    t_m.write(48+125)
    t_t.write(78-32)
    time.sleep(1)
    p_b.write(88-27)
    p_m.write(45+30)
    p_t.write(45+87)
    time.sleep(1)
    i_b.write(76-27)
    i_m.write(15+30)
    i_t.write(55+87)

    m_b.write(87-27)
    m_m.write(44+30)
    m_t.write(58+87)

    r_b.write(85-27)
    r_m.write(35+30)
    r_t.write(60+87)

    time.sleep(1)
    p_b.write(88-12)
    p_m.write(45+104)
    p_t.write(45-2)

    t_b.write(88-4)
    t_m.write(48+125)
    t_t.write(78-32)

    time.sleep(1)
    r_b.write(85-12)
    r_m.write(35+104)
    r_t.write(60-2)
    time.sleep(1)
    m_b.write(87-12)
    m_m.write(44+104)
    m_t.write(58-2)
    time.sleep(1)
    i_b.write(76-12)
    i_m.write(15+104)
    i_t.write(55-2)

    time.sleep(1)

    crouch_pos()
    time.sleep(1)
    crouch_walk_backward(steps=1)

    time.sleep(1)
    t_b.write(88-6)
    t_m.write(48+145)
    t_t.write(78-10)
    time.sleep(1)
    get_up()

def finger_stamp():
    for i in range(10):
        i_b.write(76-4)
        i_m.write(15+125)
        i_t.write(55-32)
        time.sleep(0.1)
        i_b.write(76-63)
        i_m.write(15+138)
        i_t.write(55+15)
        time.sleep(0.1)
        i_b.write(76-12)
        i_m.write(15+104)
        i_t.write(55-2)

        m_b.write(87-4)
        m_m.write(44+125)
        m_t.write(58-32)
        time.sleep(0.1)
        m_b.write(87-63)
        m_m.write(44+138)
        m_t.write(58+15)
        time.sleep(0.1)
        m_b.write(87-12)
        m_m.write(44+104)
        m_t.write(58-2)

        r_b.write(85-4)
        r_m.write(35+125)
        r_t.write(60-32)

        p_b.write(88-4)
        p_m.write(45+125)
        p_t.write(45-32)

        t_b.write(88-4)
        t_m.write(48+125)
        t_t.write(78-32)

def get_up():
    i_b.write(76-4)
    i_m.write(15+125)
    i_t.write(55-32)
    
    m_b.write(87-4)
    m_m.write(44+125)
    m_t.write(58-32)

    r_b.write(85-4)
    r_m.write(35+125)
    r_t.write(60-32)

    p_b.write(88-4)
    p_m.write(45+125)
    p_t.write(45-32)

    t_b.write(88-4)
    t_m.write(48+125)
    t_t.write(78-32)
    
    time.sleep(2)
    
    m_b.write(87+59)
    m_m.write(44+60)
    m_t.write(58-29)

    r_b.write(85+59)
    r_m.write(35+60)
    r_t.write(60-29)

    p_b.write(88+59)
    p_m.write(45+60)
    p_t.write(45-29)
    
    t_b.write(88+59)
    t_m.write(48+60)
    t_t.write(78-29)
        
    i_b.write(76+59)
    i_m.write(15+60)
    i_t.write(55-29)
    
def point_finger(point_count=4):
    m_b.write(87+59)
    m_m.write(44+60)
    m_t.write(58-29)

    r_b.write(85+59)
    r_m.write(35+60)
    r_t.write(60-29)

    p_b.write(88+59)
    p_m.write(45+60)
    p_t.write(45-29)

    t_b.write(88+59)
    t_m.write(48+60)
    t_t.write(78-29)
        
    i_b.write(76+59)
    i_m.write(15+60)
    i_t.write(55-29)
    # time.sleep(2)
    for i in range(point_count):
        i_b.write(76-59)
        i_m.write(15+119)
        i_t.write(55+20)
        time.sleep(0.2)
        i_b.write(76+10)
        i_m.write(15)
        i_t.write(55+20)
        time.sleep(0.3)
    time.sleep(1)
    i_b.write(76+59)
    i_m.write(15+60)
    i_t.write(55-29)
    
def struggle():
    i_b.write(76-28)
    i_m.write(15+47)
    i_t.write(55+37)

    m_b.write(87-28)
    m_m.write(44+47)
    m_t.write(58+37)

    r_b.write(85-28)
    r_m.write(35+47)
    r_t.write(60+37)

    p_b.write(88-28)
    p_m.write(45+47)
    p_t.write(45+37)

    t_b.write(88-28)
    t_m.write(48+47)
    t_t.write(78+37)

    for i in range(48, 140):
        i_b.write(i)
        m_b.write(i)
        r_b.write(i)
        p_b.write(i)
        t_b.write(i)
        time.sleep(0.01)
    for i in reversed(range(48, 140)):
        i_b.write(i)
        m_b.write(i)
        r_b.write(i)
        p_b.write(i)
        t_b.write(i)
        time.sleep(0.01)
    
def bow_down(bowTime=2):
    get_up()
    time.sleep(2)
    wrt.write(90)
    time.sleep(0.5)
    
    for i in range(26,155):
        i_t.write(i)
        time.sleep(0.01)
    for i in reversed(range(35,75)):
        i_m.write(i)
        time.sleep(0.02)
    
    for i in range(29,158):
        m_t.write(i)
        time.sleep(0.01)
    for i in reversed(range(64,104)):
        m_m.write(i)
        time.sleep(0.02)
 
    time.sleep(1)

    for i in range(144,175):
        r_b.write(i)
        time.sleep(0.02)
    for i in range(95,105):
        r_m.write(i)
        time.sleep(0.02)
    for i in range(31,90):
        r_t.write(60+30)
        time.sleep(0.02)
    
    time.sleep(bowTime)
    get_up()
    
def tap_fingers(tapCount=8,tapSpeed=0.05):
    for i in range(tapCount):
        t = tapSpeed
        i_t.write(55+80)
        i_m.write(15+37)
        i_b.write(76-47)

        time.sleep(t)

        m_t.write(58+80)
        m_m.write(44+37)
        m_b.write(87-47)

        time.sleep(t)

        r_t.write(60+80)
        r_m.write(35+37)
        r_b.write(85-47)

        time.sleep(t)

        p_t.write(45+80)
        p_m.write(45+37)
        p_b.write(88-47)

        time.sleep(t)

        i_b.write(76-25)
        i_m.write(15+25)
        i_t.write(55+70)

        time.sleep(t)

        m_b.write(87-25)
        m_m.write(44+25)
        m_t.write(58+70)

        time.sleep(t)

        r_b.write(85-25)
        r_m.write(35+25)
        r_t.write(60+70)

        time.sleep(t)

        p_b.write(88-25)
        p_m.write(45+25)
        p_t.write(45+70)
              
def trick_or_treat():
    for i in range(2):
        i_b.write(76+10)
        i_m.write(15+20)
        i_t.write(55+20)

        m_b.write(87+10)
        m_m.write(44+40)
        m_t.write(58+20)

        r_b.write(85+10)
        r_m.write(35+50)
        r_t.write(60+20)

        p_b.write(88+10)
        p_m.write(45+70)
        p_t.write(45+20)

        t_b.write(88+10)
        t_m.write(48+20)
        t_t.write(78+20)

        time.sleep(2)

        i_b.write(76+80)
        i_m.write(15+30)
        i_t.write(55+65)

        m_b.write(87+80)
        m_m.write(44+30)
        m_t.write(58+60)

        r_b.write(85+80)
        r_m.write(35+35)
        r_t.write(60+60)

        p_b.write(88+90)
        p_m.write(45+35)
        p_t.write(45+60)

        t_b.write(88+60)
        t_m.write(48+40)
        t_t.write(78+80)
        
        time.sleep(2)

    i_b.write(76+10)
    i_m.write(15+20)
    i_t.write(55+20)

    for i in range(3):
        for i in reversed(range(35, 55)):
            i_m.write(i)
            time.sleep(0.003)
        for i in reversed(range(75, 120)):
            i_t.write(i)
            time.sleep(0.003)

        time.sleep(0.1)
        for i in range(75, 120):
             i_t.write(i)
             time.sleep(0.003)
        for i in range(35, 55):
            i_m.write(i)
            time.sleep(0.003)

def _initial():  # Private function used in the finger_count function
    i_b.write(76+60)
    i_m.write(15+70)
    i_t.write(55+80)

    m_b.write(87+60)
    m_m.write(44+70)
    m_t.write(58+80)

    r_b.write(85+60)
    r_m.write(35+70)
    r_t.write(60+80)

    p_b.write(88+60)
    p_m.write(45+70)
    p_t.write(45+75)

    t_b.write(88+60)
    t_m.write(48+70)
    t_t.write(78+80)


def finger_count():
    _initial()
    time.sleep(1)

    i_b.write(76+60)
    i_m.write(15+30)
    i_t.write(55+10)

    time.sleep(1)
    for i in range(3):    
        wrt.write(80)
        time.sleep(0.1)
        wrt.write(100)
        time.sleep(0.1)
    wrt.write(90)

    time.sleep(1)

    _initial()
    time.sleep(1)

    i_b.write(76+60)
    i_m.write(15+30)
    i_t.write(55+10)

    m_b.write(87+60)
    m_m.write(44+30)
    m_t.write(58+10)

    time.sleep(1)

    for i in range(3):    
        wrt.write(80)
        time.sleep(0.1)
        wrt.write(100)
        time.sleep(0.1)
    wrt.write(90)
    time.sleep(1)

    _initial()
    time.sleep(1)

    i_b.write(76+60)
    i_m.write(15+30)
    i_t.write(55+10)

    m_b.write(87+60)
    m_m.write(44+30)
    m_t.write(58+10)

    r_b.write(85+60)
    r_m.write(35+30)
    r_t.write(60+10)

    time.sleep(1)
    for i in range(3):    
        wrt.write(80)
        time.sleep(0.1)
        wrt.write(100)
        time.sleep(0.1)
    wrt.write(90)
    time.sleep(1)
    _initial()
    time.sleep(1)
    i_b.write(76+60)
    i_m.write(15+30)
    i_t.write(55+10)

    m_b.write(87+60)
    m_m.write(44+30)
    m_t.write(58+10)

    r_b.write(85+60)
    r_m.write(35+30)
    r_t.write(60+10)

    p_b.write(88+60)
    p_m.write(45+30)
    p_t.write(45+10)

    time.sleep(1)

    for i in range(3):    
        wrt.write(80)
        time.sleep(0.1)
        wrt.write(100)
        time.sleep(0.1)
    wrt.write(90)
    time.sleep(1)

    _initial()

    t_b.write(88+60)
    t_m.write(48+70)
    t_t.write(78+80)


def crouch_walk_forward(steps=3, step_speed=0.1, speed=0.3):
    for i in range(steps):
        i_b.write(76-4)
        i_m.write(15+125)
        i_t.write(55-32)

        m_b.write(87-4)
        m_m.write(44+125)
        m_t.write(58-32)
        
        r_b.write(85-4)
        r_m.write(35+125)
        r_t.write(60-32)
        
        p_b.write(88-4)
        p_m.write(45+125)
        p_t.write(45-32)
        
        t_b.write(88-12)
        t_m.write(48+104)
        t_t.write(78-2)
        
        time.sleep(speed)

        i_b.write(76-63)
        i_m.write(15+138)
        i_t.write(55+15)
        time.sleep(step_speed)
        i_b.write(76-12)
        i_m.write(15+104)
        i_t.write(55-2)

        time.sleep(speed)
        
        m_b.write(87-63)
        m_m.write(44+138)
        m_t.write(58+15)
        time.sleep(step_speed)
        m_b.write(87-12)
        m_m.write(44+104)
        m_t.write(58-2)
        
        time.sleep(speed)
        
        r_b.write(85-63)
        r_m.write(35+138)
        r_t.write(60+15)
        time.sleep(step_speed)
        r_b.write(85-12)
        r_m.write(35+104)
        r_t.write(60-2)
        
        time.sleep(speed)
        
        p_b.write(88-63)
        p_m.write(45+138)
        p_t.write(45+15)
        p_b.write(88-12)
        p_m.write(45+104)
        p_t.write(45-2)
        
        time.sleep(speed)
        
        t_b.write(88-63)
        t_m.write(48+138)
        t_t.write(78+15)
        t_b.write(88-4)
        t_m.write(48+125)
        t_t.write(78-32)

        time.sleep(speed)

        i_b.write(76-4)
        i_m.write(15+125)
        i_t.write(55-32)

        m_b.write(87-4)
        m_m.write(44+125)
        m_t.write(58-32)
        
        r_b.write(85-4)
        r_m.write(35+125)
        r_t.write(60-32)

        p_b.write(88-4)
        p_m.write(45+125)
        p_t.write(45-32)

        t_b.write(88-12)
        t_m.write(48+104)
        t_t.write(78-2)

def crouch_walk_backward(steps=3, step_speed=0.1, speed=0.3):
    for i in range(steps):
        i_b.write(76-12)
        i_m.write(15+104)
        i_t.write(55-2)

        m_b.write(87-12)
        m_m.write(44+104)
        m_t.write(58-2)
        
        r_b.write(85-12)
        r_m.write(35+104)
        r_t.write(60-2)
        
        p_b.write(88-12)
        p_m.write(45+104)
        p_t.write(45-2)
        
        t_b.write(88-4)
        t_m.write(48+125)
        t_t.write(78-32)
        
        time.sleep(speed)

        i_b.write(76-63)
        i_m.write(15+138)
        i_t.write(55+15)
        time.sleep(step_speed)
        i_b.write(76-4)
        i_m.write(15+125)
        i_t.write(55-32)

        time.sleep(speed)
        
        m_b.write(87-63)
        m_m.write(44+138)
        m_t.write(58+15)
        time.sleep(step_speed)
        m_b.write(87-4)
        m_m.write(44+125)
        m_t.write(58-32)
        
        time.sleep(speed)
        
        r_b.write(85-63)
        r_m.write(35+138)
        r_t.write(60+15)
        time.sleep(step_speed)
        r_b.write(85-4)
        r_m.write(35+125)
        r_t.write(60-32)
        
        time.sleep(speed)
        
        p_b.write(88-63)
        p_m.write(45+138)
        p_t.write(45+15)
        p_b.write(88-4)
        p_m.write(45+125)
        p_t.write(45-32)
        
        time.sleep(speed)
        
        t_b.write(88-63)
        t_m.write(48+138)
        t_t.write(78+15)
        t_b.write(88-12)
        t_m.write(48+104)
        t_t.write(78-2)

        time.sleep(speed)

        i_b.write(76-12)
        i_m.write(15+104)
        i_t.write(55-2)

        m_b.write(87-12)
        m_m.write(44+104)
        m_t.write(58-2)
        
        r_b.write(85-12)
        r_m.write(35+104)
        r_t.write(60-2)

        p_b.write(88-12)
        p_m.write(45+104)
        p_t.write(45-2)

        t_b.write(88-4)
        t_m.write(48+125)
        t_t.write(78-32)

def crouch_pos():
    i_b.write(76-12)
    i_m.write(15+104)
    i_t.write(55-2)

    m_b.write(87-12)
    m_m.write(44+104)
    m_t.write(58-2)

    r_b.write(85-12)
    r_m.write(35+104)
    r_t.write(60-2)

    p_b.write(88-12)
    p_m.write(45+104)
    p_t.write(45-2)

    t_b.write(88-4)
    t_m.write(48+125)
    t_t.write(78-32)
    
def stand_walk():
    get_up()
    for i in range(3):
        wrt.write(90)
        time.sleep(0.5)
        m_b.write(87+59)
        m_m.write(44+60)
        m_t.write(58-29)

        r_b.write(85+59)
        r_m.write(35+60)
        r_t.write(60-29)

        p_b.write(88+59)
        p_m.write(45+60)
        p_t.write(45-29)

        t_b.write(88+44)
        t_m.write(48+83)
        t_t.write(78-37)
        
        t = 0.05
        t2 = 0.05

        i_b.write(76+38)
        i_m.write(15+102)
        i_t.write(55-50)
        time.sleep(t)
        i_b.write(76-2)
        i_m.write(15+124)
        i_t.write(55-22)
        time.sleep(t)
        i_t.write(55+1)
        time.sleep(t)
        i_m.write(15+76)
        time.sleep(t)
        i_b.write(76+15)

        time.sleep(t2)

        m_b.write(87+34)
        m_m.write(44+111)
        m_t.write(58-54)
        time.sleep(t)
        m_b.write(87-2)
        m_m.write(44+124)
        m_t.write(58-22)
        time.sleep(t)
        m_t.write(58-3)
        time.sleep(t)
        m_m.write(44+84)
        time.sleep(t)
        m_b.write(87+8)



        time.sleep(t2)

        r_b.write(85+38)
        r_m.write(35+102)
        r_t.write(60-50)
        time.sleep(t)
        r_b.write(85-2)
        r_m.write(35+124)
        r_t.write(60-22)
        time.sleep(t)
        r_t.write(60+1)
        time.sleep(t)
        r_m.write(35+76)
        time.sleep(t)
        r_b.write(85+15)

        time.sleep(t2)

        p_b.write(88+79)
        p_m.write(45+20)
        p_t.write(45-10)
        p_b.write(88+9)
        p_m.write(45+112)
        p_t.write(45-31)
        time.sleep(0.02)
        p_t.write(35)
        time.sleep(0.01)
        p_m.write(45+42)
        time.sleep(0.01)
        p_b.write(88+39)
        
        i_b.write(76+38)
        i_m.write(15+102)
        i_t.write(55-50)
        m_b.write(87+34)
        m_m.write(44+111)
        m_t.write(58-54)
        r_b.write(85+38)
        r_m.write(35+102)
        r_t.write(60-50)
        p_b.write(88+17)
        p_m.write(45+105)
        p_t.write(45-50)

    
while True:
    asyncio.run(main())



