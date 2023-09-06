import network
import socket
import bluetooth
import random
import struct
import time
import micropython

from micropython import const
from binascii import hexlify

_WLAN_SSID = const("wlan-id")
_WLAN_PWD = const("wlan-password")

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)
_IRQ_GATTS_READ_REQUEST = const(4)
_IRQ_SCAN_RESULT = const(5)
_IRQ_SCAN_DONE = const(6)
_IRQ_PERIPHERAL_CONNECT = const(7)
_IRQ_PERIPHERAL_DISCONNECT = const(8)
_IRQ_GATTC_SERVICE_RESULT = const(9)
_IRQ_GATTC_SERVICE_DONE = const(10)
_IRQ_GATTC_CHARACTERISTIC_RESULT = const(11)
_IRQ_GATTC_CHARACTERISTIC_DONE = const(12)
_IRQ_GATTC_DESCRIPTOR_RESULT = const(13)
_IRQ_GATTC_DESCRIPTOR_DONE = const(14)
_IRQ_GATTC_READ_RESULT = const(15)
_IRQ_GATTC_READ_DONE = const(16)
_IRQ_GATTC_WRITE_DONE = const(17)
_IRQ_GATTC_NOTIFY = const(18)
_IRQ_GATTC_INDICATE = const(19)

_ADV_IND = const(0x00)
_ADV_DIRECT_IND = const(0x01)
_ADV_SCAN_IND = const(0x02)
_ADV_NONCONN_IND = const(0x03)

_TILT_RED_UUID = const("a495bb10c5b14b44b5121370f02d74de")
_TILT_GREEN_UUID = const("a495bb20c5b14b44b5121370f02d74de")
_TILT_BLACK_UUID = const("a495bb30c5b14b44b5121370f02d74de")
_TILT_PURPLE_UUID = const("a495bb40c5b14b44b5121370f02d74de")
_TILT_ORANGE_UUID = const("a495bb50c5b14b44b5121370f02d74de")
_TILT_BLUE_UUID = const("a495bb60c5b14b44b5121370f02d74de")
_TILT_YELLOW_UUID = const("a495bb70c5b14b44b5121370f02d74de")
_TILT_PINK_UUID = const("a495bb80c5b14b44b5121370f02d74de")

class BLETiltScanner:
    def __init__(self, ble):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)

        self._reset()

    def _reset(self):
        # Cached name and address from a successful scan.
        self._name = None
        self._hd = None
        self._temp = None
        self._grav = None

        # Callbacks for completion of various operations.
        # These reset back to None after being invoked.
        self._scan_callback = None

        # Persistent callback for when new data is notified from the device.
        self._notify_callback = None

    def _irq(self, event, data):
        if event == _IRQ_SCAN_RESULT:
            addr_type, addr, adv_type, rssi, adv_data = data
            if adv_type == _ADV_NONCONN_IND:
                self._name = None
                if _TILT_RED_UUID in hexlify(adv_data):
                    self._name =  "Red"
                if _TILT_GREEN_UUID in hexlify(adv_data):
                    self._name =  "Green"
                if _TILT_BLACK_UUID in hexlify(adv_data):
                    self._name =  "Black"
                if _TILT_PURPLE_UUID in hexlify(adv_data):
                    self._name =  "Purple"
                if _TILT_ORANGE_UUID in hexlify(adv_data):
                    self._name =  "Orange"
                if _TILT_BLUE_UUID in hexlify(adv_data):
                    self._name =  "Blue"
                if _TILT_YELLOW_UUID in hexlify(adv_data):
                    self._name =  "Yellow"
                if _TILT_PINK_UUID in hexlify(adv_data):
                    self._name =  "Pink"
                if self._name != None:
                    #print("Found Tilt - ", hexlify(adv_data))
                    minor = (adv_data[27] * 256 + adv_data[28])
                    major = (adv_data[25] * 256 + adv_data[26])

                    if (minor > 5000 or minor == 1005 and major == 999 or minor == 1006 and major == 999):
                        self._hd = True
                    else:
                        self._hd = False

                    if self._hd == True:
                        self._grav = minor / 10000
                        self._temp = round(((major / 10) - 32) / 1.8, 1)

                    else:
                        self._grav = (minor) / 1000
                        self._temp = round((major - 32) / 1.8, 1)

                    self._scan_callback(self._name, self._grav, self._temp)
        elif event == _IRQ_SCAN_DONE:
            if self._scan_callback:
                self._scan_callback = None

    # Find a device
    def scan(self, callback=None):
        self._addr_type = None
        self._addr = None
        self._scan_callback = callback
        self._ble.gap_scan(2000, 30000, 30000)

    # Set handler for when data is received over the UART.
    def on_notify(self, callback):
        self._notify_callback = callback


