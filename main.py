import time
import machine
import network
import urequests

from env import (
    WIFI_SSID,
    WIFI_PASS,
    DEVICE_ID,
    DEVICE_TOKEN,
)


API = "https://lamp.deta.dev"


class Indicator:
    def __init__(self):
        self.pin = machine.Pin(2, machine.Pin.OUT)
        self._on = False

    def toggle(self):
        self._on = not self._on
        self.pin.value(int(self._on))

    def on(self):
        self._on = True
        self.pin.value(int(self._on))

    def off(self):
        self._on = False
        self.pin.value(int(self._on))

    def blink(self):
        self.on()
        time.sleep(0.2)
        self.off()
        time.sleep(0.2)
        self.on()
        time.sleep(0.2)
        self.off()
        time.sleep(0.2)
        self.on()


def connect():
    nic = network.WLAN(network.STA_IF)
    if not nic.isconnected():
        print("Connecting network...")
        nic.active(True)
        nic.connect(WIFI_SSID, WIFI_PASS)
        while not nic.isconnected():
            pass
    print("network config:", nic.ifconfig())


def heartbeat(led: Indicator):
    payload = {"id": DEVICE_ID}
    headers = {"Authorization": "Bearer " + DEVICE_TOKEN}
    r = urequests.post(API + "/devices/heartbeat", json=payload, headers=headers)
    r.close()
    del r
    led.blink()


def wait_and_feed(dur: int, wdt: machine.WDT, led: Indicator):
    c = 0
    while c < dur:
        wdt.feed()
        led.toggle()
        time.sleep(1)
        c += 1
    return


if __name__ == "__main__":
    led = Indicator()
    wdt = machine.WDT(timeout=1000 * 10)
    connect()
    led.on()
    while True:
        heartbeat(led)
        wait_and_feed(30, wdt, led)
