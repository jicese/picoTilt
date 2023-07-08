# picoTilt
Simple Raspberry Pi Pico W wifi bridge for Tilt Hydrometer

Requires a Pico W with bluetooth-enabled micropython firmware, more information at https://www.raspberrypi.com/news/new-functionality-bluetooth-for-pico-w/

To use, set the following constants to match your network:
  _WLAN_SSID = const("wlan-id")
  _WLAN_PWD = const("wlan-password")

Rename the file to main.py to autostart when the Pico is powered up.
