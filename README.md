# mtp23

## Raspberry configuration:
``$sudo apt install python3-rpi.gpio``\
``$python -m pip install pyrf24``\

``$sudo apt install git``\
``$git clone https://github.com/victorvelasco22/mtp23/``\

``sudo raspi-config``\ -> Interfacing options --> SPI

``sudo mkdir textfile``\ -> home/rpi

``sudo mkdir /home/rpi/.config/pcmafm``\ -> Automount 
``sudo mkdir /home/rpi/.config/pcmafm/LXDE-pi``\ -> Automount 
``sudo nano /home/rpi/.config/pcmafm/LXDE-pi/pcmafm.conf``\ -> Automount 
Dins de pcmafm.conf 
``
[volume]
mount_on_startup=0
mount_removable=0
``\
``sudo umount /media/rpi/USB``\
``sudo mkdir /media/rpi/USB``\

Crontab
``sudo crontab -e``\ -> Al final de text afegir: @reboot sudo python /home/rpi/main.py > /home/rpi/log.txt 



``$touch output.txt``\
``$nano helloworld.txt`` -> and write the text to be sent

## Execution
``$python mtp23/rx.py`` -> Receiver \
``$python mtp23/tx.py`` -> Transmitter
