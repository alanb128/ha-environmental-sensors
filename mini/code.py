# SPDX-FileCopyrightText: Copyright (c) 2020 ladyada for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import time
import board
import adafruit_sht4x
import busio
import digitalio
import displayio
import terminalio
import os
from adafruit_display_text import label
from fourwire import FourWire
from adafruit_st7735r import ST7735R
from adafruit_bitmap_font import bitmap_font
import ipaddress
import wifi
import socketpool
import ssl
import adafruit_minimqtt.adafruit_minimqtt as MQTT
import math
import microcontroller

screen_mode = 0
loop_count = 0
reading_count = 0
mqtt_reconnect_count = 0
wifi_reconnect_count = 0
deg_f = 0
temperature = 0
relative_humidity = 0
mqtt_connect = False
use_display = True
wifi_connect = False
startup_mode = True

# MQTT settings:
TIMEOUT = None
HOST = os.getenv('MQTT_HOST')
PORT = os.getenv('MQTT_PORT')
TOPIC = os.getenv('TOPIC_PATH')

def connected(client, userdata, flags, rc):
    # This function will be called when the client is connected
    # successfully to the broker.
    global mqtt_connect
    print(f"Connected to the MQTT broker!")
    tile_grid3.hidden = False
    mqtt_connect = True
    #mqtt_client.subscribe("/status/floor")

def disconnected(client, userdata, rc):
    # This method is called when the client is disconnected
    global mqtt_connect
    print("Disconnected from the MQTT broker!")
    tile_grid3.hidden = True
    mqtt_connect = False

def message(client, topic, message):
    # This method is called when a topic the client is subscribed to
    # has a new message.
    pass

def readings():
    
    global deg_f, temperature, relative_humidity
    
    tile_grid2.hidden = False
    temp, r_humidity = sht.measurements
    deg_f = (temp * 1.8) + 32
    temperature = int(temp)
    relative_humidity = r_humidity
    print("Temperature: %0.1f F" % deg_f)
    print("Humidity: %0.1f %%" % relative_humidity)
    print("")
    screen_change(screen_mode)
    #tile_grid2.hidden = True

def publish_it():
    
    global mqtt_connect
    
    if not wifi_connect:
        print("Not connected to wifi, skipping publish.")
        return
    else:
        if not mqtt_connect:
            print("Not connected to MQTT broker; skipping publish")
            return
    
    tile_grid4.hidden = False
    #print("here: {}, {}".format(deg_f, temperature))
    try:
        mqtt_client.publish(TOPIC + "/humidity", relative_humidity)
    except:
        print("Error publishing MQTT humidity")
        mqtt_connect = False
    try:
    #print("here: {}, {}".format(deg_f, temperature))
    #print("type {}".format(type(deg_f)))
        mqtt_client.publish(TOPIC + "/temperature", deg_f)#deg_f)
    except:
        print("Error publishing MQTT temperature")
        mqtt_connect = False
    #mqtt_client.publish(topic, str(FLOOR_ID) + "up")

def screen_change(mode):
    
    #global text
    
    print("Screen change to mode: {}".format(mode))
    
    if mode == 1:
        group_info.hidden = True
        group_readings.hidden = False
        text = "{}F / {}%".format(int(deg_f), int(relative_humidity))
        text_area.text = text
    elif mode == 2:
        text = "{}C / {}%".format(int(temperature), int(relative_humidity))
        text_area.text = text
    elif mode == 3:
        group_readings.hidden = True
        group_info.hidden = False

