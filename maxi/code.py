# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import os
import board
import busio
import digitalio
from analogio import AnalogIn
import microcontroller
import struct

import adafruit_lis3dh
from digitalio import DigitalInOut, Direction, Pull

from adafruit_pm25.i2c import PM25_I2C
from adafruit_dps310.basic import DPS310
import adafruit_veml7700
import adafruit_scd4x

import displayio
import terminalio
from adafruit_display_text.bitmap_label import Label
import adafruit_imageload
from fourwire import FourWire
from vectorio import Circle
from adafruit_gc9a01a import GC9A01A
from adafruit_display_shapes.arc import Arc
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label

import ipaddress
import wifi
import socketpool
import ssl
import adafruit_minimqtt.adafruit_minimqtt as MQTT

print("Hello.")

def take_reading(sensor):
    
    global pm10
    global pm25
    global hum
    pm1 = 0
    co2 = 0
    reading = 0
      
    if sensor == "PM1":
    
        try:
            aqdata = pm_25.read()
            # print(aqdata)
            print()
            print("Concentration Units (standard)")
            print("---------------------------------------")
            print(
                "PM 1.0: %d\tPM2.5: %d\tPM10: %d"
                % (aqdata["pm10 standard"], aqdata["pm25 standard"], aqdata["pm100 standard"])
            )
            pm25 = aqdata["pm25 standard"]
            pm10 = aqdata["pm100 standard"]
            pm1 = aqdata["pm10 standard"]
        except Exception as e:
            print("Unable to read from PM sensor: {}; retrying...".format(e))
            time.sleep(1.2)
            try:
                aqdata = pm_25.read()
                # print(aqdata)
                print()
                print("Concentration Units (standard)")
                print("---------------------------------------")
                print(
                    "PM 1.0: %d\tPM2.5: %d\tPM10: %d"
                    % (aqdata["pm10 standard"], aqdata["pm25 standard"], aqdata["pm100 standard"])
                )
                pm25 = aqdata["pm25 standard"]
                pm10 = aqdata["pm100 standard"]
                pm1 = aqdata["pm10 standard"]
            except Exception as e:
                print("Unable to read from PM sensor: {}.".format(e))
                pm25 = 0
                pm10 = 0
                pm1 = 0
        reading = pm1
    
    elif sensor == "PM2.5":
        reading = pm25

    elif sensor == "PM10":
        reading = pm10
    
    elif sensor == "Temp":
        #print("Temperature = %.2f *C" % dps310.temperature)
        reading = round((dps310.temperature * 1.8) + 32)
    
    
    elif sensor == "Pres":
        #print("Pressure = %.2f hPa" % dps310.pressure)
        reading = round(dps310.pressure)
    
    elif sensor == "Light":
        #print("Ambient light:", veml7700.light)
        reading = veml7700.light
    
    elif sensor == "CO2":
        
        if scd4x.data_ready:
            #print("CO2: %d ppm" % scd4x.CO2)
            #print("Temperature: %0.1f *C" % scd4x.temperature)
            #print("Humidity: %0.1f %%" % scd4x.relative_humidity)
            #print()
            hum = round(scd4x.relative_humidity)
            co2 = scd4x.CO2
        else:
            print("Waiting for CO2 ready...")
            time.sleep(1.33)
            if scd4x.data_ready:
                hum = scd4x.relative_humidity
                co2 = scd4x.CO2
        reading = co2
    
    elif sensor == "Hum":
        
        reading = hum
    
    elif sensor == "Gas":
        
        reading = int(analog_range(gas_pin.value))
    
    elif sensor == "Sound":
        
        reading = int(analog_range(mic_pin.value))
    
    else:
        print("Unknown sensor request {}.".format(sensor))
        reading = 0
    
    publish_it(sensor, reading)
    return reading

def angle_range(OldValue, OldMin, OldMax):
    #print(OldValue, OldMin, OldMax)
    # https://stackoverflow.com/a/929107
    NewMax = 280
    NewMin = 5
    OldRange = (OldMax - OldMin)  
    NewRange = (NewMax - NewMin)
    #print(OldValue, OldMin, NewRange, OldRange, NewMin)
    NewValue = (((OldValue - OldMin) * NewRange) / OldRange) + NewMin
    
    return NewValue

