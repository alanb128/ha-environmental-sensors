# Environmental sensors
Two different sensor projects that can be used standalone or with Home Assistant

<img src="/photos/main_image.jpg">

Disclaimer: These devices are not for any safety, medical, or critical usage. It's for hobby education and experimentation only!

## Mini-sensor

This one is designed to be inexpensive and easy to build. The parts should cost around $25. It measures temperature and humidity, and can publish the sensor readings to Home Assistant.

<img src="/photos/mini-01.jpg">

### Hardware List

- [Raspberry Pi Pico 2W](https://www.raspberrypi.com/products/raspberry-pi-pico-2/) microcontroller
- The case is based on a "2 Inch 22.5 Degree PVC Elbow Pipe Fitting" [like this one](https://www.amazon.com/dp/B0DZS46D2V)
- Display (optional) [Adafruit 0.96" 160x80 Color TFT Display](https://www.adafruit.com/product/3533) - ST7735
- 12mm x 12mm momentary tactile button (optional)
- Some wire or ribbon cable, 28AWG or similar
- [3cm x 7cm proto board](https://www.adafruit.com/product/4784) (only one board needed per sensor)
- [SHT40 Temperature and Humidity Sensor](https://www.adafruit.com/product/4885) (or SHT41, SHT45)
- M2 x 12 self tapping screws (optional) - 4 pieces to secure top and bottom to case

If not using the display, you can use an LED instead:
- bi-color LED
- two 470 ohm resistors

### Assembly

3D print the top, bottom, and insulator. Then use the photos below to help assemble the unit. The file `schematic-mini.pdf` shows how to wire everything together.

<img src="/mini/images/mini-01.jpg">

<img src="/mini/images/mini-02.jpg">

<img src="/mini/images/mini-03.jpg">

<img src="/mini/images/mini-04.jpg">

### Software

[Download and install](https://circuitpython.org/board/raspberry_pi_pico2_w/) Circuitpython for the Pico 2W. This code was developed and tested on version 9.2.7, but should work on newer versions. 

Copy all of the files in the mini folder to the root of your Pico. (This includes all of the code and icons needed to run the project) You'll be replacing the default code.py file if it already exists.  

You will need to find and download the font file `Helvetica-Bold-16.bdf` to the root of the Pico as well. (I can't host it here due to its proprietary nature.)

Edit the `settings.toml` file with your WiFi SSID and password.

Add the following libraries to the Lib folder on the device: (You can find them in [the bundles](https://circuitpython.org/libraries) for version 9.x)

- adafruit_bitmap_font
- adafruit_minimqtt
- adafruit_display_text
- adafuit_ticks
- adafruit_st7735r
- adafruit_sht4x
- adafruit_connection_manager

### Operation

Provide 5v 1A or greater to the Pico's mico usb port to power the device and start the code automatically. Update the settings file to publish via MQTT.

## Maxi

This one has up to ten sensors and is a more advanced project. The full code and some build suggestions are in this repo, but you'll need to improside a little bit for best results.

<img src="/photos/maxi-main.jpg">

### Hardware List

- [Raspberry Pi Pico 2W](https://www.raspberrypi.com/products/raspberry-pi-pico-2/) microcontroller
- The case is based on a "2 Inch 22.5 Degree PVC Elbow Pipe Fitting" [like this one](https://www.amazon.com/dp/B0DZS46D2V)
- Display [Adafruit 1.28" 240x240 Round TFT LCD]([https://www.adafruit.com/product/3533](https://www.adafruit.com/product/6178))
- 12mm x 12mm momentary tactile buttons (three)
- Some wire or ribbon cable, 28AWG or similar
- [Swirly Aluminum Grids]([https://www.adafruit.com/product/4784](https://www.adafruit.com/product/5774)) (mix and match, cut to size if needed)
- [Basic PIR Sensor]([https://www.adafruit.com/product/4885](https://www.adafruit.com/product/4667)) (or SHT41, SHT45)
- [Adafruit EYESPI breakout board](https://www.adafruit.com/product/5613) For connecting display ribbon cable to the Pico
- [MAX 4466 electret microphone](https://www.adafruit.com/product/1063)
- [Tiny Code Reader from Useful Sensors](https://www.adafruit.com/product/5744)
- [Adafruit MiCS5524 gas sensor](https://www.adafruit.com/product/3199)
- [DPS 310 Pressure sensor](https://www.adafruit.com/product/4494)
- [Accelerometer](https://www.adafruit.com/product/2809)
- [VEML7700 Lux Sensor](https://www.adafruit.com/product/4162)
- [SCD 40](CO2 sensor)
- [Adafruit PMSA003I Air Quality Breakout](https://www.adafruit.com/product/4632)
- Qwiic/STEMMAQT connectors/cables to connect the sensors together
- M2.5 spacers, standoffs and hardware for mounting sensors
- "Reducing" pipe fitting, [like this one](https://www.homedepot.com/p/Charlotte-Pipe-3-in-x-3-in-x-2-in-DWV-PVC-Wye-Reducing-PVC006011400HD/203396277) for the case
- [3cm x 7cm proto board](https://www.adafruit.com/product/4784) - cut as needed
- 5V, 4A power supply

Optional:
- blue LED and resistor
- acrylic security camera dome

### Assembly

3D print the control panel, bottom bracket, and clips. Then use the photos below to help assemble the unit. The file `schematic-maxi.pdf` shows how to wire everything together.

<img src="/maxi/images/maxi-01.jpg">

<img src="/maxi/images/maxi-02.jpg">

<img src="/maxi/images/maxi-03.jpg">

### Software

[Download and install](https://circuitpython.org/board/raspberry_pi_pico2_w/) Circuitpython for the Pico 2W. This code was developed and tested on version 9.2.7, but should work on newer versions. 

Copy all of the files in the maxi folder to the root of your Pico. (This includes all of the code and icons needed to run the project) You'll be replacing the default code.py file if it already exists.  

You will need to find and download the font file `Helvetica-Bold-16.bdf` to the root of the Pico as well. (I can't host it here due to its proprietary nature.)

Edit the `settings.toml` file with your WiFi SSID and password.

Add the following libraries to the Lib folder on the device: (You can find them in [the bundles](https://circuitpython.org/libraries) for version 9.x)

- adafruit_bitmap_font
- adafruit_bus_device
- adafruit_display_shapes
- adafruit_minimqtt
- adafruit_display_text
- adafruit_imageload
- adafruit_dps310
- adafruit_pm25
- adafruit_register
- adafuit_ticks
- adafruit_gc9a01a
- adafruit_lis3dh
- adafruit_scd4x
- adafruit_veml7700
- adafruit_connection_manager

### Operation

Provide 5v 4A or greater to the Pico's mico usb port to power the device and start the code automatically. Update the settings file to publish via MQTT.

## Connecting to Home Assistant

You will need an MQTT broker running on your network. [Mosquitto](https://mosquitto.org/) is a good choice!

Then, [add the sensors](https://www.home-assistant.io/integrations/sensor.mqtt/) and binary sensors to your configuration.yaml file in Home Assistant. 

For an example of the House Map dashboard configuration, see the `house-map.txt` file in this repo. Note that is uses an image uploaded to the Home Assistant media folder.
