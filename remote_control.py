#Shoutout to Kevin McAleer for the great intro to using Bluetooth on Raspberry Pi Pico W to build remote control devices for robots.

import sys
import aioble
import bluetooth
import machine
from machine import Pin
from machine import I2C
from machine import ADC
import uasyncio as asyncio
from micropython import const
import time

import ssd1306
import framebuf

i2c = I2C(0, sda=Pin(0), scl=Pin(1))
display = ssd1306.SSD1306_I2C(128, 64, i2c)


def clear_display():
    display.fill(0)
    display.show()
    
# ---------- Display image of Thing on display -----------

display.text('The THING', 28, 0)


with open('hand.pbm', 'rb') as f:
    f.readline() 
    f.readline() 
    f.readline() 
    data = bytearray(f.read())
fbuf = framebuf.FrameBuffer(data, 60, 61, framebuf.MONO_HLSB)
display.blit(fbuf, 35, 12, 0)

display.show()
time.sleep(2)
display.fill(0)
display.text("INITIALIZING", 15, 30)
display.show()
time.sleep(1)
display.text("CAPACITOR CHARGE",0, 40)
display.show()
time.sleep(1)
display.text("READY!", 40, 50)
display.show()
time.sleep(2)
clear_display()

# --------------------------------------------------------

# The Thing - Remote Buttons Pin Assignment
white_button = Pin(2, Pin.IN, Pin.PULL_DOWN)
black_button = Pin(3, Pin.IN, Pin.PULL_DOWN)
green_button = Pin(4, Pin.IN, Pin.PULL_DOWN)
red_button = Pin(5, Pin.IN, Pin.PULL_DOWN)
blue_button = Pin(6, Pin.IN, Pin.PULL_DOWN)
yellow_button = Pin(7, Pin.IN, Pin.PULL_DOWN)


white_led = Pin(8, machine.Pin.OUT)
black_led = Pin(10, machine.Pin.OUT)
green_led = Pin(11, machine.Pin.OUT)
red_led = Pin(12, machine.Pin.OUT)
blue_led = Pin(13, machine.Pin.OUT)
yellow_led = Pin(9, machine.Pin.OUT)

def turn_off_leds():
    white_led.value(0)
    black_led.value(0)
    green_led.value(0)
    red_led.value(0)
    blue_led.value(0)
    yellow_led.value(0)

# Thumb Stick Pin Definitions
adcpin1 = 26
adcpin2 = 27
adcpin3 = 28

# Thumb Stick Pin Assignment
left_thumb1 = ADC(adcpin1)
left_thumb2 = ADC(adcpin2)
right_thumb1 = ADC(adcpin3)

def uid():
    """ Return the unique id of the device as a string """
    return "{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}".format(
        *machine.unique_id())

MANUFACTURER_ID = const(0x02A29)
MODEL_NUMBER_ID = const(0x2A24)
SERIAL_NUMBER_ID = const(0x2A25)
HARDWARE_REVISION_ID = const(0x2A26)
BLE_VERSION_ID = const(0x2A28)

led = machine.Pin("LED", machine.Pin.OUT)

_ENV_SENSE_UUID = bluetooth.UUID(0x180A)
_GENERIC = bluetooth.UUID(0x1848)
_ENV_SENSE_TEMP_UUID = bluetooth.UUID(0x1800)
_BUTTON_UUID = bluetooth.UUID(0x2A6E)

_BLE_APPEARANCE_GENERIC_REMOTE_CONTROL = const(384)

# Advertising frequency
ADV_INTERVAL_MS = 250_000

device_info = aioble.Service(_ENV_SENSE_UUID)

connection = None

# Create characteristics for device info
aioble.Characteristic(device_info, bluetooth.UUID(MANUFACTURER_ID), read=True, initial="TheThingRemote")
aioble.Characteristic(device_info, bluetooth.UUID(MODEL_NUMBER_ID), read=True, initial="1.0")
aioble.Characteristic(device_info, bluetooth.UUID(SERIAL_NUMBER_ID), read=True, initial=uid())
aioble.Characteristic(device_info, bluetooth.UUID(HARDWARE_REVISION_ID), read=True, initial=sys.version)
aioble.Characteristic(device_info, bluetooth.UUID(BLE_VERSION_ID), read=True, initial="1.0")

