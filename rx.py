import struct
from pyrf24 import RF24
#import bz2
from functions import  *

# MAIN
#2 EOF depending on the sequence number
EOF1 = (0, b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF')
EOF2 = (1, b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF')

radio = RF24(22, 0)

if not radio.begin():
    raise OSError("nRF24L01 hardware isn't responding")

#radio setup
#radio.setDataRate(2)-> This is to change the data rate to 250Kbps. Default is 1Mbps (1)
radio.setPALevel(2,1)
address=12345
radio.openReadingPipe(0,address)
radio.channel = 90
radio.listen = True
radio.print_pretty_details()

expected_seq_num = 0x00
eof = False
payload = []
received_packets = 0
byte_txt = bytes('', 'utf-16-le')

try:
    while not eof:
        if radio.available():
            buffer = radio.read()
            fragment = struct.unpack("<B31s",buffer)
            #print(fragment)
            if fragment == EOF1 or fragment == EOF2:
                eof = True
            elif fragment[0] == expected_seq_num:
                for i in range(len(fragment)-1):
                    #fichero.write(fragment[i])
                    byte_txt = b''.join([byte_txt, fragment[i+1]])
                #payload.append(fragment)
                if expected_seq_num == 0x00:
                    expected_seq_num = 0x01
                elif expected_seq_num == 0x01:
                    expected_seq_num = 0x00
                received_packets += 1
    print(f"Transmission ok, total received packets: {received_packets}")
    decompressed_bytes = decompress(byte_txt)
    with open("/home/rpi/output.txt", mode="wb") as fichero:
        fichero.write(decompressed_bytes)
    fichero.close()
    radio.power = False
    
except KeyboardInterrupt:
    print("powering down radio and exiting.")
    radio.power = False