def direction_range(OldValue):
    
    OldMax = 280
    OldMin = 5
    NewMax = 130
    NewMin = 0
    OldRange = (OldMax - OldMin)  
    NewRange = (NewMax - NewMin)  
    NewValue = (((OldValue - OldMin) * NewRange) / OldRange) + NewMin
    
    return 220 - NewValue
    
def arc_measure(reading, minimum, middle, high, maximum):
    
    angle = angle_range(reading, minimum, maximum)
    arc.angle = angle
    arc.direction = direction_range(angle)
    if reading > middle:
        arc.fill=0xFFFF00
    elif reading > high:
        arc.fill=0xFF0000
    else:
        arc.fill=0x00FF00

def analog_range(OldValue):
    
    # https://stackoverflow.com/a/929107
    OldMin = 0
    OldMax = 65535
    NewMax = 100
    NewMin = 0
    OldRange = (OldMax - OldMin)  
    NewRange = (NewMax - NewMin)
    #print(OldValue, OldMin, NewRange, OldRange, NewMin)
    NewValue = (((OldValue - OldMin) * NewRange) / OldRange) + NewMin
    
    return NewValue

def show_info():
    
    global screen_mode
    global mode_count
    
    mode_count = 0
    
    if screen_mode == 0 or screen_mode == 2:
        screen_mode = 1
        group_scan.hidden = True
        group_readings.hidden = True
        group_info.hidden = False
        
        
    else:
        screen_mode = 0
        group_info.hidden = True
        group_scan.hidden = True
        group_readings.hidden = False
        
    if wifi_connect:
        tile_grid3.hidden = False
    else:
        tile_grid3.hidden = True
        
    if mqtt_connect:
        tile_grid4.hidden = False
    else:
        tile_grid4.hidden = True
        
        
def show_scan():
    
    global screen_mode
    global mode_count
    
    mode_count = 0
    
    if screen_mode == 0 or screen_mode == 1:
        screen_mode = 2
        group_readings.hidden = True
        group_info.hidden = True
        text_area_s1.text = "Scan QR..."
        text_area_s2.color = 0xFFFF00
        text_area_s2.text = "Waiting..."
        group_scan.hidden = False
        
        
    else:
        screen_mode = 0
        group_info.hidden = True
        group_scan.hidden = True
        group_readings.hidden = False

def show_reading():
    
    group_info.hidden = True
    group_scan.hidden = True
    group_readings.hidden = False
        
def connected(client, userdata, flags, rc):
    # This function will be called when the client is connected
    # successfully to the broker.
    global mqtt_connect
    print(f"Connected to the MQTT broker!")
    #tile_grid3.hidden = False
    mqtt_connect = True
    print("Subscribing to led1 topic.")
    client.subscribe("/beast/led1")

def disconnected(client, userdata, rc):
    # This method is called when the client is disconnected
    global mqtt_connect
    print("Disconnected from the MQTT broker!")
    #tile_grid3.hidden = True
    mqtt_connect = False

def publish_it(subtopic, read_value):
    
    global mqtt_connect
    
    if not wifi_connect:
        #print("Not connected to wifi, skipping publish.")
        return
    else:
        if not mqtt_connect:
            #print("Not connected to MQTT broker; skipping publish")
            return
    
    #tile_grid4.hidden = False
    #print("here: {}, {}".format(deg_f, temperature))
    try:
        mqtt_client.publish(TOPIC + "/" + subtopic, read_value)
    except:
        print("Error publishing MQTT {}".format(subtopic))
        mqtt_connect = False

def message(client, topic, message):
    # This method is called when a topic the client is subscribed to
    # has a new message.
    print("New MQTT message: {}; topic: {}".format(message, topic))

    if topic == "/beast/led1":
        if message == "1":
            pir_led.value = True
        else:
            pir_led.value = False
            