def connect_wifi(retry):
    
    global wifi_connect
    
    try:
        ssid = os.getenv('CIRCUITPY_WIFI_SSID')
        pw = os.getenv('CIRCUITPY_WIFI_PASSWORD')
    except:
        print("Could not find WiFi info. Check your settings.toml file!")
        wifi_connect = False
        tile_grid.hidden = True
        return
    
    print("Attempting connection to WiFi...")

    #  connect to your SSID
    try:
        wifi.radio.connect(ssid, pw)
    except:
        print("Could not connect to WiFi!")
        tile_grid.hidden = True
        wifi_connect = False
    else:
        wifi_connect = True
        tile_grid.hidden = False
        print("Connected to WiFi")
        print("My IP address is ", wifi.radio.ipv4_address)
              
    if wifi_connect:
        if mqtt_connect:
            led_control("G")
        else:
            led_control("Y")
    else:
        led_control("0")
            
def connect_mqtt(retry):
    
    global mqtt_connect
    
    # Connect the client to the MQTT broker.
    print("Connecting to the MQTT broker...")
    if wifi_connect:
        try:
            mqtt_client.connect()
        except:
            print("Error trying to connect to MQTT broker")
            mqtt_connect = False
    else:
        print("Not connected to WiFi, skipping broker connection attempt.")
    
    if mqtt_connect:
        led_control("G")
    else:
        if wifi_connect:
            led_control("Y")
        else:
            led_control("0")
            
def led_control(state):
    
    if state == "R":
        led_grn.value = 0
        led_red.value = 1
    elif state == "G":
        led_red.value = 0
        led_grn.value = 1
    elif state == "Y":
        led_red.value = 1
        led_grn.value = 1
    else:
        led_red.value = 0
        led_grn.value = 0
        
        
i2c = busio.I2C(scl=board.GP5, sda=board.GP4)
sht = adafruit_sht4x.SHT4x(i2c)
serial_num = hex(sht.serial_number)
print("Found SHT4x with serial number", serial_num)

sht.mode = adafruit_sht4x.Mode.NOHEAT_HIGHPRECISION
# Can also set the mode to enable heater
# sht.mode = adafruit_sht4x.Mode.LOWHEAT_100MS
print("Current mode is: ", adafruit_sht4x.Mode.string[sht.mode])

# Define GPIO
btn1 = digitalio.DigitalInOut(board.GP16)
btn1.direction = digitalio.Direction.INPUT
btn1.pull = digitalio.Pull.UP

led_red = digitalio.DigitalInOut(board.GP18)
led_red.direction = digitalio.Direction.OUTPUT

led_grn = digitalio.DigitalInOut(board.GP19)
led_grn.direction = digitalio.Direction.OUTPUT

led_control("R")

# Set up display

# Release any resources currently in use for the displays
displayio.release_displays()

#spi = board.SPI()
spi = busio.SPI(clock=board.GP10, MOSI=board.GP11) #, MISO=board.GP16)
tft_cs = board.GP12
tft_dc = board.GP13

try:
    display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=board.GP15)
except:
    print("Could not set up display...")
    use_display = False

try:
    display = ST7735R(
        display_bus,
        width=160,
        height=80,
        rowstart=1,
        colstart=26,
        rotation=90,
        invert=True,
    )
except:
    print("Could not set up display...")
    use_display = False
    
group_main = displayio.Group()
group_readings = displayio.Group()
group_info = displayio.Group()
group_info.hidden = True

display.root_group = group_main

# Set up the pre-made bitmap icons
# Setup the file as the bitmap data source
bitmap1 = displayio.OnDiskBitmap("/wifi.bmp")
# Create a TileGrid to hold the bitmap
tile_grid = displayio.TileGrid(bitmap1, pixel_shader=bitmap1.pixel_shader, x=1,y=60)

bitmap2 = displayio.OnDiskBitmap("/thermo.bmp")
tile_grid2 = displayio.TileGrid(bitmap2, pixel_shader=bitmap2.pixel_shader, x=40,y=60)

bitmap3 = displayio.OnDiskBitmap("/mqtt.bmp")
tile_grid3 = displayio.TileGrid(bitmap3, pixel_shader=bitmap3.pixel_shader, x=80,y=60)

bitmap4 = displayio.OnDiskBitmap("/comm.bmp")
tile_grid4 = displayio.TileGrid(bitmap4, pixel_shader=bitmap4.pixel_shader, x=120,y=60)