def demo():
    ble = bluetooth.BLE()
    central = BLETiltScanner(ble)

    tilt_gravity = {"Red": None, "Green": None, "Black": None, "Purple": None, "Orange": None, "Blue": None, "Yellow": None, "Pink": None}
    tilt_temp = {"Red": None, "Green": None, "Black": None, "Purple": None, "Orange": None, "Blue": None, "Yellow": None, "Pink": None}
    updateTime = None
  
    def get_tilt_html(name):
        nonlocal tilt_gravity
        nonlocal tilt_temp
        tilt_colorcode = {"Red": "#FF0000", "Green": "#008000", "Black": "#000000", "Purple": "#800080", "Orange": "#FF8000", "Blue": "#0000FF", "Yellow": "#FFFF00", "Pink": "#FFC0CB"}
        #return """<p><table border="4" bordercolor=" """ + tilt_colorcode[name] + """ "><tr>""" + """<td>""" + name + """</td><td>""" + str(tilt_gravity[name]) + """</td><td>""" + str(tilt_temp[name]) + """&deg;C</td>""" + """</tr></table></p>"""
        return """<p>
                    <table border="0" bgcolor="#1f1f1f"  style="padding: 20px; border-spacing: 20px">
                    <tr>
                    <td bgcolor=" """ + tilt_colorcode[name] + """ " style="padding: 10px">   </td
                    ><td>""" + str(tilt_gravity[name]) + """</td>
                    <td>""" + str(tilt_temp[name]) + """&deg;C</td>
                    </tr>
                    </table>
                </p>"""
    
    def on_scan(name, grav, temp):
        if name is not None:
            nonlocal tilt_gravity
            nonlocal tilt_temp
            nonlocal updateTime

            print("Found Tilt:", name, grav, temp)
            tilt_gravity[name] = grav
            tilt_temp[name] = temp
            currentTime = time.localtime()
            updateTime = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}".format(currentTime[0], currentTime[1], currentTime[2], currentTime[3], currentTime[4])

    #initial scan
    central.scan(callback=on_scan)

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    network.hostname("picoTilt")
    wlan.connect(_WLAN_SSID, _WLAN_PWD)

    max_wait = 30
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('Waiting for connection...')
        time.sleep(2)

    if wlan.status() != 3:
        raise RuntimeError('Network connection failed')
    else:
        print('Connected')
        status = wlan.ifconfig()
        print( 'IP = ' + status[0] )

    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.settimeout(10)
    s.bind(addr)
    s.listen(1)
    print('Listening on', addr)

    while True:
        try:
            cl, addr = s.accept()
#        Should be "except socket.timeout:" - micropython sends OSError exception instead
        except:                        
            print('Caught accept exception (timeout?)')
            tilt_gravity.fromkeys(tilt_gravity, None)
            tilt_temp.fromkeys(tilt_temp, None)
            central.scan(callback=on_scan)
        else:
            print('Connect from ', addr)
            try:
                request = cl.recv(1024)
            except:
                print('Caught recv exception')

            html = """<!DOCTYPE html>
                <html>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <head> <title>picoTilt</title> </head>
                <body bgcolor="#000000" text="#ffffff"  style="font-family: Verdana, Geneva, Tahoma, sans-serif"><center>
                <h1>picoTilt</h1><h2>"""
            
            if(tilt_gravity["Red"] != None):
                html = html + get_tilt_html("Red");
            if(tilt_gravity["Green"] != None):
                html = html + get_tilt_html("Green");
            if(tilt_gravity["Black"] != None):
                html = html + get_tilt_html("Black");
            if(tilt_gravity["Purple"] != None):
                html = html + get_tilt_html("Purple");
            if(tilt_gravity["Orange"] != None):
                html = html + get_tilt_html("Orange");
            if(tilt_gravity["Blue"] != None):
                html = html + get_tilt_html("Blue");
            if(tilt_gravity["Yellow"] != None):
                html = html + get_tilt_html("Yellow");
            if(tilt_gravity["Pink"] != None):
                html = html + get_tilt_html("Pink");
            # TODO Add latest tilt update time to html
            html = html + """</h2>"""
            if updateTime != None:
                html = html + """Last Update """ + updateTime
            html = html + """</center></body></html>"""
            try:
                cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
                cl.send(html)
                cl.close()
            except:
                print('Caught send exception')

if __name__ == "__main__":
    demo()
