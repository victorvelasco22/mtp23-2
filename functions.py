import os
from glob import glob
from subprocess import check_output, CalledProcessError
import bz2
import struct
from pyrf24 import RF24, rf24
import shutil

EOF = b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF' 
EOF1 = (0, b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF')
EOF2 = (1, b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF')

#radio setup
#mode = False for TX or True for RX

radio = RF24(22, 0)

def radioSetupRX():
  if not radio.begin():
      raise OSError("nRF24L01 hardware isn't responding")
  radio.setPALevel(2,1)
  radio.openReadingPipe(0,12345)
  radio.channel = 50
  radio.listen = True
  radio.print_pretty_details()
  radio.setDataRate(rf24.RF24_1MBPS)
  radio.setAutoAck(True)

def radioSetupTX():
  if not radio.begin():
      raise OSError("nRF24L01 hardware isn't responding")
  radio.setPALevel(2,1)
  radio.setRetries(2,15)
  radio.openWritingPipe(12345)
  radio.channel = 50
  radio.listen = False
  radio.setPayloadSize(struct.calcsize("<B31s"))
  radio.print_pretty_details()
  radio.setDataRate(rf24.RF24_1MBPS)
  radio.setAutoAck(True)

def radioPowerOff():
  radio.power = False
  
def rx():
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
                    byte_txt = b''.join([byte_txt, fragment[i+1]])
                if expected_seq_num == 0x00:
                    expected_seq_num = 0x01
                elif expected_seq_num == 0x01:
                    expected_seq_num = 0x00
                received_packets += 1
                print(received_packets)
                #print(byte_txt)
    print(f"Transmission ok, total received packets: {received_packets}")
  except KeyboardInterrupt:
    print("powering down radio and exiting.")
    radio.power = False
  return eof, byte_txt

def upload_to_usb(filename):
  #path = str(filename,'utf-16-le').split("/")
  name = str(filename,'utf-16-le')
  print(name)
  name = name.replace("TX","RX")
  #shutil.copy("/home/rpi/textfile/output.txt", "/media/rpi/USB/output.txt")
  print(name)
  shutil.copy("/home/rpi/textfile/output.txt", "/media/rpi/USB/"+name)
  print("Uploaded successfully")

def write(byte_txt):
  decompressed_bytes = decompress(byte_txt)
  #with open("/media/rpi/USB/output.txt", mode="wb") as fichero:
  with open("/home/rpi/textfile/output.txt", mode="wb") as fichero:
      fichero.write(decompressed_bytes)
  fichero.close()

def tx(payload):
  total_packets_sent = 0
  packets_sent_ok = 0
  packets_sent_failed = 0
  seq_num = 0x00
  try:
    for i in range(len(payload)):
      message = struct.pack("<B31s",seq_num,payload[i])
      ok = False
      #Infinite retries
      while not ok:
        ok = radio.write(message)
        total_packets_sent += 1
        #print(f"Sending {total_packets_sent}...", ("ok" if ok else "failed"))
        if not ok:
          packets_sent_failed += 1
      packets_sent_ok += 1
      #Changing sequence number
      print(packets_sent_ok)
      if seq_num == 0x00:
        seq_num = 0x01
      elif seq_num == 0x01:
        seq_num = 0x00
      #print(message)
    #Sending EOF
    message = struct.pack("<B31s",seq_num,EOF)
    ok = radio.write(message)
    while not ok:
      ok = radio.write(message)
      total_packets_sent += 1
      #print(f"Sending {total_packets_sent}...", ("ok" if ok else "failed"))
    if ok:
      print("Transmission complete")
      print(f"Total packets sent: {total_packets_sent}")
      print(f"Total packets ok: {packets_sent_ok}")
      print(f"Total packets failed: {packets_sent_failed}")
    else:
      print("Transmission failed")
    #radio.power = False
    return ok
  except KeyboardInterrupt:
    print("powering down radio and exiting.")
    radio.power = False

def download_from_usb():
  for file in glob("/media/rpi/USB/*.txt"):
    continue
  shutil.copy(file, "/home/rpi/textfile/file.txt")
  filename = file.split("/")[-1]
  print(filename)
  print("Downloaded successfully")
  compressed_bytes = compress(open_txt())
  print("Compression successfully")
  return filename, compressed_bytes
  
#CHANGE FILE PATH/NAME
#read the utf-16-le file
def open_txt():
  #for file in glob("/media/rpi/USB/*.txt"):
  #  continue
  with open('/home/rpi/textfile/file.txt', "rb") as f:
        text = f.read()
  return text

#encoding of the text to utf-16-le for compression, NOT USED NOT
def encodes(text):
  return text.encode(encoding='utf-16-le', errors='strict')

#decode the text back to utf-16, NOT USED NOT
def decodes(text):
  return text.decode(encoding='utf-16-le', errors='strict')

#fragment text in a list elements of 31 bytes (the first one is the sequence number)
def frament_the_text(text):
  payload = list()
  for i in range(0,len(text), 31):
    payload.append(text[i:i+31])
  return payload

def compress(text_to_tx):
  # preset = 9 -> max compression, but slowest
  return bz2.compress(text_to_tx, compresslevel=9)

def decompress(compressed_txt):
    return bz2.decompress(compressed_txt)

#TO DO: read pins

#funcions per a detectar el path fins el directori del pendrive
def get_usb_devices():
    sdb_devices = map(os.path.realpath, glob('/sys/block/sd*'))
    usb_devices = (dev for dev in sdb_devices
        if 'usb' in dev.split('/')[5])
    return dict((os.path.basename(dev), dev) for dev in usb_devices)

def get_mount_points(devices=None):
    devices = devices or get_usb_devices()  # if devices are None: get_usb_devices
    output = check_output(['mount']).splitlines()
    output = [tmp.decode('UTF-8') for tmp in output]

    def is_usb(path):
        return any(dev in path for dev in devices)
    usb_info = (line for line in output if is_usb(line.split()[0]))
    return [(info.split()[0], info.split()[2]) for info in usb_info] #el primer valor es el Filesystem i el segon es on esta ubicat el directori del pendrive.


def read_from_pen():                #obtenció del path fins al pendrive i coversió de fitxer .txt a string, el output de la funció es "data" que es el .txt convertit a string.
    dir=get_mount_points()[0][1]    #obtenció del directori de usb (dir).
    os.chdir(dir)                   #establim el directori del usb(dir) com a directori de treball.
    for file in glob("*.txt"):      #es localitza el fitxer .txt.
        print(file)
    with open(file, 'r') as file:   #es converteix el fitxer .txt a string.
        data = file.read()
    return data


def write_on_pen(data):                         #obtenció del path fins al pendrive i escriptura en forma de .txt de la variable data que es una string en el pendrive.
    dir=get_mount_points()[0][1]                #obtenció del directori de usb (dir).
    os.chdir(dir)                               #establim el directori del usb(dir) com a directori de treball.
    with open("Output.txt", "w") as text_file:  #es converteix string(data) a fitxer .txt(Output.txt).
        text_file.write(data)


        #controlador pels leds
import RPi.GPIO as GPIO  #importem la llibreria correpsonent

GPIO.setmode(GPIO.BCM) #establim com es fara referencia als pins de la RPi

#Definim constants per a referirnos als Leds de una manera més senzilla
L1=2
L2=3
L3=27
L4=24
L5=23

#establim els pins conectats als leds com a outputs
GPIO.setup(L1, GPIO.OUT)
GPIO.setup(L2, GPIO.OUT)
GPIO.setup(L3, GPIO.OUT)
GPIO.setup(L4, GPIO.OUT)
GPIO.setup(L5, GPIO.OUT)

def led_manager(led, estat): #funció per a operar els leds, es donen com a inputs el led i l'estat del led (On/Off) per a fer el funcionament d'aquests
  if(estat):
    GPIO.output(led, GPIO.HIGH) #obrir el led

  else:
    GPIO.output(led, GPIO.LOW) #tencar el led