# Add the TileGrids to the Group
group_readings.append(tile_grid)
group_readings.append(tile_grid2)
group_readings.append(tile_grid3)
group_readings.append(tile_grid4)

# Add this group to the root group
group_main.append(group_readings)

# All readings start out hidden
tile_grid.hidden = True
tile_grid2.hidden = True
tile_grid3.hidden = True
tile_grid4.hidden = True

# Set up text for readings
text_group = displayio.Group(scale=2, x=5, y=20)
text = "Starting!"
font = bitmap_font.load_font("/Helvetica-Bold-16.bdf")
text_area = label.Label(font, text=text, color=0xFFFF00)
text_group.append(text_area) # Subgroup for text scaling
group_readings.append(text_group)

connect_wifi(False)

# set up MQTT
# Create a socket pool
pool = socketpool.SocketPool(wifi.radio)

# Set up a MiniMQTT Client
mqtt_client = MQTT.MQTT(
    broker=HOST,
    port=PORT,
    is_ssl=False,
    keep_alive=3600,
    socket_pool=pool
)

# Setup the callback methods above
mqtt_client.on_connect = connected
mqtt_client.on_disconnect = disconnected
#mqtt_client.on_message = message

connect_mqtt(0)

# Set up the info page
text_info1 = displayio.Group(x=4, y=5)
text_info2 = displayio.Group(x=4, y=24)
text_info3 = displayio.Group(x=4, y=45)
text_info4 = displayio.Group(x=4, y=64)
text = "ip: " + str(wifi.radio.ipv4_address)
text_area_f1 = label.Label(font, text=text, color=0xFFFFFF)
text = "sw ver: " + os.getenv('SW_VERSION')
text_area_f2 = label.Label(font, text=text, color=0xFFFFFF)
text = "cpu temp: " + str(microcontroller.cpu.temperature) + " C"
text_area_f3 = label.Label(font, text=text, color=0xFFFFFF)
text = "mqtt: " + os.getenv('MQTT_HOST')
text_area_f4 = label.Label(font, text=text, color=0xFFFFFF)
text_info1.append(text_area_f1)
text_info2.append(text_area_f2)
text_info3.append(text_area_f3)
text_info4.append(text_area_f4)
group_info.append(text_info1)
group_info.append(text_info2)
group_info.append(text_info3)
group_info.append(text_info4)
# Add this group to the root group
group_main.append(group_info)

screen_mode = 1        
time.sleep(1)
    
while True:
    
    #mqtt_client.loop()
    
    if startup_mode:
        print("Startup complete!")
        startup_mode = False
        readings()
    time.sleep(0.4)
    if loop_count == 0:
        tile_grid2.hidden = True
    if reading_count == 0:
        tile_grid4.hidden = True
    if btn1.value == False:
        screen_mode = screen_mode + 1
        if screen_mode == 4:
            screen_mode = 1
        print('pushed btn; mode is: {}'.format(screen_mode))
        screen_change(screen_mode)
    loop_count = loop_count + 1
    if loop_count == 26:  # every 10.4 seconds
        loop_count = 0
        reading_count = reading_count + 1
        readings()
    if reading_count == 4:  # every 40 seconds or so
        reading_count = 0
        publish_it()
    if not wifi_connect:
        wifi_reconnect_count = wifi_reconnect_count + 1
        if wifi_reconnect_count == 480:  # about 2 minutes
            print("Attempting wifi connection...")
            wifi_connect_count = 0
            connect_wifi(True)
    else:
        if not mqtt_connect:
            mqtt_reconnect_count = mqtt_reconnect_count + 1
            if mqtt_reconnect_count == 480:  # about 2 minutes
                print("Attempting mqtt broker connection...")
                mqtt_reconnect_count = 0
                connect_mqtt(True)
                    
    #text_group.append(text_area) # Subgroup for text scaling
    #splash.append(text_group)
    #time.sleep(4)
    