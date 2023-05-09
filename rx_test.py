from functions import *
from pyrf24 import RF24

radioSetupRX()

reception = rx()

#encendre leds en funció del valor de "reception[0]"
if reception[0]:
    print("ok")
    #encendre un led
elif not reception[0]:
    print("not ok")
    #encendre un altre led

write(reception[1])
upload_to_usb()

radioPowerOff()

print(reception[1])
print("ok!")