def connect_wifi(force):
    
    global wifi_connect
    
    
    print("Attempting connection to WiFi...")

    #  connect to your SSID if not connected unless forced
    if (not wifi_connect) or force:
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
    

def code_read():
    
    read_data = bytearray(TINY_CODE_READER_I2C_BYTE_COUNT)
    while not i2c.try_lock():
        # Keep trying until the lock is acquired
        print("Trying to lock I2C for reader...:")
        time.sleep(0.5)
        
    try:
        try:
            i2c.readfrom_into(TINY_CODE_READER_I2C_ADDRESS, read_data)
        except:
            print("Error reading QR - is device attached?")
        else:
            print("QR code read.")
            #print(i2c.scan())
    finally:
        i2c.unlock()
        

    message_length,  = struct.unpack_from(TINY_CODE_READER_LENGTH_FORMAT, read_data, TINY_CODE_READER_LENGTH_OFFSET)
    message_bytes = struct.unpack_from(TINY_CODE_READER_MESSAGE_FORMAT, read_data, TINY_CODE_READER_MESSAGE_OFFSET)
    print(message_length)

    if message_length > 0:
        try:
            message_string = bytearray(message_bytes[0:message_length]).decode("utf-8")
            print("Code reader msg: {}".format(message_string))
            return message_string
        except:
            print("Couldn't decode reader as UTF 8")
            return "Empty"
    else:
        print("QR message empty.")
        return "Empty"

def read_scan_data(qr_data):
    
    global ssid
    global pw
    
    # Sample WiFi data: WIFI:T:WPA;S:MyNet;P:QW6HN8IKL9;H:;;

    if qr_data.startswith("WIFI:"):
        # Remove the "WIFI:" prefix
        data_string = qr_data[5:]
        
        # Split into individual components
        components = data_string.split(';')
        
        for comp in components:
            if comp.startswith("S:"):
                ssid = comp[2:]
            elif comp.startswith("T:"):
                pass
            elif comp.startswith("P:"):
                pw = comp[2:]
        text_area_s2.color = 0x00FF00
        text_area_s2.text = "Accepted!"
        print("WiFi credentials received!")
        
        connect_wifi(True)
        
    else:
        text_area_s2.color = 0xFF0000
        text_area_s2.text = "Rejected!"
        print("QR code not for WiFi!")
    
    time.sleep(1.25)
    
def do_pir():
    
    global pir_led
    
    if pir_active:
        # turn on LED
        pir_led.value = True
        # publish
        publish_it("motion", 1)
    else:
        # turn off led
        pir_led.value = False
        # publish
        publish_it("motion", 0)
        
        
sensors = {
    "Light": {
        "unit": "lux",
        "minimum": 0,
        "middle": 1000,
        "high": 1500,
        "maxi": 2000
        },
    "CO2": {
        "unit": "ppm",
        "minimum": 0,
        "middle": 1000,
        "high": 2000,
        "maxi": 3000
        },
    "Temp": {
        "unit": "F",
        "minimum": 0,
        "middle": 72,
        "high": 85,
        "maxi": 120
        },
    "Hum": {
        "unit": "%",
        "minimum": 0,
        "middle": 50,
        "high": 60,
        "maxi": 100
        },
    "Pres": {
        "unit": "hPa",
        "minimum": 970,
        "middle": 1020,
        "high": 1030,
        "maxi": 1050
        },
    "PM1": {
        "unit": "ppm",
        "minimum": 0,
        "middle": 25,
        "high": 50,
        "maxi": 100
        },
    "PM2.5": {
        "unit": "ppm",
        "minimum": 0,
        "middle": 35,
        "high": 55,
        "maxi": 120
        },
    "PM10": {
        "unit": "ppm",
        "minimum": 0,
        "middle": 53,
        "high": 150,
        "maxi": 220
        },
    "Sound": {
        "unit": "lvl",
        "minimum": 0,
        "middle": 75,
        "high": 90,
        "maxi": 100
        },
    "Gas": {
        "unit": "lvl",
        "minimum": 0,
        "middle": 50,
        "high": 75,
        "maxi": 100
        }
    }