remote_service = aioble.Service(_GENERIC)

button_characteristic = aioble.Characteristic(
    remote_service, _BUTTON_UUID, read=True, notify=True
)

print('registering services')
aioble.register_services(remote_service, device_info)

connected = False

async def remote_task():
    """ Send the event to the connected device """
    while True:
        left_thumb1_value = left_thumb1.read_u16()
        right_thumb1_value = right_thumb1.read_u16()
        if not connected:
            print('not connected')
            await asyncio.sleep_ms(1000)
            continue
        if green_button.value():
            button_characteristic.write(b"g")   
            button_characteristic.notify(connection,b"g")
            turn_off_leds()
            green_led.value(1)
            clear_display()
            display.text("FINGER STAMP", 20, 40)
            display.show()
        if red_button.value():
            button_characteristic.write(b"r")   
            button_characteristic.notify(connection,b"r")
            turn_off_leds()
            red_led.value(1)
            clear_display()
            display.text("CROUCH POS", 20, 40)
            display.show()
        if blue_button.value():
            button_characteristic.write(b"b")   
            button_characteristic.notify(connection,b"b")
            turn_off_leds()
            blue_led.value(1)
            clear_display()
            display.text("STAND POS", 20, 40)
            display.show()
        if yellow_button.value():
            button_characteristic.write(b"y")   
            button_characteristic.notify(connection,b"y")
            turn_off_leds()
            yellow_led.value(1)
            clear_display()
            display.text("POINT FINGER", 20, 40)
            display.show()
        if white_button.value():
            button_characteristic.write(b"w")   
            button_characteristic.notify(connection,b"w")
            turn_off_leds()
            white_led.value(1)
            clear_display()
            display.text("LED ON", 20, 40)
            display.show()
        if black_button.value():
            button_characteristic.write(b"k")   
            button_characteristic.notify(connection,b"k")
            turn_off_leds()
            black_led.value(1)
            clear_display()
            display.text("BOW DOWN", 20, 40)
            display.show()
        if left_thumb1_value > 40000:
            button_characteristic.write(b"x")   
            button_characteristic.notify(connection,b"x")
            clear_display()
            display.text("CROUCH FWD", 20, 40)
            display.show()
        if left_thumb1_value < 20000:
            button_characteristic.write(b"z")   
            button_characteristic.notify(connection,b"z")
            clear_display()
            display.text("CROUCH BWD", 20, 40)
            display.show()
        if right_thumb1_value > 40000:
            button_characteristic.write(b"v")   
            button_characteristic.notify(connection,b"v")
            clear_display()
            display.text("STAND WALK", 20, 40)
            display.show()
        else:
            button_characteristic.write(b"!")
        await asyncio.sleep_ms(10)
            
   
async def peripheral_task():
    print('peripheral task started')
    global connected, connection
    while True:
        connected = False
        async with await aioble.advertise(
            ADV_INTERVAL_MS, 
            name="TheThing", 
            appearance=_BLE_APPEARANCE_GENERIC_REMOTE_CONTROL, 
            services=[_ENV_SENSE_TEMP_UUID]
        ) as connection:
            print("Connection from", connection.device)
            connected = True
            print(f"connected: {connected}")
            await connection.disconnected(timeout_ms=None)
            print(f'disconnected')
        

async def blink_task():
    print('blink task started')
    toggle = True
    while True:
        led.value(toggle)
        toggle = not toggle
        blink = 1000
        if connected:
            blink = 1000
        else:
            blink = 250
        await asyncio.sleep_ms(blink)
        
async def main():
    tasks = [
        asyncio.create_task(peripheral_task()),
        asyncio.create_task(blink_task()),
        asyncio.create_task(remote_task()),
    ]
    await asyncio.gather(*tasks)

asyncio.run(main())

