# Environmental sensors
Two different sensor projects that can be used standalone or with Home Assistant

## Mini-sensor

This one is designed to be inexpensive and easy to build. The parts should cost around $25. It measures temperature and humidity, and can publish the sensor readings to Home Assistant.

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

Edit the `settings.toml` file with your WiFi SSID and password.

Add the following libraries to the Lib folder on the device: (You can find them in [the bundles](https://circuitpython.org/libraries) for version 9.x)

- adafruit_bitmap_font
- adafruit_minimqtt
- adafruit_display_text
- adafuit_ticks
- adafruit_st7735r
- adafruit_sht4x
- adafruit_connection_manager