pages = ["Light","CO2","Temp","Hum","Pres","PM1","PM2.5","PM10","Sound","Gas"]
page = 0
screen_mode = 0
mode_count = 0
mqtt_reconnect_count = 0
wifi_reconnect_count = 0
mqtt_connect = False
wifi_connect = False
ssid = ""
pw = ""
pir_active = False
pir_active_count = 0

# MQTT settings:
TIMEOUT = None
HOST = os.getenv('MQTT_HOST')
PORT = os.getenv('MQTT_PORT')
TOPIC = os.getenv('TOPIC_PATH')

# for caching
pm25 = 0
pm10 = 0
temp = 0
hum = 0


# Set up display
displayio.release_displays()

spi = busio.SPI(clock=board.GP10, MOSI=board.GP11) #, MISO=board.GP16)
tft_cs = board.GP12
tft_dc = board.GP13
tft_reset=board.GP15



display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_reset)
display = GC9A01A(display_bus, width=240, height=240)

# Set up screens
group_main = displayio.Group()
group_readings = displayio.Group()
group_info = displayio.Group()
group_scan = displayio.Group()
group_info.hidden = True
group_scan.hidden = True

display.root_group = group_main

group_metric = displayio.Group(scale=2, x=65, y=145)
text = "Startup"
#font = bitmap_font.load_font("/Helvetica-Bold-16.bdf")
font = bitmap_font.load_font("/helvB14.bdf")
text_metric = label.Label(font, text=text, color=0xFFFF00)
group_metric.append(text_metric) # Subgroup for text scaling
group_readings.append(group_metric)

group_value = displayio.Group(scale=2, x=70, y=75)
text = "    0"
font = bitmap_font.load_font("/helvB14.bdf")
text_value = label.Label(font, text=text, color=0xFFFFFF)
group_value.append(text_value) # Subgroup for text scaling
group_readings.append(group_value)

group_units = displayio.Group(scale=1, x=95, y=105)
text = "hello"
font = bitmap_font.load_font("/helvB14.bdf")
text_units = label.Label(font, text=text, color=0xFFFFFF)
group_units.append(text_units) # Subgroup for text scaling
group_readings.append(group_units)

arc = Arc(x=120, y=120, radius=110, angle=5, direction=220, segments=20, arc_width=8, fill=0x00FF00)
bg_arc = Arc(x=120, y=120, radius=110, angle=280, direction=90, segments=20, arc_width=8, fill=0x808080)
group_readings.append(bg_arc)
group_readings.append(arc)


# Add this group to the root group
group_main.append(group_readings)

# Set up the info page
text_info1 = displayio.Group(x=24, y=100)
text_info2 = displayio.Group(x=24, y=120)
text_info3 = displayio.Group(x=24, y=140)
text_info4 = displayio.Group(x=24, y=160)
text_info5 = displayio.Group(x=40, y=180)
text = "ip: " + "192.168.1.55" #str(wifi.radio.ipv4_address)
text_area_f3 = label.Label(font, text=text, color=0xFFFFFF)
text = "sw v. " + os.getenv('SW_VERSION')
text_area_f1 = label.Label(font, text=text, color=0xFFFFFF)
text = "cpu temp: " + str(int(microcontroller.cpu.temperature))
text_area_f2 = label.Label(font, text=text, color=0xFFFFFF)
text = "mqtt: " + os.getenv('MQTT_HOST')
text_area_f4 = label.Label(font, text=text, color=0xFFFFFF)
text = "port: " + str(os.getenv('MQTT_PORT'))
text_area_f5 = label.Label(font, text=text, color=0xFFFFFF)
text_info1.append(text_area_f1)
text_info2.append(text_area_f2)
text_info3.append(text_area_f3)
text_info4.append(text_area_f4)
text_info5.append(text_area_f5)
group_info.append(text_info1)
group_info.append(text_info2)
group_info.append(text_info3)
group_info.append(text_info4)
group_info.append(text_info5)
# Add the settings page image
bitmap1 = displayio.OnDiskBitmap("/info.bmp")
# Create a TileGrid to hold the bitmap
tile_grid = displayio.TileGrid(bitmap1, pixel_shader=bitmap1.pixel_shader, x=100,y=35)
# Add the TileGrids to the Group
group_info.append(tile_grid)

