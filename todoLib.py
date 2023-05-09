from pyrf24 import RF24, rf24

OWN_ADDRESS = b'NodeA1' #TODO Change to each address of each team TR

#Filename TODO: Change for each team
FILENAME = 'transmittedFile.txt' 

def initializeRadio():
    radio = RF24()
    if not radio.begin(4,0): #TODO: Here the 1st pin cahnegs for each team
        raise OSError("nRF24L01 hardware isn't responding")
    return radio

def readFile(fileName): #TODO Read file from usb, particular for each team
    """
    Read file from usb.
    Return the file in bytes
    """
    with open("transmittedFile.txt", 'rb') as transmittedFile:
        file_data = transmittedFile.read()
    return file_data

def saveFile(file_data): #TODO Save file in usb, particular for each team
    """
    Gets file in bytes.
    Save file in usb.
    """
    with open('transmittedFile.txt','wb') as transmittedFile:
        transmittedFile.write(file_data)