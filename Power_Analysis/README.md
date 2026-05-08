### Step 1:
You need the Chipwhisperer repository to use the device.
Visit https://chipwhisperer.readthedocs.io/en/latest/linux-install.html if any issue arises.
sudo apt update && sudo apt upgrade
sudo apt update && sudo apt upgrade
sudo apt install make git avr-libc gcc-avr \
gcc-arm-none-eabi libusb-1.0-0-dev usbutils python3 python3-venv python3-dev
cd ~/
git clone https://github.com/newaetech/chipwhisperer
cd chipwhisperer
python3 -m venv ~/.cwvenv
source ~/.cwvenv/bin/activate
sudo cp 50-newae.rules /etc/udev/rules.d/50-newae.rules
sudo udevadm control --reload-rules
sudo groupadd -fr chipwhisperer # new systemd versions require system accounts for udev
sudo usermod -aG chipwhisperer $USER
sudo usermod -aG plugdev $USER
git submodule update --init jupyter
python -m pip install -e .
python -m pip install -r jupyter/requirements.txt

### Step 2:
Install jupyter notebook
source ~/.cwvenv/bin/activate
cd ~/chipwhisperer
jupyter notebook
[The experiment will be in Jupyter notebook], now you the chipwhisperer folder with you.

### Step 3:
i>  Copy the simpleserial-present folder in /chipwhisperer/firmware/mcu/ 
ii> Put the present_power_anlysis_final.ipynb inside /chipwhisperer/jupyter/courses/fault101/ 

### Setup:
1 #connect the Chipwhisperer and the target board
  i> connect measure pin to the target boards vout pin
  <p align="center"> <img src="images/setup.jpeg" width="700"> </p> <p align="center"
2 #Open terminal
  i>  activate the env (source ~/.cwvenv/bin/activate)
  ii> cd ~/chipwhisperer/firmware/mcu/simpleserial-present
  iii>make PLATFORM=CW308_STM32F3 
  this makes .hex and .bin file for the flashing the target board
  iv> cd ../../../
#Open jupythe notebook in the chipwhisperer directory
  v>  Go to the /jupyter/courses/fault101 and open present_power_anlysis_final.ipynb
  Vi> run the code