# add the wifi and mqtt icons
bitmap3 = displayio.OnDiskBitmap("/wifi.bmp")
# Create a TileGrid to hold the bitmap
tile_grid3 = displayio.TileGrid(bitmap3, pixel_shader=bitmap1.pixel_shader, x=75,y=200)
# Add the TileGrids to the Group
group_info.append(tile_grid3)

bitmap4 = displayio.OnDiskBitmap("/mqtt.bmp")
# Create a TileGrid to hold the bitmap
tile_grid4 = displayio.TileGrid(bitmap4, pixel_shader=bitmap1.pixel_shader, x=110,y=200)
# Add the TileGrids to the Group
group_info.append(tile_grid4)

# Add this group to the root group
group_main.append(group_info)

# WiFi and MQTT start out hidden
tile_grid3.hidden = True
tile_grid4.hidden = True

# Set up the scan page
text_scan1 = displayio.Group(scale=2, x=17, y=120)
text_scan2 = displayio.Group(x=75, y=165)

text = "Scan QR now"
text_area_s1 = label.Label(font, text=text, color=0xFFFFFF)

text_scan1.append(text_area_s1)

group_scan.append(text_scan1)

text = "waiting..."
text_area_s2 = label.Label(font, text=text, color=0xFFFF00)

text_scan2.append(text_area_s2)

group_scan.append(text_scan2)

# Add the scan page image
bitmap2 = displayio.OnDiskBitmap("/qr.bmp")
# Create a TileGrid to hold the bitmap
tile_grid2 = displayio.TileGrid(bitmap2, pixel_shader=bitmap1.pixel_shader, x=100,y=40)
# Add the TileGrids to the Group
group_scan.append(tile_grid2)

# Add this group to the root group
group_main.append(group_scan)
# -------------------------------------------------------------

# GPIO /ADC

btn1 = digitalio.DigitalInOut(board.GP21)
btn1.direction = digitalio.Direction.INPUT
btn1.pull = digitalio.Pull.UP

btn2 = digitalio.DigitalInOut(board.GP20)
btn2.direction = digitalio.Direction.INPUT
btn2.pull = digitalio.Pull.UP

btn3 = digitalio.DigitalInOut(board.GP16)
btn3.direction = digitalio.Direction.INPUT
btn3.pull = digitalio.Pull.UP

pir = digitalio.DigitalInOut(board.GP22)
pir.direction = digitalio.Direction.INPUT
pir.pull = digitalio.Pull.DOWN

pir_led = digitalio.DigitalInOut(board.GP17)
pir_led.direction = digitalio.Direction.OUTPUT

mic_pin = AnalogIn(board.A0)
gas_pin = AnalogIn(board.A1)


i2c = busio.I2C(scl=board.GP5, sda=board.GP4)

# LIS3DH
lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c)
# Set range of accelerometer (can be RANGE_2_G, RANGE_4_G, RANGE_8_G or RANGE_16_G).
lis3dh.range = adafruit_lis3dh.RANGE_2_G

#PM25
reset_pin = None
# Connect to a PM2.5 sensor over I2C
pm_25 = PM25_I2C(i2c, reset_pin)
print("Found PM2.5 sensor, reading data...")

#DPS310
dps310 = DPS310(i2c)

#VEML7700
veml7700 = adafruit_veml7700.VEML7700(i2c)

text_value.text = "  25"
arc_measure(25, 0, 101, 101, 100)

#SCD4X
scd4x = adafruit_scd4x.SCD4X(i2c)
print("Serial number:", [hex(i) for i in scd4x.serial_number])
scd4x.start_periodic_measurement()
print("Waiting for first measurement....")

text_value.text = "  40"
arc_measure(40, 0, 101, 101, 100)

