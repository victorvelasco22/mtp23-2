from functions import *
from pyrf24 import RF24

radioSetupTX()

download_from_usb()

payload = frament_the_text(compress(open_txt()))

ok = tx(payload)

#encendre leds en funció del valor de "ok"
#if ok:
#    continue
    #encendre un led
#elif not ok:
#    continue
    #encendre un altre led

radioPowerOff()
#radio.power = False

print("ok!")