# code reader setup
# The code reader has the I2C ID of hex 0c, or decimal 12.
TINY_CODE_READER_I2C_ADDRESS = 0x0C
TINY_CODE_READER_LENGTH_OFFSET = 0
TINY_CODE_READER_LENGTH_FORMAT = "H"
TINY_CODE_READER_MESSAGE_OFFSET = TINY_CODE_READER_LENGTH_OFFSET + struct.calcsize(TINY_CODE_READER_LENGTH_FORMAT)
TINY_CODE_READER_MESSAGE_SIZE = 254
TINY_CODE_READER_MESSAGE_FORMAT = "B" * TINY_CODE_READER_MESSAGE_SIZE
TINY_CODE_READER_I2C_FORMAT = TINY_CODE_READER_LENGTH_FORMAT + TINY_CODE_READER_MESSAGE_FORMAT
TINY_CODE_READER_I2C_BYTE_COUNT = struct.calcsize(TINY_CODE_READER_I2C_FORMAT)

# let sensors stabilize
print("Initializing sensors...")
time.sleep(2.3)
text_value.text = "  60"
arc_measure(60, 0, 101, 101, 100)
try:
    ssid = os.getenv('CIRCUITPY_WIFI_SSID')
    pw = os.getenv('CIRCUITPY_WIFI_PASSWORD')
except:
    print("Could not find WiFi info. Check your settings.toml file!")
    wifi_connect = False
    tile_grid.hidden = True
else:
    connect_wifi(False)

text_value.text = "  80"
arc_measure(80, 0, 101, 101, 100)

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
mqtt_client.on_message = message
#mqtt_client.on_subscribe = subscribe

connect_mqtt(0)

text_value.text = " 100"
arc_measure(100, 0, 101, 101, 100)

while True:
    if screen_mode != 0:
        mode_count = mode_count + 1
    if mode_count == 3:
        mode_count = 0
        show_reading()
    # Poll the message queue
    if mqtt_connect:
        
        mqtt_client.loop()
    # For centering:
    tx = pages[page]
    if len(tx) == 2:
        tx = "  " + tx
    elif len(tx) == 3:
        tx = " " + tx
    text_metric.text = tx
    u = sensors[pages[page]]["unit"]
    # for centering:
    if len(u) == 1:
        u = " " + u
    text_units.text = u
    
    y = take_reading(pages[page])
    x = str(y)
    # For centering:
    if len(x) == 1:
        x = "   " + x
    elif len(x) == 2:
        x = "  " + x
    elif len(x) == 3:
        x = " " + x
    text_value.text = x
    arc_measure(y, sensors[pages[page]]["minimum"], sensors[pages[page]]["middle"], sensors[pages[page]]["high"], sensors[pages[page]]["maxi"])
    
    #print("Reading buttons")
    for t in range(11):
        if btn1.value == False:
            print("Pressed btn1")
            show_info()
        if btn2.value == False:
            print("Pressed btn2")
            # move to next page without delay
            break
        if btn3.value == False:
            print("Pressed btn3")
            show_scan()
        if pir.value == True:
            if not pir_active:
                pir_active = True
                print("PIR active")
                do_pir()
        else:
            #print("PIR inactive")
            if pir_active:
                pir_active = False
                do_pir()
        time.sleep(0.4)
    #print("Not reading buttons")
    
    if screen_mode == 2:
        qr = code_read()
        if qr == "Empty":
            time.sleep(1)
        else:
            text_area_s1.text = "Scanned!"
            # Code reader msg: WIFI:T:WPA;S:MyNet;P:QW6HN8IKL9;H:;;
            read_scan_data(qr)
            time.sleep(0.5)
            show_scan()  # reverts mode and display
            
    page = page + 1
    if page == 10:
        page = 0
    
    if not wifi_connect:
        wifi_reconnect_count = wifi_reconnect_count + 1
        if wifi_reconnect_count == 480:  # about 2 minutes
            print("Offline, attempting wifi connection...")
            wifi_connect_count = 0
            connect_wifi(True)
    else:
        if not mqtt_connect:
            mqtt_reconnect_count = mqtt_reconnect_count + 1
            if mqtt_reconnect_count == 480:  # about 2 minutes
                print("Unconnected, attempting mqtt broker connection...")
                mqtt_reconnect_count = 0
                connect_mqtt(True)
    
